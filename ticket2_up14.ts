// ============================================
// TICKETS DATA - COMBINED DUMMY + LLM TICKETS
// ============================================
// Mode: combined
// Auto-generated from database on 2026-01-08 00:12:37 UTC
// Total tickets: 0
// Data source mode controlled by .env DATA_SOURCE_MODE

import { Ticket } from '@/types';

// Static LLM tickets from backend
const staticTickets: Ticket[] = [];

// Function to load user-created tickets from localStorage
function loadUserCreatedTickets(): Ticket[] {
    if (typeof window === 'undefined') {
        console.log('📄 tickets2.ts: Server-side, returning empty array');
        return []; // Server-side, no localStorage
    }

    try {
        const stored = localStorage.getItem('userCreatedTickets');
        console.log('📄 tickets2.ts: Checking localStorage:', stored ? `Found ${JSON.parse(stored).length} tickets` : 'No data');
        const tickets = stored ? JSON.parse(stored) : [];
        console.log('📄 tickets2.ts: Loaded user tickets:', tickets.length);
        return tickets;
    } catch (error) {
        console.error('📄 tickets2.ts: Failed to load user tickets from localStorage:', error);
        return [];
    }
}

// Export function that loads data dynamically
export function getTicketsData(): Ticket[] {
    const staticTickets: Ticket[] = [];
    const userTickets = loadUserCreatedTickets();
    const combined = [...staticTickets, ...userTickets];
    console.log(`📄 tickets2.ts: getTicketsData returning ${combined.length} total tickets (${staticTickets.length} static + ${userTickets.length} user)`);
    return combined;
}

// For backward compatibility, also export the data directly
// This will be empty on server-side, but populated on client-side
export const ticketsData: Ticket[] = typeof window !== 'undefined' ? getTicketsData() : [];
