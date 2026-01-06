// ============================================
// ANALYTICS HOOK - Analytics State Management
// ============================================

import { useState, useEffect, useMemo, useCallback } from 'react';
import { Ticket, AnalyticsData } from '@/types';
import { 
    calculateAnalytics, 
    getOverdueTicketDetails,
    getUpcomingDeadlineDetails,
    getAssigneeWorkloadReport,
    getPriorityDistribution,
    getModuleDistribution,
    getStatusSummary,
    getDateRangeReport,
} from '@/lib/analytics-service';

interface UseAnalyticsOptions {
    tickets: Ticket[];
    upcomingDays?: number;
}

interface UseAnalyticsReturn {
    analytics: AnalyticsData;
    overdueTickets: (Ticket & { daysOverdue: number })[];
    upcomingTickets: (Ticket & { daysUntilDue: number })[];
    workloadReport: ReturnType<typeof getAssigneeWorkloadReport>;
    priorityDistribution: ReturnType<typeof getPriorityDistribution>;
    moduleDistribution: ReturnType<typeof getModuleDistribution>;
    statusSummary: ReturnType<typeof getStatusSummary>;
    isCalculating: boolean;
    
    // Actions
    getDateRangeData: (startDate: string, endDate: string) => ReturnType<typeof getDateRangeReport>;
    recalculate: () => void;
}

export function useAnalytics(options: UseAnalyticsOptions): UseAnalyticsReturn {
    const { tickets, upcomingDays = 7 } = options;
    const [isCalculating, setIsCalculating] = useState(false);
    const [calculationKey, setCalculationKey] = useState(0);
    
    // Calculate analytics data
    const analytics = useMemo(() => {
        return calculateAnalytics(tickets);
    }, [tickets]);
    
    // Get overdue tickets with details
    const overdueTickets = useMemo(() => {
        return getOverdueTicketDetails(tickets);
    }, [tickets]);
    
    // Get upcoming deadline tickets
    const upcomingTickets = useMemo(() => {
        return getUpcomingDeadlineDetails(tickets, upcomingDays);
    }, [tickets, upcomingDays]);
    
    // Get workload report
    const workloadReport = useMemo(() => {
        return getAssigneeWorkloadReport(tickets);
    }, [tickets]);
    
    // Get priority distribution
    const priorityDistribution = useMemo(() => {
        return getPriorityDistribution(tickets);
    }, [tickets]);
    
    // Get module distribution
    const moduleDistribution = useMemo(() => {
        return getModuleDistribution(tickets);
    }, [tickets]);
    
    // Get status summary
    const statusSummary = useMemo(() => {
        return getStatusSummary(tickets);
    }, [tickets]);
    
    // Get date range report data
    const getDateRangeData = useCallback((startDate: string, endDate: string) => {
        return getDateRangeReport(tickets, startDate, endDate);
    }, [tickets]);
    
    // Force recalculation
    const recalculate = useCallback(() => {
        setCalculationKey(prev => prev + 1);
    }, []);
    
    return {
        analytics,
        overdueTickets,
        upcomingTickets,
        workloadReport,
        priorityDistribution,
        moduleDistribution,
        statusSummary,
        isCalculating,
        getDateRangeData,
        recalculate,
    };
}

/**
 * Hook for date range report
 */
export function useDateRangeReport(tickets: Ticket[]) {
    const [dateRange, setDateRange] = useState({
        startDate: '',
        endDate: '',
    });
    const [reportData, setReportData] = useState<ReturnType<typeof getDateRangeReport> | null>(null);
    
    // Update date range
    const updateDateRange = useCallback((startDate: string, endDate: string) => {
        setDateRange({ startDate, endDate });
    }, []);
    
    // Calculate report when dates change
    useEffect(() => {
        if (dateRange.startDate && dateRange.endDate) {
            const data = getDateRangeReport(tickets, dateRange.startDate, dateRange.endDate);
            setReportData(data);
        } else {
            setReportData(null);
        }
    }, [tickets, dateRange]);
    
    return {
        dateRange,
        reportData,
        updateDateRange,
    };
}

/**
 * Hook for assignee workload
 */
export function useAssigneeWorkload(tickets: Ticket[], selectedAssignee?: string) {
    const workloadReport = useMemo(() => {
        return getAssigneeWorkloadReport(tickets);
    }, [tickets]);
    
    const selectedWorkload = useMemo(() => {
        if (!selectedAssignee) return null;
        return workloadReport.find(w => w.assignee === selectedAssignee) || null;
    }, [workloadReport, selectedAssignee]);
    
    const assigneeTickets = useMemo(() => {
        if (!selectedAssignee) return [];
        return tickets.filter(t => t.assignedTo === selectedAssignee);
    }, [tickets, selectedAssignee]);
    
    return {
        workloadReport,
        selectedWorkload,
        assigneeTickets,
    };
}
