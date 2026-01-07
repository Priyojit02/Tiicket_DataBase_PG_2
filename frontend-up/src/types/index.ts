// ============================================
// TICKET MANAGEMENT SYSTEM - TYPE DEFINITIONS
// ============================================

// User Types
export interface User {
    id: string;
    email: string;
    name: string;
    role: UserRole;
    avatar?: string;
    isAdmin: boolean;
    isActive?: boolean;
    createdAt: Date;
    updatedAt: Date;
}

export type UserRole = 'admin' | 'manager' | 'user';

// Admin Types
export interface AdminUser {
    id: string;
    email: string;
    name: string;
    isAdmin: boolean;
    addedBy: string;
    addedAt: Date;
}

export interface DBUser {
    id: string;
    email: string;
    name: string;
    lastLogin: Date;
    isActive: boolean;
    isAdmin: boolean;
}

// Ticket Log Types (Activity Tracking)
export interface TicketLog {
    id: number;
    action: TicketAction;
    performedBy: string;
    timestamp: string;
    details: string;
}

export type TicketAction = 
    | 'ticket_created' 
    | 'assigned' 
    | 'status_changed' 
    | 'comment_added' 
    | 'ticket_closed'
    | 'priority_changed'
    | 'reassigned';

// Ticket Comment Types
export interface TicketComment {
    id: number;
    author: string;
    role: 'raiser' | 'assignee' | 'admin' | 'viewer';
    message: string;
    timestamp: string;
}

// Ticket Types
export interface Ticket {
    id: number;
    title: string;
    description: string;
    status: TicketStatus;
    priority: TicketPriority;
    assignedTo: string;
    assignedToEmail?: string;
    raisedBy: string;
    createdBy?: string;
    createdOn: string;
    completionBy: string;
    closedOn: string | null;
    module?: SAPModule;
    tags?: string[];
    logs: TicketLog[];
    comments: TicketComment[];
    attachments?: Attachment[];
    emailSource?: EmailSource;
}

export type TicketStatus = 'Open' | 'In Progress' | 'Awaiting Info' | 'Resolved' | 'Closed';

export type TicketPriority = 'Low' | 'Medium' | 'High' | 'Critical';

export type SAPModule = 'MM' | 'SD' | 'FICO' | 'PP' | 'HCM' | 'PM' | 'QM' | 'WM' | 'PS' | 'BW' | 'ABAP' | 'BASIS' | 'OTHER';

// Attachment Types
export interface Attachment {
    id: string;
    ticketId: number;
    fileName: string;
    fileUrl: string;
    fileType: string;
    fileSize: number;
    uploadedBy: string;
    uploadedAt: Date;
}

// Email Source (for LLM-parsed tickets)
export interface EmailSource {
    emailId: string;
    subject: string;
    from: string;
    receivedAt: Date;
    parsedContent?: string;
}

// Filter Types
export interface TicketFilters {
    id?: string;
    title?: string;
    status?: TicketStatus | '';
    assignedTo?: string;
    completionBy?: string;
    priority?: TicketPriority | '';
    module?: SAPModule | '';
    dateFrom?: string;
    dateTo?: string;
    search?: string;
}

// Sort Types
export interface SortConfig {
    column: keyof Ticket;
    direction: 'asc' | 'desc';
    key?: keyof Ticket; // Alias for column
}

// Create/Update Ticket Payloads
export interface CreateTicketPayload {
    title: string;
    description?: string;
    status?: TicketStatus;
    priority?: TicketPriority;
    assignedTo: string;
    completionBy: string;
    module?: SAPModule;
    tags?: string[];
    createdBy?: string;
    raisedBy?: string;
}

export interface UpdateTicketPayload {
    title?: string;
    description?: string;
    status?: TicketStatus;
    priority?: TicketPriority;
    assignedTo?: string;
    completionBy?: string;
    module?: SAPModule;
    tags?: string[];
}

// Analytics Types
export interface TicketStats {
    total: number;
    open: number;
    inProgress: number;
    completed: number;
    onHold: number;
    cancelled: number;
    overdue: number;
}

export interface AnalyticsData {
    // Basic counts
    totalTickets: number;
    openTickets: number;
    inProgressTickets: number;
    completedTickets: number;
    onHoldTickets: number;
    overdueTickets: number;
    upcomingDeadlines: number;
    // Breakdowns
    byPriority: Record<string, number>;
    byStatus: Record<string, number>;
    byModule: Record<string, number>;
    byAssignee: Record<string, number>;
    // Legacy support
    stats?: TicketStats;
}

export interface AssigneeWorkload {
    assignee: string;
    total: number;
    open: number;
    inProgress: number;
    completed: number;
    overdue: number;
}

// Report Types
export interface DateRangeReport {
    startDate: string;
    endDate: string;
    openedTickets: Ticket[];
    closedTickets: Ticket[];
    netChange: number;
}

export interface WorkloadReport {
    assignee: string;
    tickets: Ticket[];
    stats: {
        total: number;
        open: number;
        inProgress: number;
        completed: number;
        overdue: number;
    };
}

// API Response Types
export interface ApiResponse<T> {
    success: boolean;
    data?: T;
    error?: string;
    message?: string;
}

export interface PaginatedResponse<T> {
    data: T[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
}

// Auth Types
export interface AuthState {
    isAuthenticated: boolean;
    user: User | null;
    loading: boolean;
    isLoading?: boolean; // Alias for loading
    error?: string | null;
}

export interface LoginCredentials {
    accessToken: string;
}

// Navigation Types
export type NavTab = 'tickets' | 'analytics' | 'reports';

// Export Action Types
export type ExportFormat = 'xlsx' | 'csv' | 'pdf';

export interface ExportOptions {
    format: ExportFormat;
    filename: string;
    data: Ticket[];
    columns?: (keyof Ticket)[];
}

// Admin Panel Types
export interface AdminPanelData {
    users: DBUser[];
    admins: AdminUser[];
    totalUsers: number;
    activeUsers: number;
}

export interface AddAdminPayload {
    email: string;
    name: string;
}

export interface RemoveAdminPayload {
    userId: string;
}
