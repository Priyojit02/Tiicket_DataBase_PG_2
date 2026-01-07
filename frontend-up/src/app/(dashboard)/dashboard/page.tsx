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
import { getCurrentDataSource } from '@/lib/ticket-service';
import { emailService } from '@/lib/api-service';

export default function DashboardPage() {
    const [isSyncing, setIsSyncing] = useState(false);
    const [syncMessage, setSyncMessage] = useState<string | null>(null);
    const [isAutoSyncEnabled, setIsAutoSyncEnabled] = useState(
        process.env.NEXT_PUBLIC_AUTO_SYNC_ENABLED === 'true' // ← READ FROM ENV
    );
    const [autoSyncInterval, setAutoSyncInterval] = useState<NodeJS.Timeout | null>(null);
    const { tickets, isLoading, loadTickets } = useTickets();
    const { 
        analytics, 
        overdueTickets, 
        upcomingTickets,
        statusSummary 
    } = useAnalytics({ tickets });
    
    const currentDataSource = getCurrentDataSource();
    
    // Initial sync on page load (one time)
    useEffect(() => {
        const initialSync = async () => {
            // Small delay to let the page load first
            setTimeout(() => {
                handleSyncEmails(true);
            }, 2000);
        };
        
        initialSync();
    }, []); // Empty dependency array = runs once on mount
    
    // Auto-sync effect
    useEffect(() => {
        if (isAutoSyncEnabled) {
            // Start auto-sync every 30 seconds (reduced frequency)
            const interval = setInterval(() => {
                handleSyncEmails(true); // true indicates auto-sync
            }, 30000); // 30 seconds
            
            setAutoSyncInterval(interval);
            
            // Initial sync when auto-sync is enabled
            handleSyncEmails(true);
        } else {
            // Stop auto-sync
            if (autoSyncInterval) {
                clearInterval(autoSyncInterval);
                setAutoSyncInterval(null);
            }
        }
        
        // Cleanup on unmount
        return () => {
            if (autoSyncInterval) {
                clearInterval(autoSyncInterval);
            }
        };
    }, [isAutoSyncEnabled]);
    
    const getDataSourceInfo = () => {
        switch (currentDataSource) {
            case 'normal':
                return { label: 'Sample Data', color: 'bg-gray-100 text-gray-800', icon: '📊' };
            case 'llm':
                return { label: 'LLM Data', color: 'bg-blue-100 text-blue-800', icon: '🤖' };
            case 'combined':
            default:
                return { label: 'Combined Data', color: 'bg-green-100 text-green-800', icon: '🔄' };
        }
    };
    
    const dataSourceInfo = getDataSourceInfo();
    
    const handleSyncEmails = async (isAutoSync = false) => {
        // Skip if already syncing
        if (isSyncing) return;
        
        setIsSyncing(true);
        if (!isAutoSync) {
            setSyncMessage(null);
        }
        
        try {
            const result = await emailService.triggerEmailFetch();
            
            if (!isAutoSync) {
                setSyncMessage(`Sync completed! Processed ${result.processed_emails || 0} emails, created ${result.created_tickets || 0} tickets.`);
                // Refresh the data for manual sync
                window.location.reload();
            } else {
                // For auto-sync, refresh data without page reload
                const processed = result.processed_emails || 0;
                const created = result.created_tickets || 0;
                if (processed > 0 || created > 0) {
                    setSyncMessage(`🔄 Auto-sync: ${processed} emails processed, ${created} tickets created (${new Date().toLocaleTimeString()})`);
                    // Refresh ticket data
                    await loadTickets();
                } else {
                    setSyncMessage(`✅ Auto-sync: No new emails (${new Date().toLocaleTimeString()})`);
                }
            }
        } catch (error) {
            console.error('Sync failed:', error);
            if (!isAutoSync) {
                setSyncMessage('Sync failed. Please try again.');
            } else {
                setSyncMessage(`Auto-sync failed at ${new Date().toLocaleTimeString()}`);
            }
        } finally {
            setIsSyncing(false);
        }
    };
    
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
                <div className="flex items-center gap-4">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
                        <p className="text-gray-500 mt-1">
                            Overview of your Ticket Management System
                        </p>
                    </div>
                    <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${dataSourceInfo.color}`}>
                        <span>{dataSourceInfo.icon}</span>
                        <span>{dataSourceInfo.label}</span>
                        <Link 
                            href="/settings" 
                            className="ml-1 text-xs underline hover:no-underline"
                            title="Change data source in settings"
                        >
                            ⚙️
                        </Link>
                    </div>
                </div>
                <div className="flex gap-3">
                    {/* Auto-Sync Toggle Button */}
                    <button
                        onClick={() => setIsAutoSyncEnabled(!isAutoSyncEnabled)}
                        className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                            isAutoSyncEnabled 
                                ? 'bg-green-600 text-white hover:bg-green-700' 
                                : 'bg-gray-600 text-white hover:bg-gray-700'
                        }`}
                        title={isAutoSyncEnabled ? 'Disable auto-sync (every 10s)' : 'Enable auto-sync (every 10s)'}
                    >
                        {isAutoSyncEnabled ? (
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4" />
                            </svg>
                        ) : (
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        )}
                        {isAutoSyncEnabled ? 'Auto-Sync ON' : 'Auto-Sync OFF'}
                    </button>
                    
                    {/* Manual Sync Button */}
                    <button
                        onClick={() => handleSyncEmails(false)}
                        disabled={isSyncing}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed transition-colors"
                    >
                        {isSyncing ? (
                            <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                        ) : (
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                            </svg>
                        )}
                        {isSyncing ? 'Syncing...' : 'Sync Emails'}
                    </button>
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
            </div>
            
            {/* Sync Message */}
            {syncMessage && (
                <div className={`p-4 rounded-lg ${
                    syncMessage.includes('failed') 
                        ? 'bg-red-50 border border-red-200 text-red-800' 
                        : syncMessage.includes('Auto-sync') 
                            ? 'bg-blue-50 border border-blue-200 text-blue-800'
                            : 'bg-green-50 border border-green-200 text-green-800'
                }`}>
                    <div className="flex items-center gap-2">
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            {syncMessage.includes('failed') ? (
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                            ) : syncMessage.includes('Auto-sync') ? (
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                            ) : (
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            )}
                        </svg>
                        <span className="font-medium">{syncMessage}</span>
                        {isAutoSyncEnabled && syncMessage.includes('Auto-sync') && (
                            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
                                Auto-sync active (30s intervals)
                            </span>
                        )}
                    </div>
                </div>
            )}
            
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
