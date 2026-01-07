// ============================================
// Backend API Service - Data Fetching
// ============================================
// Uses Azure AD token directly (no JWT)

import api, { ApiError } from './api-client';
import { API_ENDPOINTS } from './api-config';
import type { Ticket, User, TicketLog, TicketComment } from '@/types';

// ============================================
// Auth API
// ============================================

export interface LoginResponse {
  id: number;
  azure_id: string;
  email: string;
  name: string;
  is_admin: boolean;
  is_active: boolean;
  department?: string;
  avatar_url?: string;
  created_at: string;
  updated_at: string;
}

export const authApi = {
  /**
   * Login with Azure AD access token
   * No JWT returned - backend validates Azure token directly
   */
  async login(azureAccessToken: string): Promise<LoginResponse> {
    return api.post<LoginResponse>(
      API_ENDPOINTS.auth.login,
      { access_token: azureAccessToken },
      false // No auth required for login
    );
  },

  /**
   * Get current user profile
   */
  async getMe(): Promise<User> {
    return api.get<User>(API_ENDPOINTS.auth.me);
  },

  /**
   * Verify current token is valid
   */
  async verifyToken(): Promise<{ valid: boolean; user: any }> {
    return api.get(API_ENDPOINTS.auth.verify);
  },
};

// ============================================
// Tickets API
// ============================================

export interface TicketListParams {
  skip?: number;
  limit?: number;
  status?: string;
  priority?: string;
  category?: string;
  assigned_to?: number;
  created_by?: number;
  search?: string;
  order_by?: string;
  order_desc?: boolean;
}

export interface TicketListResponse {
  items: Ticket[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface CreateTicketData {
  title: string;
  description: string;
  status?: string;
  priority?: string;
  category?: string;
  assigned_to?: number;
  assignee_id?: number;
}

export interface UpdateTicketData {
  title?: string;
  description?: string;
  status?: string;
  priority?: string;
  category?: string;
  assigned_to?: number;
}

export const ticketsApi = {
  /**
   * Get paginated list of tickets
   */
  async getTickets(params: TicketListParams = {}): Promise<TicketListResponse> {
    return api.get<TicketListResponse>(API_ENDPOINTS.tickets.list, params);
  },

  /**
   * Get ticket by ID
   */
  async getTicket(id: number): Promise<Ticket> {
    return api.get<Ticket>(API_ENDPOINTS.tickets.get(id));
  },

  /**
   * Get ticket by ticket_id (T-001 format)
   */
  async getTicketByTicketId(ticketId: string): Promise<Ticket> {
    return api.get<Ticket>(API_ENDPOINTS.tickets.getByTicketId(ticketId));
  },

  /**
   * Create a new ticket
   */
  async createTicket(data: CreateTicketData): Promise<Ticket> {
    return api.post<Ticket>(API_ENDPOINTS.tickets.create, data);
  },

  /**
   * Update a ticket
   */
  async updateTicket(id: number, data: UpdateTicketData): Promise<Ticket> {
    return api.patch<Ticket>(API_ENDPOINTS.tickets.update(id), data);
  },

  /**
   * Delete a ticket
   */
  async deleteTicket(id: number): Promise<void> {
    return api.delete(API_ENDPOINTS.tickets.delete(id));
  },

  /**
   * Get recent tickets
   */
  async getRecentTickets(limit = 10): Promise<Ticket[]> {
    return api.get<Ticket[]>(API_ENDPOINTS.tickets.recent, { limit });
  },

  /**
   * Get my tickets
   */
  async getMyTickets(params: { skip?: number; limit?: number } = {}): Promise<TicketListResponse> {
    return api.get<TicketListResponse>(API_ENDPOINTS.tickets.my, params);
  },

  /**
   * Get ticket logs
   */
  async getTicketLogs(ticketId: number): Promise<TicketLog[]> {
    return api.get<TicketLog[]>(API_ENDPOINTS.tickets.logs(ticketId));
  },

  /**
   * Add comment to ticket
   */
  async addComment(ticketId: number, content: string, isInternal = false): Promise<TicketComment> {
    return api.post<TicketComment>(
      API_ENDPOINTS.tickets.comments.add(ticketId),
      { content, is_internal: isInternal, ticket_id: ticketId }
    );
  },

  /**
   * Update comment
   */
  async updateComment(commentId: number, content: string): Promise<TicketComment> {
    return api.patch<TicketComment>(
      API_ENDPOINTS.tickets.comments.update(commentId),
      { content }
    );
  },

  /**
   * Delete comment
   */
  async deleteComment(commentId: number): Promise<void> {
    return api.delete(API_ENDPOINTS.tickets.comments.delete(commentId));
  },
};

// ============================================
// Users API
// ============================================

export const usersApi = {
  /**
   * Get all users
   */
  async getUsers(params: { skip?: number; limit?: number } = {}): Promise<User[]> {
    return api.get<User[]>(API_ENDPOINTS.users.list, params);
  },

  /**
   * Get user by ID
   */
  async getUser(id: number): Promise<User> {
    return api.get<User>(API_ENDPOINTS.users.get(id));
  },

  /**
   * Search users
   */
  async searchUsers(query: string, params: { skip?: number; limit?: number } = {}): Promise<User[]> {
    return api.get<User[]>(API_ENDPOINTS.users.search, { query, ...params });
  },

  /**
   * Get assignable users
   */
  async getAssignableUsers(): Promise<User[]> {
    return api.get<User[]>(API_ENDPOINTS.users.assignable);
  },

  /**
   * Update profile
   */
  async updateProfile(data: { name?: string; department?: string }): Promise<User> {
    return api.patch<User>(API_ENDPOINTS.users.profile, data);
  },
};

// ============================================
// Admin API
// ============================================

export const adminApi = {
  /**
   * Get all users (admin)
   */
  async getAllUsers(params: { skip?: number; limit?: number } = {}): Promise<User[]> {
    return api.get<User[]>(API_ENDPOINTS.admin.users, params);
  },

  /**
   * Get all admins
   */
  async getAdmins(): Promise<User[]> {
    return api.get<User[]>(API_ENDPOINTS.admin.admins);
  },

  /**
   * Add admin
   */
  async addAdmin(userId: number): Promise<User> {
    return api.post<User>(API_ENDPOINTS.admin.addAdmin, { user_id: userId });
  },

  /**
   * Remove admin
   */
  async removeAdmin(userId: number): Promise<User> {
    return api.post<User>(API_ENDPOINTS.admin.removeAdmin, { user_id: userId });
  },

  /**
   * Get admin stats
   */
  async getStats(): Promise<{ total_users: number; total_admins: number }> {
    return api.get(API_ENDPOINTS.admin.stats);
  },

  /**
   * Get audit logs
   */
  async getAuditLogs(params: { skip?: number; limit?: number } = {}): Promise<any[]> {
    return api.get(API_ENDPOINTS.admin.auditLogs, params);
  },

  /**
   * Deactivate user
   */
  async deactivateUser(userId: number): Promise<void> {
    return api.post(API_ENDPOINTS.admin.deactivateUser(userId));
  },

  /**
   * Reactivate user
   */
  async reactivateUser(userId: number): Promise<void> {
    return api.post(API_ENDPOINTS.admin.reactivateUser(userId));
  },
};

// ============================================
// Analytics API
// ============================================

export interface DashboardStats {
  total_tickets: number;
  open_tickets: number;
  resolved_today: number;
  avg_response_time: number | null;
  tickets_by_status: Record<string, number>;
  tickets_by_priority: Record<string, number>;
  recent_tickets: Ticket[];
}

export interface AnalyticsResponse {
  ticket_stats: {
    total: number;
    open: number;
    in_progress: number;
    resolved: number;
    closed: number;
    awaiting_info: number;
  };
  category_breakdown: Array<{
    category: string;
    count: number;
    percentage: number;
  }>;
  priority_breakdown: Array<{
    priority: string;
    count: number;
    percentage: number;
  }>;
  daily_trends: Array<{
    date: string;
    count: number;
  }>;
  avg_resolution_time: number | null;
  sla_compliance_rate: number | null;
}

export const analyticsApi = {
  /**
   * Get dashboard statistics
   */
  async getDashboardStats(): Promise<DashboardStats> {
    return api.get<DashboardStats>(API_ENDPOINTS.analytics.dashboard);
  },

  /**
   * Get full analytics
   */
  async getFullAnalytics(days = 30): Promise<AnalyticsResponse> {
    return api.get<AnalyticsResponse>(API_ENDPOINTS.analytics.full, { days });
  },

  /**
   * Get user analytics
   */
  async getUserAnalytics(): Promise<any> {
    return api.get(API_ENDPOINTS.analytics.user);
  },

  /**
   * Get category summary
   */
  async getCategorySummary(): Promise<any[]> {
    return api.get(API_ENDPOINTS.analytics.categories);
  },
};

// ============================================
// Email Processing API (Admin only)
// ============================================

export const emailsApi = {
  /**
   * Trigger email fetch
   */
  async triggerFetch(params: { days_back?: number; max_emails?: number } = {}): Promise<any> {
    return api.post(API_ENDPOINTS.emails.fetch, null, true, params);
  },

  /**
   * Get email stats
   */
  async getStats(): Promise<any> {
    return api.get(API_ENDPOINTS.emails.stats);
  },

  /**
   * Get recent emails
   */
  async getRecent(limit = 10): Promise<any[]> {
    return api.get(API_ENDPOINTS.emails.recent, { limit });
  },

  /**
   * Get unprocessed emails
   */
  async getUnprocessed(limit = 50): Promise<any[]> {
    return api.get(API_ENDPOINTS.emails.unprocessed, { limit });
  },

  /**
   * Reprocess an email
   */
  async reprocess(emailId: number): Promise<any> {
    return api.post(API_ENDPOINTS.emails.reprocess(emailId));
  },
};

// Export all APIs
export default {
  auth: authApi,
  tickets: ticketsApi,
  users: usersApi,
  admin: adminApi,
  analytics: analyticsApi,
  emails: emailsApi,
};
