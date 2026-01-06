// ============================================
// ANALYTICS SERVICE - Statistics & Reports
// ============================================

import { Ticket, AnalyticsData } from '@/types';
import { isOverdue, getToday, getDaysDifference } from './utils';

/**
 * Calculate comprehensive analytics data
 */
export function calculateAnalytics(tickets: Ticket[]): AnalyticsData {
    const today = getToday();
    const weekFromNow = new Date(today);
    weekFromNow.setDate(weekFromNow.getDate() + 7);
    
    // Basic counts
    const totalTickets = tickets.length;
    const openTickets = tickets.filter(t => t.status === 'Open').length;
    const inProgressTickets = tickets.filter(t => t.status === 'In Progress').length;
    const completedTickets = tickets.filter(t => t.status === 'Completed').length;
    const onHoldTickets = tickets.filter(t => t.status === 'On Hold').length;
    const overdueTickets = tickets.filter(t => isOverdue(t)).length;
    
    // Upcoming deadlines (within 7 days)
    const upcomingDeadlines = tickets.filter(ticket => {
        if (ticket.status === 'Completed' || ticket.status === 'Cancelled') return false;
        const dueDate = new Date(ticket.completionBy);
        return dueDate >= today && dueDate <= weekFromNow;
    }).length;
    
    // By priority
    const byPriority = {
        Critical: tickets.filter(t => t.priority === 'Critical').length,
        High: tickets.filter(t => t.priority === 'High').length,
        Medium: tickets.filter(t => t.priority === 'Medium').length,
        Low: tickets.filter(t => t.priority === 'Low').length,
    };
    
    // By status
    const byStatus = {
        Open: openTickets,
        'In Progress': inProgressTickets,
        Completed: completedTickets,
        'On Hold': onHoldTickets,
        Cancelled: tickets.filter(t => t.status === 'Cancelled').length,
    };
    
    // By module
    const byModule: Record<string, number> = {};
    tickets.forEach(ticket => {
        if (ticket.module) {
            byModule[ticket.module] = (byModule[ticket.module] || 0) + 1;
        }
    });
    
    // By assignee
    const byAssignee: Record<string, number> = {};
    tickets.forEach(ticket => {
        byAssignee[ticket.assignedTo] = (byAssignee[ticket.assignedTo] || 0) + 1;
    });
    
    return {
        totalTickets,
        openTickets,
        inProgressTickets,
        completedTickets,
        onHoldTickets,
        overdueTickets,
        upcomingDeadlines,
        byPriority,
        byStatus,
        byModule,
        byAssignee,
    };
}

/**
 * Get overdue tickets with details
 */
export function getOverdueTicketDetails(tickets: Ticket[]): (Ticket & { daysOverdue: number })[] {
    return tickets
        .filter(t => isOverdue(t))
        .map(ticket => ({
            ...ticket,
            daysOverdue: Math.abs(getDaysDifference(ticket.completionBy)),
        }))
        .sort((a, b) => b.daysOverdue - a.daysOverdue);
}

/**
 * Get upcoming deadline tickets with details
 */
export function getUpcomingDeadlineDetails(
    tickets: Ticket[],
    days: number = 7
): (Ticket & { daysUntilDue: number })[] {
    const today = getToday();
    const futureDate = new Date(today);
    futureDate.setDate(futureDate.getDate() + days);
    
    return tickets
        .filter(ticket => {
            if (ticket.status === 'Completed' || ticket.status === 'Cancelled') return false;
            const dueDate = new Date(ticket.completionBy);
            return dueDate >= today && dueDate <= futureDate;
        })
        .map(ticket => ({
            ...ticket,
            daysUntilDue: getDaysDifference(ticket.completionBy),
        }))
        .sort((a, b) => a.daysUntilDue - b.daysUntilDue);
}

/**
 * Get date range report data
 */
export function getDateRangeReport(
    tickets: Ticket[],
    startDate: string,
    endDate: string
): {
    ticketsCreated: Ticket[];
    ticketsClosed: Ticket[];
    totalCreated: number;
    totalClosed: number;
} {
    const start = new Date(startDate);
    const end = new Date(endDate);
    end.setHours(23, 59, 59, 999);
    
    const ticketsCreated = tickets.filter(ticket => {
        const createdDate = new Date(ticket.createdOn);
        return createdDate >= start && createdDate <= end;
    });
    
    const ticketsClosed = tickets.filter(ticket => {
        if (ticket.status !== 'Completed') return false;
        // Use closedOn for completion date
        const closedDate = ticket.closedOn ? new Date(ticket.closedOn) : null;
        if (!closedDate) return false;
        return closedDate >= start && closedDate <= end;
    });
    
    return {
        ticketsCreated,
        ticketsClosed,
        totalCreated: ticketsCreated.length,
        totalClosed: ticketsClosed.length,
    };
}

/**
 * Get assignee workload report
 */
export function getAssigneeWorkloadReport(tickets: Ticket[]): {
    assignee: string;
    total: number;
    open: number;
    inProgress: number;
    completed: number;
    onHold: number;
    overdue: number;
    completionRate: number;
}[] {
    const workloadMap: Record<string, {
        total: number;
        open: number;
        inProgress: number;
        completed: number;
        onHold: number;
        overdue: number;
    }> = {};
    
    tickets.forEach(ticket => {
        const assignee = ticket.assignedTo;
        if (!workloadMap[assignee]) {
            workloadMap[assignee] = {
                total: 0,
                open: 0,
                inProgress: 0,
                completed: 0,
                onHold: 0,
                overdue: 0,
            };
        }
        
        workloadMap[assignee].total++;
        
        switch (ticket.status) {
            case 'Open':
                workloadMap[assignee].open++;
                break;
            case 'In Progress':
                workloadMap[assignee].inProgress++;
                break;
            case 'Completed':
                workloadMap[assignee].completed++;
                break;
            case 'On Hold':
                workloadMap[assignee].onHold++;
                break;
        }
        
        if (isOverdue(ticket)) {
            workloadMap[assignee].overdue++;
        }
    });
    
    return Object.entries(workloadMap)
        .map(([assignee, data]) => ({
            assignee,
            ...data,
            completionRate: data.total > 0 
                ? Number(((data.completed / data.total) * 100).toFixed(1))
                : 0,
        }))
        .sort((a, b) => b.total - a.total);
}

/**
 * Get priority distribution
 */
export function getPriorityDistribution(tickets: Ticket[]): {
    priority: string;
    count: number;
    percentage: number;
}[] {
    const total = tickets.length;
    const priorities = ['Critical', 'High', 'Medium', 'Low'];
    
    return priorities.map(priority => {
        const count = tickets.filter(t => t.priority === priority).length;
        return {
            priority,
            count,
            percentage: total > 0 ? Number(((count / total) * 100).toFixed(1)) : 0,
        };
    });
}

/**
 * Get module distribution
 */
export function getModuleDistribution(tickets: Ticket[]): {
    module: string;
    count: number;
    percentage: number;
}[] {
    const total = tickets.length;
    const moduleCount: Record<string, number> = {};
    
    tickets.forEach(ticket => {
        const ticketModule = ticket.module || 'Other';
        moduleCount[ticketModule] = (moduleCount[ticketModule] || 0) + 1;
    });
    
    return Object.entries(moduleCount)
        .map(([module, count]) => ({
            module,
            count,
            percentage: total > 0 ? Number(((count / total) * 100).toFixed(1)) : 0,
        }))
        .sort((a, b) => b.count - a.count);
}

/**
 * Get ticket trend data (tickets created per day/week/month)
 */
export function getTicketTrend(
    tickets: Ticket[],
    days: number = 30
): { date: string; created: number; closed: number }[] {
    const trend: Record<string, { created: number; closed: number }> = {};
    const today = getToday();
    
    // Initialize all dates
    for (let i = days - 1; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        const dateStr = date.toISOString().split('T')[0];
        trend[dateStr] = { created: 0, closed: 0 };
    }
    
    // Count tickets
    tickets.forEach(ticket => {
        const createdDate = ticket.createdOn;
        if (trend[createdDate]) {
            trend[createdDate].created++;
        }
        
        if (ticket.status === 'Completed' && ticket.closedOn) {
            if (trend[ticket.closedOn]) {
                trend[ticket.closedOn].closed++;
            }
        }
    });
    
    return Object.entries(trend)
        .map(([date, data]) => ({ date, ...data }))
        .sort((a, b) => a.date.localeCompare(b.date));
}

/**
 * Get status summary for dashboard cards
 */
export function getStatusSummary(tickets: Ticket[]): {
    status: string;
    count: number;
    color: string;
    icon: string;
}[] {
    const statusConfig = [
        { status: 'Open', color: '#4A90D9', icon: 'folder-open' },
        { status: 'In Progress', color: '#FFB347', icon: 'refresh' },
        { status: 'Completed', color: '#5CB85C', icon: 'check-circle' },
        { status: 'On Hold', color: '#9E9E9E', icon: 'pause-circle' },
        { status: 'Overdue', color: '#FF6B6B', icon: 'alert-circle' },
    ];
    
    return statusConfig.map(({ status, color, icon }) => {
        const count = status === 'Overdue'
            ? tickets.filter(t => isOverdue(t)).length
            : tickets.filter(t => t.status === status).length;
        return { status, count, color, icon };
    });
}
