// ============================================
// DASHBOARD HOME PAGE
// ============================================

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Ticket } from '@/types';
import { useTickets } from '@/hooks/useTickets';
import { useAnalytics } from '@/hooks/useAnalytics';
import { StatsCard, Card, CardHeader, CardTitle, CardContent, StatusBadge, PriorityBadge } from '@/components/ui';
import { formatDate, getDaysLabel } from '@/lib/utils';

export default function DashboardPage() {
    const { tickets, isLoading } = useTickets();
    const { 
        analytics, 
        overdueTickets, 
        upcomingTickets,
        statusSummary 
    } = useAnalytics({ tickets });
    
    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="spinner"></div>
            </div>
        );
    }
    
    return (
        <div className="space-y-6">
            {/* Page Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
                    <p className="text-gray-500 mt-1">
                        Overview of your Ticket Management System
                    </p>
                </div>
                <Link
                    href="/tickets/new"
                    className="inline-flex items-center gap-2 px-4 py-2 bg-[#D04A02] text-white rounded-lg hover:bg-[#b84102] transition-colors"
                >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    New Ticket
                </Link>
            </div>
            
            {/* Stats Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatsCard
                    title="Total Tickets"
                    value={analytics.totalTickets}
                    color="primary"
                    icon={
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                        </svg>
                    }
                />
                <StatsCard
                    title="Open"
                    value={analytics.openTickets}
                    color="info"
                    icon={
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                        </svg>
                    }
                />
                <StatsCard
                    title="In Progress"
                    value={analytics.inProgressTickets}
                    color="warning"
                    icon={
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                    }
                />
                <StatsCard
                    title="Overdue"
                    value={analytics.overdueTickets}
                    color="danger"
                    icon={
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    }
                />
            </div>
            
            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Overdue Tickets */}
                <Card>
                    <CardHeader>
                        <div className="flex items-center justify-between">
                            <CardTitle>
                                <span className="flex items-center gap-2">
                                    <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                                    Overdue Tickets
                                </span>
                            </CardTitle>
                            <span className="text-sm text-gray-500">
                                {overdueTickets.length} tickets
                            </span>
                        </div>
                    </CardHeader>
                    <CardContent>
                        {overdueTickets.length === 0 ? (
                            <p className="text-gray-500 text-center py-8">
                                No overdue tickets! 🎉
                            </p>
                        ) : (
                            <div className="space-y-3 max-h-80 overflow-y-auto">
                                {overdueTickets.slice(0, 5).map((ticket) => (
                                    <TicketItem key={ticket.id} ticket={ticket} showOverdue />
                                ))}
                                {overdueTickets.length > 5 && (
                                    <Link
                                        href="/tickets?filter=overdue"
                                        className="block text-center text-sm text-[#D04A02] hover:underline py-2"
                                    >
                                        View all {overdueTickets.length} overdue tickets →
                                    </Link>
                                )}
                            </div>
                        )}
                    </CardContent>
                </Card>
                
                {/* Upcoming Deadlines */}
                <Card>
                    <CardHeader>
                        <div className="flex items-center justify-between">
                            <CardTitle>
                                <span className="flex items-center gap-2">
                                    <span className="w-2 h-2 bg-yellow-500 rounded-full"></span>
                                    Upcoming Deadlines
                                </span>
                            </CardTitle>
                            <span className="text-sm text-gray-500">
                                Next 7 days
                            </span>
                        </div>
                    </CardHeader>
                    <CardContent>
                        {upcomingTickets.length === 0 ? (
                            <p className="text-gray-500 text-center py-8">
                                No upcoming deadlines in the next 7 days
                            </p>
                        ) : (
                            <div className="space-y-3 max-h-80 overflow-y-auto">
                                {upcomingTickets.slice(0, 5).map((ticket) => (
                                    <TicketItem key={ticket.id} ticket={ticket} showDueDate />
                                ))}
                                {upcomingTickets.length > 5 && (
                                    <Link
                                        href="/tickets?filter=upcoming"
                                        className="block text-center text-sm text-[#D04A02] hover:underline py-2"
                                    >
                                        View all {upcomingTickets.length} upcoming tickets →
                                    </Link>
                                )}
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
            
            {/* Status Distribution */}
            <Card>
                <CardHeader>
                    <CardTitle>Ticket Distribution by Status</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
                        {statusSummary.map(({ status, count, color }) => (
                            <Link
                                key={status}
                                href={`/tickets?status=${status.toLowerCase().replace(' ', '-')}`}
                                className="p-4 rounded-lg border border-gray-200 hover:border-gray-300 hover:shadow-sm transition-all text-center"
                            >
                                <div 
                                    className="w-3 h-3 rounded-full mx-auto mb-2"
                                    style={{ backgroundColor: color }}
                                ></div>
                                <p className="text-2xl font-bold text-gray-900">{count}</p>
                                <p className="text-sm text-gray-500">{status}</p>
                            </Link>
                        ))}
                    </div>
                </CardContent>
            </Card>
            
            {/* Recent Tickets */}
            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <CardTitle>Recent Tickets</CardTitle>
                        <Link
                            href="/tickets"
                            className="text-sm text-[#D04A02] hover:underline"
                        >
                            View all →
                        </Link>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="space-y-3">
                        {tickets.slice(0, 5).map((ticket) => (
                            <TicketItem key={ticket.id} ticket={ticket} showStatus showPriority />
                        ))}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}

// Ticket Item Component
interface TicketItemProps {
    ticket: Ticket & { daysOverdue?: number; daysUntilDue?: number };
    showOverdue?: boolean;
    showDueDate?: boolean;
    showStatus?: boolean;
    showPriority?: boolean;
}

function TicketItem({ ticket, showOverdue, showDueDate, showStatus, showPriority }: TicketItemProps) {
    const daysInfo = getDaysLabel(ticket.completionBy);
    
    return (
        <Link
            href={`/tickets/${ticket.id}`}
            className="flex items-center justify-between p-3 rounded-lg border border-gray-200 hover:border-[#D04A02] hover:bg-gray-50 transition-all"
        >
            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-400 font-mono">#{ticket.id}</span>
                    {ticket.module && (
                        <span className="px-1.5 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">
                            {ticket.module}
                        </span>
                    )}
                </div>
                <p className="font-medium text-gray-900 truncate mt-1">
                    {ticket.title}
                </p>
                <p className="text-sm text-gray-500 mt-0.5">
                    Assigned to {ticket.assignedTo}
                </p>
            </div>
            
            <div className="flex items-center gap-3 ml-4">
                {showOverdue && ticket.daysOverdue !== undefined && (
                    <span className="text-sm text-red-600 font-medium whitespace-nowrap">
                        {ticket.daysOverdue} days overdue
                    </span>
                )}
                
                {showDueDate && (
                    <span className={`text-sm font-medium whitespace-nowrap ${
                        daysInfo.type === 'today' ? 'text-yellow-600' : 'text-gray-600'
                    }`}>
                        {daysInfo.text}
                    </span>
                )}
                
                {showStatus && <StatusBadge status={ticket.status} size="sm" />}
                {showPriority && <PriorityBadge priority={ticket.priority} size="sm" />}
            </div>
        </Link>
    );
}
