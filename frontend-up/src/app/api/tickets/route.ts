// ============================================
// TICKETS API - GET ALL & CREATE
// ============================================

import { NextRequest, NextResponse } from 'next/server';
import { initialTickets } from '@/data/tickets';
import { Ticket } from '@/types';

// In-memory store (will be replaced with database)
let tickets: Ticket[] = [...initialTickets];

// GET /api/tickets - Get all tickets with optional filtering
export async function GET(request: NextRequest) {
    try {
        const { searchParams } = new URL(request.url);
        
        let result = [...tickets];
        
        // Filter by status
        const status = searchParams.get('status');
        if (status) {
            result = result.filter(t => t.status === status);
        }
        
        // Filter by priority
        const priority = searchParams.get('priority');
        if (priority) {
            result = result.filter(t => t.priority === priority);
        }
        
        // Filter by assignee
        const assignee = searchParams.get('assignee');
        if (assignee) {
            result = result.filter(t => 
                t.assignedTo.toLowerCase().includes(assignee.toLowerCase())
            );
        }
        
        // Filter by module
        const moduleParam = searchParams.get('module');
        if (moduleParam) {
            result = result.filter(t => t.module === moduleParam);
        }
        
        // Search query
        const search = searchParams.get('search');
        if (search) {
            const lowerSearch = search.toLowerCase();
            result = result.filter(t =>
                t.title.toLowerCase().includes(lowerSearch) ||
                t.description.toLowerCase().includes(lowerSearch) ||
                t.id.toString().includes(search)
            );
        }
        
        // Sort
        const sortBy = searchParams.get('sortBy') || 'id';
        const sortOrder = searchParams.get('sortOrder') || 'desc';
        
        result.sort((a, b) => {
            const aVal = a[sortBy as keyof Ticket];
            const bVal = b[sortBy as keyof Ticket];
            
            if (typeof aVal === 'string' && typeof bVal === 'string') {
                return sortOrder === 'asc' 
                    ? aVal.localeCompare(bVal)
                    : bVal.localeCompare(aVal);
            }
            
            if (sortOrder === 'asc') {
                return (aVal as number) - (bVal as number);
            }
            return (bVal as number) - (aVal as number);
        });
        
        return NextResponse.json({
            success: true,
            data: result,
            total: result.length,
        });
    } catch (error) {
        console.error('Error fetching tickets:', error);
        return NextResponse.json(
            { success: false, error: 'Failed to fetch tickets' },
            { status: 500 }
        );
    }
}

// POST /api/tickets - Create new ticket
export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        
        // Validate required fields
        const requiredFields = ['title', 'assignedTo', 'completionBy'];
        for (const field of requiredFields) {
            if (!body[field]) {
                return NextResponse.json(
                    { success: false, error: `Missing required field: ${field}` },
                    { status: 400 }
                );
            }
        }
        
        // Generate new ID
        const newId = Math.max(...tickets.map(t => t.id)) + 1;
        
        const newTicket: Ticket = {
            id: newId,
            title: body.title,
            description: body.description || '',
            status: body.status || 'Open',
            priority: body.priority || 'Medium',
            assignedTo: body.assignedTo,
            raisedBy: body.raisedBy || body.createdBy || 'System',
            createdOn: new Date().toISOString().split('T')[0],
            completionBy: body.completionBy,
            closedOn: null,
            module: body.module,
            tags: body.tags || [],
            attachments: [],
            comments: [],
            logs: [{
                id: 1,
                action: 'ticket_created',
                performedBy: body.createdBy || 'System',
                timestamp: new Date().toISOString(),
                details: 'Ticket was created',
            }],
        };
        
        tickets = [...tickets, newTicket];
        
        return NextResponse.json({
            success: true,
            data: newTicket,
        }, { status: 201 });
    } catch (error) {
        console.error('Error creating ticket:', error);
        return NextResponse.json(
            { success: false, error: 'Failed to create ticket' },
            { status: 500 }
        );
    }
}
