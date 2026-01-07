// ============================================
// TICKETS LIST PAGE
// ============================================

'use client';

import { useState, useCallback } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { useTickets } from '@/hooks/useTickets';
import { 
    Button, 
    Input, 
    Select, 
    StatusBadge, 
    PriorityBadge,
    Table,
    TableHeader,
    TableBody,
    TableRow,
    TableHead,
    TableCell,
    Card,
} from '@/components/ui';
import { formatDate } from '@/lib/utils';
import { exportToExcel, exportToCSV } from '@/lib/export-service';
import { getCurrentDataSource } from '@/lib/ticket-service';
import { Ticket, TicketFilters } from '@/types';

const statusOptions = [
    { value: '', label: 'All Status' },
    { value: 'Open', label: 'Open' },
    { value: 'In Progress', label: 'In Progress' },
    { value: 'Completed', label: 'Completed' },
    { value: 'On Hold', label: 'On Hold' },
    { value: 'Cancelled', label: 'Cancelled' },
];

const priorityOptions = [
    { value: '', label: 'All Priority' },
    { value: 'Critical', label: 'Critical' },
    { value: 'High', label: 'High' },
    { value: 'Medium', label: 'Medium' },
    { value: 'Low', label: 'Low' },
];

const moduleOptions = [
    { value: '', label: 'All Modules' },
    { value: 'MM', label: 'MM - Materials' },
    { value: 'PP', label: 'PP - Production' },
    { value: 'FICO', label: 'FICO - Finance' },
    { value: 'SD', label: 'SD - Sales' },
    { value: 'HCM', label: 'HCM - Human Capital' },
    { value: 'WM', label: 'WM - Warehouse' },
    { value: 'QM', label: 'QM - Quality' },
    { value: 'PM', label: 'PM - Plant' },
];

export default function TicketsPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [showFilters, setShowFilters] = useState(true);
    const [isExporting, setIsExporting] = useState(false);
    
    const {
        filteredTickets,
        isLoading,
        filters,
        updateFilter,
        clearFilters,
        sortConfig,
        toggleSort,
    } = useTickets();
    
    const currentDataSource = getCurrentDataSource();
    
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
    
    // Handle row click
    const handleRowClick = useCallback((ticket: Ticket) => {
        router.push(`/tickets/${ticket.id}`);
    }, [router]);
    
    // Handle export
    const handleExport = async (format: 'excel' | 'csv') => {
        setIsExporting(true);
        try {
            if (format === 'excel') {
                await exportToExcel(filteredTickets, 'tickets_export');
            } else {
                exportToCSV(filteredTickets, 'tickets_export');
            }
        } finally {
            setIsExporting(false);
        }
    };
    
    return (
        <div className="space-y-6">
            {/* Page Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div className="flex items-center gap-4">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">Tickets</h1>
                        <p className="text-gray-500 mt-1">
                            {filteredTickets.length} tickets found
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
                <div className="flex items-center gap-2">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setShowFilters(!showFilters)}
                    >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                        </svg>
                        Filters
                    </Button>
                    <div className="relative">
                        <Button
                            variant="outline"
                            size="sm"
                            isLoading={isExporting}
                            onClick={() => handleExport('excel')}
                        >
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            Export
                        </Button>
                    </div>
                    <Link href="/tickets/new">
                        <Button size="sm">
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                            </svg>
                            New Ticket
                        </Button>
                    </Link>
                </div>
            </div>
            
            {/* Filters */}
            {showFilters && (
                <Card padding="none" className="overflow-hidden">
                    <div className="p-4 bg-gray-50 border-b border-gray-200">
                        <div className="flex items-center justify-between">
                            <h3 className="text-sm font-medium text-gray-700">Filters</h3>
                            <button
                                onClick={clearFilters}
                                className="text-sm text-[#D04A02] hover:underline"
                            >
                                Clear all
                            </button>
                        </div>
                    </div>
                    <div className="p-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-4">
                        <Input
                            placeholder="Search ID..."
                            value={filters.id}
                            onChange={(e) => updateFilter('id', e.target.value)}
                        />
                        <Input
                            placeholder="Search title..."
                            value={filters.title}
                            onChange={(e) => updateFilter('title', e.target.value)}
                        />
                        <Select
                            options={statusOptions}
                            value={filters.status}
                            onChange={(e) => updateFilter('status', e.target.value)}
                            placeholder="All Status"
                        />
                        <Select
                            options={priorityOptions}
                            value={filters.priority}
                            onChange={(e) => updateFilter('priority', e.target.value)}
                            placeholder="All Priority"
                        />
                        <Select
                            options={moduleOptions}
                            value={filters.module}
                            onChange={(e) => updateFilter('module', e.target.value)}
                            placeholder="All Modules"
                        />
                        <Input
                            placeholder="Search assignee..."
                            value={filters.assignedTo}
                            onChange={(e) => updateFilter('assignedTo', e.target.value)}
                        />
                    </div>
                </Card>
            )}
            
            {/* Tickets Table */}
            <Card padding="none" className="overflow-hidden">
                {isLoading ? (
                    <div className="flex items-center justify-center h-64">
                        <div className="spinner"></div>
                    </div>
                ) : filteredTickets.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-64 text-gray-500">
                        <svg className="w-16 h-16 mb-4 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                        </svg>
                        <p className="text-lg font-medium">No tickets found</p>
                        <p className="text-sm mt-1">Try adjusting your filters</p>
                    </div>
                ) : (
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead
                                    sortable
                                    sortDirection={sortConfig.column === 'id' ? sortConfig.direction : null}
                                    onSort={() => toggleSort('id')}
                                    width="80px"
                                >
                                    ID
                                </TableHead>
                                <TableHead
                                    sortable
                                    sortDirection={sortConfig.column === 'title' ? sortConfig.direction : null}
                                    onSort={() => toggleSort('title')}
                                >
                                    Title
                                </TableHead>
                                <TableHead width="100px">Module</TableHead>
                                <TableHead
                                    sortable
                                    sortDirection={sortConfig.column === 'status' ? sortConfig.direction : null}
                                    onSort={() => toggleSort('status')}
                                    width="120px"
                                >
                                    Status
                                </TableHead>
                                <TableHead
                                    sortable
                                    sortDirection={sortConfig.column === 'priority' ? sortConfig.direction : null}
                                    onSort={() => toggleSort('priority')}
                                    width="100px"
                                >
                                    Priority
                                </TableHead>
                                <TableHead
                                    sortable
                                    sortDirection={sortConfig.column === 'assignedTo' ? sortConfig.direction : null}
                                    onSort={() => toggleSort('assignedTo')}
                                    width="150px"
                                >
                                    Assigned To
                                </TableHead>
                                <TableHead
                                    sortable
                                    sortDirection={sortConfig.column === 'completionBy' ? sortConfig.direction : null}
                                    onSort={() => toggleSort('completionBy')}
                                    width="120px"
                                >
                                    Due Date
                                </TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {filteredTickets.map((ticket) => (
                                <TableRow
                                    key={ticket.id}
                                    isClickable
                                    onClick={() => handleRowClick(ticket)}
                                >
                                    <TableCell>
                                        <span className="text-xs font-mono text-gray-500">
                                            #{ticket.id}
                                        </span>
                                    </TableCell>
                                    <TableCell>
                                        <div className="max-w-md">
                                            <p className="font-medium text-gray-900 truncate">
                                                {ticket.title}
                                            </p>
                                            <p className="text-xs text-gray-500 truncate mt-0.5">
                                                {ticket.description}
                                            </p>
                                        </div>
                                    </TableCell>
                                    <TableCell>
                                        {ticket.module && (
                                            <span className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded font-medium">
                                                {ticket.module}
                                            </span>
                                        )}
                                    </TableCell>
                                    <TableCell>
                                        <StatusBadge status={ticket.status} size="sm" />
                                    </TableCell>
                                    <TableCell>
                                        <PriorityBadge priority={ticket.priority} size="sm" />
                                    </TableCell>
                                    <TableCell>
                                        <span className="text-sm text-gray-600">
                                            {ticket.assignedTo}
                                        </span>
                                    </TableCell>
                                    <TableCell>
                                        <span className={`text-sm ${
                                            new Date(ticket.completionBy) < new Date() && 
                                            ticket.status !== 'Completed' &&
                                            ticket.status !== 'Cancelled'
                                                ? 'text-red-600 font-medium'
                                                : 'text-gray-600'
                                        }`}>
                                            {formatDate(ticket.completionBy)}
                                        </span>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                )}
            </Card>
        </div>
    );
}
