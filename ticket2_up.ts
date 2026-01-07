// ============================================
// TICKETS DATA - COMBINED DUMMY + LLM TICKETS
// ============================================
// Mode: combined
// Auto-generated from database on 2026-01-07 07:44:13 UTC
// Total tickets: 0
// Data source mode controlled by .env DATA_SOURCE_MODE

import { Ticket } from '@/types';

// Load static LLM tickets
const staticTickets: Ticket[] = [];

// Load user-created tickets from localStorage (treated as LLM tickets)
let userCreatedTickets: Ticket[] = [];
if (typeof window !== 'undefined') {
    try {
        const stored = localStorage.getItem('userCreatedTickets');
        if (stored) {
            userCreatedTickets = JSON.parse(stored);
        }
    } catch (error) {
        console.error('Failed to load user tickets from localStorage:', error);
    }
}

// Combine static tickets with user-created tickets
export const ticketsData: Ticket[] = [...staticTickets, ...userCreatedTickets];
