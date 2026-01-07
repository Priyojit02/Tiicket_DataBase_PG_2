// ============================================
// TICKET SERVICE - Backend API Integration
// ============================================
// Connects to FastAPI backend for real data

import { Ticket, TicketFilters, SortConfig, ApiResponse, CreateTicketPayload, UpdateTicketPayload } from '@/types';
import { ticketsApi } from './backend-api';
import { filterTickets, sortTickets, isOverdue, getToday } from './utils';
import { transformTicket, transformTicketList, toBackendCreateTicket, toBackendUpdateTicket } from './data-transform';

// For development fallback - import mock data
import { initialTickets } from '@/data/tickets';

// Data source configuration
// Now controlled by .env USE_DB variable
// Options: 'llm' (only tickets2.ts), 'normal' (only tickets.ts), 'combined' (both)
// Controlled by frontend-up/.env.local USE_DB variable

// Function to safely load LLM-parsed tickets
async function loadLLMTickets(): Promise<Ticket[]> {
    try {
        // Use dynamic import for Next.js compatibility
        const tickets2Module = await import('@/data/tickets2');
        return tickets2Module.ticketsData || [];
    } catch (error) {
        // tickets2.ts not available, return empty array
        console.log('ℹ️ tickets2.ts not found or failed to load, using only initial tickets');
        return [];
    }
}

// Get current data source mode from .env
export function getCurrentDataSource(): 'normal' | 'llm' | 'combined' {
    return (process.env.NEXT_PUBLIC_DATA_SOURCE as 'normal' | 'llm' | 'combined') || 'combined';
}

// Load tickets based on .env configuration
async function loadTickets(): Promise<Ticket[]> {
    const llmTickets = await loadLLMTickets();
    const hasLLMTickets = llmTickets.length > 0;
    
    // Get data source mode from .env
    const dataSourceMode = process.env.NEXT_PUBLIC_DATA_SOURCE || 'combined';
    
    switch (dataSourceMode) {
        case 'normal':
            console.log('📊 Using NORMAL data mode (tickets.ts only)');
            return [...initialTickets];

        case 'llm':
            console.log('🤖 Using LLM data mode (tickets2.ts only)');
            if (hasLLMTickets) {
                return [...llmTickets];
            } else {
                console.log('⚠️ No LLM tickets found, falling back to normal data');
                return [...initialTickets];
            }

        case 'combined':
        default:
            console.log('🔄 Using COMBINED data mode (tickets.ts + tickets2.ts)');
            return [...initialTickets, ...llmTickets];
    }
}

// Load LLM tickets safely
let llmParsedTickets: Ticket[] = [];

// Flag to use mock data (set to false to use real backend)
const USE_MOCK_DATA = process.env.NEXT_PUBLIC_USE_MOCK_DATA === 'true';

// Load tickets based on data source configuration
let mockTickets: Ticket[] = [];

// Initialize tickets data
async function initializeTickets() {
    llmParsedTickets = await loadLLMTickets();
    mockTickets = await loadTickets();
}

// Initialize on module load
initializeTickets().catch(console.error);

/**
 * Get all tickets from backend
 */
export async function getAllTickets(): Promise<ApiResponse<Ticket[]>> {
    if (USE_MOCK_DATA) {
        return { success: true, data: mockTickets };
    }
    
    try {
        const response = await ticketsApi.getTickets({ limit: 100 });
        const transformed = transformTicketList(response as any);
        return { success: true, data: transformed.items };
    } catch (error: unknown) {
        console.error('Failed to fetch tickets:', error);
        // Fallback to mock data on error
        return { success: true, data: mockTickets };
    }
}

/**
 * Get ticket by ID from backend
 */
export async function getTicketById(id: number | string): Promise<ApiResponse<Ticket>> {
    if (USE_MOCK_DATA) {
        const ticket = mockTickets.find((t: Ticket) => t.id === Number(id));
        return ticket 
            ? { success: true, data: ticket }
            : { success: false, error: 'Ticket not found' };
    }
    
    try {
        const ticket = await ticketsApi.getTicket(Number(id));
        const transformed = transformTicket(ticket as any);
        return { success: true, data: transformed };
    } catch (error: unknown) {
        console.error('Failed to fetch ticket:', error);
        // Fallback to mock data
        const ticket = mockTickets.find((t: Ticket) => t.id === Number(id));
        return ticket 
            ? { success: true, data: ticket }
            : { success: false, error: 'Ticket not found' };
    }
}

/**
 * Get tickets with filtering and sorting
 */
export async function getFilteredTickets(
    filters: TicketFilters,
    sort?: SortConfig
): Promise<ApiResponse<Ticket[]>> {
    if (USE_MOCK_DATA) {
        let result = filterTickets(mockTickets, filters);
        if (sort) {
            result = sortTickets(result, sort);
        }
        return { success: true, data: result };
    }
    
    try {
        const response = await ticketsApi.getTickets({
            status: filters.status,
            priority: filters.priority,
            search: filters.search || filters.title,
            order_by: sort?.column || sort?.key || 'created_at',
            order_desc: sort?.direction === 'desc',
            limit: 100,
        });
        const transformed = transformTicketList(response as any);
        return { success: true, data: transformed.items };
    } catch (error: unknown) {
        console.error('Failed to fetch filtered tickets:', error);
        let result = filterTickets(mockTickets, filters);
        if (sort) {
            result = sortTickets(result, sort);
        }
        return { success: true, data: result };
    }
}

/**
 * Get tickets by assignee
 */
export async function getTicketsByAssignee(assignee: string): Promise<ApiResponse<Ticket[]>> {
    if (USE_MOCK_DATA) {
        const userTickets = mockTickets.filter(
            (t: Ticket) => t.assignedTo.toLowerCase() === assignee.toLowerCase()
        );
        return { success: true, data: userTickets };
    }
    
    try {
        // Backend uses user IDs, so we search by name
        const response = await ticketsApi.getTickets({ search: assignee, limit: 100 });
        return { success: true, data: response.items as unknown as Ticket[] };
    } catch (error: unknown) {
        const userTickets = mockTickets.filter(
            (t: Ticket) => t.assignedTo.toLowerCase() === assignee.toLowerCase()
        );
        return { success: true, data: userTickets };
    }
}

/**
 * Get tickets by status
 */
export async function getTicketsByStatus(status: string): Promise<ApiResponse<Ticket[]>> {
    if (USE_MOCK_DATA) {
        return { success: true, data: mockTickets.filter((t: Ticket) => t.status === status) };
    }
    
    try {
        const response = await ticketsApi.getTickets({ status, limit: 100 });
        return { success: true, data: response.items as unknown as Ticket[] };
    } catch (error: unknown) {
        return { success: true, data: mockTickets.filter((t: Ticket) => t.status === status) };
    }
}

/**
 * Get overdue tickets
 */
export async function getOverdueTickets(): Promise<ApiResponse<Ticket[]>> {
    // For now, filter locally (backend could add overdue filter)
    const allTickets = await getAllTickets();
    if (allTickets.success && allTickets.data) {
        const overdueTickets = allTickets.data.filter((t: Ticket) => isOverdue(t));
        return { success: true, data: overdueTickets };
    }
    return { success: true, data: [] };
}

/**
 * Get tickets due soon (within N days)
 */
export async function getTicketsDueSoon(days: number = 7): Promise<ApiResponse<Ticket[]>> {
    return new Promise((resolve) => {
        setTimeout(() => {
            const today = getToday();
            const futureDate = new Date(today);
            futureDate.setDate(futureDate.getDate() + days);
            
            const dueSoonTickets = mockTickets.filter((ticket: Ticket) => {
                if (ticket.status === 'Completed' || ticket.status === 'Cancelled') return false;
                const dueDate = new Date(ticket.completionBy);
                return dueDate >= today && dueDate <= futureDate && !isOverdue(ticket);
            });
            
            resolve({ success: true, data: dueSoonTickets });
        }, 100);
    });
}

/**
 * Create a new ticket
 */
export async function createTicket(payload: CreateTicketPayload): Promise<ApiResponse<Ticket>> {
    if (!USE_MOCK_DATA) {
        try {
            const response = await ticketsApi.createTicket({
                title: payload.title,
                description: payload.description || '',
                status: payload.status || 'Open',
                priority: payload.priority || 'Medium',
                assignee_id: 1, // Default assignee, should be mapped from name
            });
            return { success: true, data: response as unknown as Ticket };
        } catch (error: unknown) {
            console.error('Failed to create ticket:', error);
            // Fall through to mock implementation
        }
    }
    
    return new Promise((resolve) => {
        setTimeout(() => {
            const newId = Math.max(...mockTickets.map((t: Ticket) => t.id)) + 1;
            const newTicket: Ticket = {
                id: newId,
                title: payload.title,
                description: payload.description || '',
                status: payload.status || 'Open',
                priority: payload.priority || 'Medium',
                assignedTo: payload.assignedTo,
                raisedBy: payload.raisedBy || payload.createdBy || 'System',
                createdOn: new Date().toISOString().split('T')[0],
                completionBy: payload.completionBy,
                closedOn: null,
                module: payload.module,
                tags: payload.tags || [],
                logs: [{
                    id: 1,
                    action: 'ticket_created',
                    performedBy: payload.createdBy || 'System',
                    timestamp: new Date().toISOString(),
                    details: 'Ticket was created'
                }],
                comments: [],
            };
            
            mockTickets = [...mockTickets, newTicket];
            resolve({ success: true, data: newTicket });
        }, 200);
    });
}

/**
 * Update an existing ticket
 */
export async function updateTicket(
    id: number,
    payload: UpdateTicketPayload
): Promise<ApiResponse<Ticket>> {
    if (!USE_MOCK_DATA) {
        try {
            const response = await ticketsApi.updateTicket(id, payload);
            return { success: true, data: response as unknown as Ticket };
        } catch (error: unknown) {
            console.error('Failed to update ticket:', error);
            // Fall through to mock implementation
        }
    }
    
    return new Promise((resolve) => {
        setTimeout(() => {
            const index = mockTickets.findIndex((t: Ticket) => t.id === id);
            if (index === -1) {
                resolve({ success: false, error: 'Ticket not found' });
                return;
            }
            
            const existingTicket = mockTickets[index];
            const updatedTicket: Ticket = {
                ...existingTicket,
                ...payload,
                logs: [
                    ...existingTicket.logs,
                    {
                        id: existingTicket.logs.length + 1,
                        action: 'status_changed',
                        performedBy: 'User',
                        timestamp: new Date().toISOString(),
                        details: `Fields updated: ${Object.keys(payload).join(', ')}`
                    }
                ]
            };
            
            mockTickets = [
                ...mockTickets.slice(0, index),
                updatedTicket,
                ...mockTickets.slice(index + 1)
            ];
            
            resolve({ success: true, data: updatedTicket });
        }, 200);
    });
}

/**
 * Delete a ticket
 */
export async function deleteTicket(id: number): Promise<ApiResponse<null>> {
    if (!USE_MOCK_DATA) {
        try {
            await ticketsApi.deleteTicket(id);
            return { success: true, data: null };
        } catch (error: unknown) {
            console.error('Failed to delete ticket:', error);
            // Fall through to mock implementation
        }
    }
    
    return new Promise((resolve) => {
        setTimeout(() => {
            const index = mockTickets.findIndex((t: Ticket) => t.id === id);
            if (index === -1) {
                resolve({ success: false, error: 'Ticket not found' });
                return;
            }
            
            mockTickets = [...mockTickets.slice(0, index), ...mockTickets.slice(index + 1)];
            resolve({ success: true, data: null });
        }, 200);
    });
}

/**
 * Update ticket status
 */
export async function updateTicketStatus(
    id: number,
    status: Ticket['status']
): Promise<ApiResponse<Ticket>> {
    return updateTicket(id, { status });
}

/**
 * Assign ticket to user
 */
export async function assignTicket(
    id: number,
    assignee: string
): Promise<ApiResponse<Ticket>> {
    return updateTicket(id, { assignedTo: assignee });
}

/**
 * Add comment to ticket
 */
export async function addComment(
    id: number,
    commentText: string,
    author: string
): Promise<ApiResponse<Ticket>> {
    return new Promise((resolve) => {
        setTimeout(() => {
            const index = mockTickets.findIndex((t: Ticket) => t.id === id);
            if (index === -1) {
                resolve({ success: false, error: 'Ticket not found' });
                return;
            }
            
            const ticket = mockTickets[index];
            const newComment = {
                id: ticket.comments.length + 1,
                message: commentText,
                author,
                role: 'assignee' as const,
                timestamp: new Date().toISOString(),
            };
            
            const updatedTicket: Ticket = {
                ...ticket,
                comments: [...ticket.comments, newComment],
                logs: [
                    ...ticket.logs,
                    {
                        id: ticket.logs.length + 1,
                        action: 'comment_added',
                        performedBy: author,
                        timestamp: new Date().toISOString(),
                        details: 'New comment added to ticket'
                    }
                ]
            };
            
            mockTickets = [
                ...mockTickets.slice(0, index),
                updatedTicket,
                ...mockTickets.slice(index + 1)
            ];
            
            resolve({ success: true, data: updatedTicket });
        }, 200);
    });
}

/**
 * Get ticket statistics for dashboard
 */
export async function getTicketStats(): Promise<ApiResponse<{
    total: number;
    byStatus: Record<string, number>;
    byPriority: Record<string, number>;
    byModule: Record<string, number>;
    overdue: number;
    dueSoon: number;
}>> {
    return new Promise((resolve) => {
        setTimeout(() => {
            const today = getToday();
            const weekFromNow = new Date(today);
            weekFromNow.setDate(weekFromNow.getDate() + 7);
            
            const stats = {
                total: mockTickets.length,
                byStatus: {} as Record<string, number>,
                byPriority: {} as Record<string, number>,
                byModule: {} as Record<string, number>,
                overdue: 0,
                dueSoon: 0,
            };
            
            mockTickets.forEach((ticket: Ticket) => {
                // Count by status
                stats.byStatus[ticket.status] = (stats.byStatus[ticket.status] || 0) + 1;
                
                // Count by priority
                stats.byPriority[ticket.priority] = (stats.byPriority[ticket.priority] || 0) + 1;
                
                // Count by module
                if (ticket.module) {
                    stats.byModule[ticket.module] = (stats.byModule[ticket.module] || 0) + 1;
                }
                
                // Count overdue
                if (isOverdue(ticket)) {
                    stats.overdue++;
                }
                
                // Count due soon
                const dueDate = new Date(ticket.completionBy);
                if (dueDate >= today && dueDate <= weekFromNow && 
                    ticket.status !== 'Completed' && ticket.status !== 'Cancelled') {
                    stats.dueSoon++;
                }
            });
            
            resolve({ success: true, data: stats });
        }, 100);
    });
}

/**
 * Search tickets by query
 */
export async function searchTickets(query: string): Promise<ApiResponse<Ticket[]>> {
    return new Promise((resolve) => {
        setTimeout(() => {
            const lowerQuery = query.toLowerCase();
            const results = mockTickets.filter((ticket: Ticket) => 
                ticket.title.toLowerCase().includes(lowerQuery) ||
                ticket.description.toLowerCase().includes(lowerQuery) ||
                ticket.assignedTo.toLowerCase().includes(lowerQuery) ||
                ticket.id.toString().includes(query) ||
                ticket.module?.toLowerCase().includes(lowerQuery) ||
                ticket.tags?.some((tag: string) => tag.toLowerCase().includes(lowerQuery))
            );
            resolve({ success: true, data: results });
        }, 100);
    });
}

/**
 * Get assignee workload
 */
export async function getAssigneeWorkload(): Promise<ApiResponse<Record<string, {
    total: number;
    open: number;
    inProgress: number;
    completed: number;
    overdue: number;
}>>> {
    return new Promise((resolve) => {
        setTimeout(() => {
            const workload: Record<string, {
                total: number;
                open: number;
                inProgress: number;
                completed: number;
                overdue: number;
            }> = {};
            
            mockTickets.forEach((ticket: Ticket) => {
                const assignee = ticket.assignedTo;
                if (!workload[assignee]) {
                    workload[assignee] = {
                        total: 0,
                        open: 0,
                        inProgress: 0,
                        completed: 0,
                        overdue: 0,
                    };
                }
                
                workload[assignee].total++;
                
                if (ticket.status === 'Open') workload[assignee].open++;
                if (ticket.status === 'In Progress') workload[assignee].inProgress++;
                if (ticket.status === 'Completed') workload[assignee].completed++;
                if (isOverdue(ticket)) workload[assignee].overdue++;
            });
            
            resolve({ success: true, data: workload });
        }, 100);
    });
}
