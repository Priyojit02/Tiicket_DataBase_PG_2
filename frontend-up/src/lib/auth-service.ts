// ============================================
// AUTHENTICATION SERVICE - MSAL Azure AD
// ============================================

import { PublicClientApplication, Configuration, AuthenticationResult, AccountInfo } from '@azure/msal-browser';
import { AuthState, User } from '@/types';

// MSAL Configuration
const msalConfig: Configuration = {
    auth: {
        clientId: process.env.NEXT_PUBLIC_AZURE_CLIENT_ID || "033bcde2-d023-405e-8f84-ef33902bfb94",
        // Use 'organizations' to allow any Azure AD tenant (multi-tenant)
        // Use specific tenant ID if you want single-tenant only
        authority: process.env.NEXT_PUBLIC_AZURE_TENANT_ID 
            ? `https://login.microsoftonline.com/${process.env.NEXT_PUBLIC_AZURE_TENANT_ID}`
            : "https://login.microsoftonline.com/organizations",
        redirectUri: typeof window !== 'undefined' ? window.location.origin : "http://localhost:3000",
        postLogoutRedirectUri: typeof window !== 'undefined' ? window.location.origin : "http://localhost:3000",
    },
    cache: {
        cacheLocation: "sessionStorage",
        storeAuthStateInCookie: false,
    },
};

// Login request scopes
const loginRequest = {
    scopes: ["User.Read", "openid", "profile", "email"],
};

// Graph API scopes for user info
const graphConfig = {
    graphMeEndpoint: "https://graph.microsoft.com/v1.0/me",
};

// MSAL instance (singleton)
let msalInstance: PublicClientApplication | null = null;

/**
 * Initialize MSAL instance
 */
export async function initializeMsal(): Promise<PublicClientApplication> {
    if (!msalInstance) {
        msalInstance = new PublicClientApplication(msalConfig);
        await msalInstance.initialize();
        
        // Handle redirect response
        await msalInstance.handleRedirectPromise();
    }
    return msalInstance;
}

/**
 * Get MSAL instance
 */
export function getMsalInstance(): PublicClientApplication | null {
    return msalInstance;
}

/**
 * Login with popup
 */
export async function loginWithPopup(): Promise<AuthenticationResult | null> {
    try {
        const msal = await initializeMsal();
        const response = await msal.loginPopup(loginRequest);
        return response;
    } catch (error) {
        console.error("Login failed:", error);
        return null;
    }
}

/**
 * Login with redirect
 */
export async function loginWithRedirect(): Promise<void> {
    try {
        const msal = await initializeMsal();
        await msal.loginRedirect(loginRequest);
    } catch (error) {
        console.error("Login redirect failed:", error);
    }
}

/**
 * Logout
 */
export async function logout(): Promise<void> {
    try {
        const msal = await initializeMsal();
        const accounts = msal.getAllAccounts();
        if (accounts.length > 0) {
            await msal.logoutPopup({
                account: accounts[0],
                postLogoutRedirectUri: msalConfig.auth.postLogoutRedirectUri,
            });
        }
    } catch (error) {
        console.error("Logout failed:", error);
    }
}

/**
 * Logout with redirect
 */
export async function logoutWithRedirect(): Promise<void> {
    try {
        const msal = await initializeMsal();
        await msal.logoutRedirect();
    } catch (error) {
        console.error("Logout redirect failed:", error);
    }
}

/**
 * Get current account
 */
export async function getCurrentAccount(): Promise<AccountInfo | null> {
    try {
        const msal = await initializeMsal();
        const accounts = msal.getAllAccounts();
        return accounts.length > 0 ? accounts[0] : null;
    } catch (error) {
        console.error("Failed to get account:", error);
        return null;
    }
}

/**
 * Get access token silently
 */
export async function getAccessToken(): Promise<string | null> {
    try {
        const msal = await initializeMsal();
        const accounts = msal.getAllAccounts();
        
        if (accounts.length === 0) {
            return null;
        }
        
        const response = await msal.acquireTokenSilent({
            ...loginRequest,
            account: accounts[0],
        });
        
        return response.accessToken;
    } catch (error) {
        console.error("Token acquisition failed:", error);
        // Try interactive login if silent fails
        try {
            const msal = await initializeMsal();
            const response = await msal.acquireTokenPopup(loginRequest);
            return response.accessToken;
        } catch {
            return null;
        }
    }
}

/**
 * Get user profile from Microsoft Graph
 */
export async function getUserProfile(): Promise<User | null> {
    try {
        const accessToken = await getAccessToken();
        if (!accessToken) return null;
        
        const response = await fetch(graphConfig.graphMeEndpoint, {
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        });
        
        if (!response.ok) {
            throw new Error("Failed to fetch user profile");
        }
        
        const profileData = await response.json();
        
        return {
            id: profileData.id,
            name: profileData.displayName,
            email: profileData.mail || profileData.userPrincipalName,
            role: 'user', // Default role, can be customized
            avatar: profileData.photo || undefined,
            isAdmin: false, // Will be updated by admin service
            createdAt: new Date(),
            updatedAt: new Date(),
        };
    } catch (error) {
        console.error("Failed to get user profile:", error);
        return null;
    }
}

/**
 * Check if user is authenticated
 */
export async function isAuthenticated(): Promise<boolean> {
    const account = await getCurrentAccount();
    return account !== null;
}

/**
 * Get authentication state
 */
export async function getAuthState(): Promise<AuthState> {
    try {
        const account = await getCurrentAccount();
        
        if (!account) {
            return {
                isAuthenticated: false,
                user: null,
                loading: false,
            };
        }
        
        const user = await getUserProfile();
        
        return {
            isAuthenticated: true,
            user,
            loading: false,
        };
    } catch (error) {
        console.error("Auth state error:", error);
        return {
            isAuthenticated: false,
            user: null,
            loading: false,
            error: 'Failed to get authentication state',
        };
    }
}

/**
 * Get user initials from account
 */
export function getAccountInitials(account: AccountInfo | null): string {
    if (!account?.name) return "U";
    const parts = account.name.trim().split(" ");
    if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return account.name.substring(0, 2).toUpperCase();
}
