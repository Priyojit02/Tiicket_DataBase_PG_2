// ============================================
// API Configuration - Backend Connection
// ============================================
// Uses Azure AD token directly (no JWT)

// Backend API base URL
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
console.log('🔍 API_CONFIG - NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);
console.log('🔍 API_CONFIG - API_BASE_URL:', API_BASE_URL);

// API endpoints
export const API_ENDPOINTS = {
  // Auth (No JWT - uses Azure AD token directly)
  auth: {
    login: '/api/v1/auth/login',
    me: '/api/v1/auth/me',
    verify: '/api/v1/auth/verify',
  },
  
  // Tickets
  tickets: {
    list: '/api/v1/tickets',
    create: '/api/v1/tickets',
    get: (id: number) => `/api/v1/tickets/${id}`,
    getByTicketId: (ticketId: string) => `/api/v1/tickets/by-ticket-id/${ticketId}`,
    update: (id: number) => `/api/v1/tickets/${id}`,
    delete: (id: number) => `/api/v1/tickets/${id}`,
    recent: '/api/v1/tickets/recent',
    my: '/api/v1/tickets/my',
    logs: (id: number) => `/api/v1/tickets/${id}/logs`,
    comments: {
      add: (ticketId: number) => `/api/v1/tickets/${ticketId}/comments`,
      update: (commentId: number) => `/api/v1/tickets/comments/${commentId}`,
      delete: (commentId: number) => `/api/v1/tickets/comments/${commentId}`,
    },
  },
  
  // Users
  users: {
    list: '/api/v1/users',
    get: (id: number) => `/api/v1/users/${id}`,
    search: '/api/v1/users/search',
    assignable: '/api/v1/users/assignable',
    count: '/api/v1/users/count',
    profile: '/api/v1/users/profile',
  },
  
  // Admin
  admin: {
    users: '/api/v1/admin/users',
    admins: '/api/v1/admin/admins',
    addAdmin: '/api/v1/admin/admins/add',
    removeAdmin: '/api/v1/admin/admins/remove',
    stats: '/api/v1/admin/stats',
    auditLogs: '/api/v1/admin/audit-logs',
    deactivateUser: (id: number) => `/api/v1/admin/users/${id}/deactivate`,
    reactivateUser: (id: number) => `/api/v1/admin/users/${id}/reactivate`,
  },
  
  // Analytics
  analytics: {
    dashboard: '/api/v1/analytics/dashboard',
    full: '/api/v1/analytics/full',
    user: '/api/v1/analytics/user',
    categories: '/api/v1/analytics/categories',
  },
  
  // Email Processing
  emails: {
    fetch: '/api/v1/emails/fetch',
    stats: '/api/v1/emails/stats',
    recent: '/api/v1/emails/recent',
    unprocessed: '/api/v1/emails/unprocessed',
    reprocess: (id: number) => `/api/v1/emails/${id}/reprocess`,
    byCategory: (category: string) => `/api/v1/emails/by-category/${category}`,
  },
};

// Request configuration
export const API_CONFIG = {
  timeout: 30000, // 30 seconds
  retries: 3,
};
c
