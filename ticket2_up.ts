// ============================================
// TICKETS DATA - COMBINED DUMMY + LLM TICKETS
// ============================================
// Mode: combined
// Auto-generated from database on 2026-01-07 07:44:13 UTC
// Total tickets: 0
// Data source mode controlled by .env DATA_SOURCE_MODE

import { Ticket } from '@/types';

// Static LLM tickets from backend
const staticTickets: Ticket[] = [];

// Function to load user-created tickets from localStorage
function loadUserCreatedTickets(): Ticket[] {
    if (typeof window === 'undefined') {
        return []; // Server-side, no localStorage
    }

    try {
        const stored = localStorage.getItem('userCreatedTickets');
        return stored ? JSON.parse(stored) : [];
    } catch (error) {
        console.error('Failed to load user tickets from localStorage:', error);
        return [];
    }
}

// Export function that loads data dynamically
export function getTicketsData(): Ticket[] {
    const userTickets = loadUserCreatedTickets();
    return [...staticTickets, ...userTickets];
}

// For backward compatibility, also export the data directly
// This will be empty on server-side, but populated on client-side
export const ticketsData: Ticket[] = typeof window !== 'undefined' ? getTicketsData() : [];
