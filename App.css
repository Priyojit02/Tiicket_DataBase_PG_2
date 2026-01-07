import { useState, useRef, useEffect } from "react";
import "../App.css";
import Analytics from "../pages/Analytics";
import Reports from "../pages/Reports";
import Tickets from "../pages/Tickets";
import pwcLogo from "../assets/pwcicon.jpg";
import ObjectPage from "../pages/ObjectPage";
import apiService from "../services/apiService";

function TicketDashboard({ user, onLogout }) {
    // Profile dropdown state
    const [showProfileMenu, setShowProfileMenu] = useState(false);
    const [activeTab, setActiveTab] = useState("tickets");
    const profileRef = useRef(null);
    const [selectedTicketId, setSelectedTicketId] = useState(null);

    // Sync state
    const [isSyncing, setIsSyncing] = useState(false);
    const [syncResult, setSyncResult] = useState(null);
    const [showSyncResult, setShowSyncResult] = useState(false);

    // Close dropdown when clicking outside
    useEffect(() => {
        function handleClickOutside(event) {
            if (profileRef.current && !profileRef.current.contains(event.target)) {
                setShowProfileMenu(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    // Get user initials for avatar
    function getUserInitials(name) {
        if (!name) return "U";
        const parts = name.trim().split(" ");
        if (parts.length >= 2) {
            return (parts[0][0] + parts[1][0]).toUpperCase();
        }
        return name.substring(0, 2).toUpperCase();
    }

    // Sync emails and create tickets
    async function handleSyncEmails() {
        setIsSyncing(true);
        setSyncResult(null);
        setShowSyncResult(false);

        try {
            console.log("🔄 Starting email sync...");
            const result = await apiService.fetchEmails("inbox", 1, 50);

            setSyncResult({
                success: true,
                message: "Email sync completed!",
                data: result
            });
            setShowSyncResult(true);

            // Hide result after 5 seconds
            setTimeout(() => setShowSyncResult(false), 5000);

            console.log("✅ Email sync successful:", result);

        } catch (error) {
            console.error("❌ Email sync failed:", error);
            setSyncResult({
                success: false,
                message: `Sync failed: ${error.message}`,
                error: error
            });
            setShowSyncResult(true);

            // Hide error after 8 seconds
            setTimeout(() => setShowSyncResult(false), 8000);
        } finally {
            setIsSyncing(false);
        }
    }

    return (
        <div className="page-dashboard">
            {/* Top Navigation Bar */}
            <nav className="navbar">
                <div className="navbar-left">
                    <img src={pwcLogo} alt="PwC Logo" className="logo-small" />
                    <span className="navbar-title">Ticket Management System</span>
                </div>
                <div className="navbar-center">
                    <button
                        className={`navbar-tab ${activeTab === "tickets" ? "active" : ""}`}
                        onClick={() => setActiveTab("tickets")}
                    >
                        All Tickets
                    </button>
                    <button
                        className={`navbar-tab ${activeTab === "analytics" ? "active" : ""}`}
                        onClick={() => setActiveTab("analytics")}
                    >
                        Analytics
                    </button>
                    <button
                        className={`navbar-tab ${activeTab === "reports" ? "active" : ""}`}
                        onClick={() => setActiveTab("reports")}
                    >
                        Reports
                    </button>
                </div>
                <div className="navbar-right">
                    {/* Sync Button */}
                    <button
                        className={`sync-button ${isSyncing ? 'syncing' : ''}`}
                        onClick={handleSyncEmails}
                        disabled={isSyncing}
                        title="Sync emails and create tickets"
                    >
                        {isSyncing ? (
                            <>
                                <span className="sync-spinner">⟳</span>
                                Syncing...
                            </>
                        ) : (
                            <>
                                <span className="sync-icon">🔄</span>
                                Sync Emails
                            </>
                        )}
                    </button>

                    {/* Sync Result Toast */}
                    {showSyncResult && syncResult && (
                        <div className={`sync-result ${syncResult.success ? 'success' : 'error'}`}>
                            <span className="sync-result-icon">
                                {syncResult.success ? '✅' : '❌'}
                            </span>
                            <span className="sync-result-message">
                                {syncResult.message}
                                {syncResult.data && (
                                    <small>
                                        ({syncResult.data.fetched_count || 0} emails, {syncResult.data.stats?.tickets_created || 0} tickets)
                                    </small>
                                )}
                            </span>
                        </div>
                    )}

                    <div className="profile-container" ref={profileRef}>
                        <button
                            className="profile-button"
                            onClick={() => setShowProfileMenu(!showProfileMenu)}
                            title={user?.name}
                        >
                            {getUserInitials(user?.name)}
                        </button>
                        {showProfileMenu && (
                            <div className="profile-dropdown">
                                <div className="profile-dropdown-header">
                                    <div className="profile-avatar-large">
                                        {getUserInitials(user?.name)}
                                    </div>
                                    <div className="profile-info">
                                        <span className="profile-name">{user?.name}</span>
                                        <span className="profile-email">{user?.email}</span>
                                    </div>
                                </div>
                                <div className="profile-dropdown-divider"></div>
                                <ul className="profile-dropdown-menu">
                                    <li
                                        className="profile-dropdown-item"
                                        onClick={() => alert("View Profile clicked (placeholder)")}
                                    >
                                        <span className="profile-dropdown-icon">👤</span>
                                        View Profile
                                    </li>
                                    <li
                                        className="profile-dropdown-item"
                                        onClick={() => alert("Settings clicked (placeholder)")}
                                    >
                                        <span className="profile-dropdown-icon">⚙️</span>
                                        Settings
                                    </li>
                                </ul>
                                <div className="profile-dropdown-divider"></div>
                                <ul className="profile-dropdown-menu">
                                    <li
                                        className="profile-dropdown-item profile-dropdown-logout"
                                        onClick={onLogout}
                                    >
                                        <span className="profile-dropdown-icon">🚪</span>
                                        Logout
                                    </li>
                                </ul>
                            </div>
                        )}
                    </div>
                </div>
            </nav>
            {/* Main Content */}
            <div className="main-content">
                {selectedTicketId ? (
                    <ObjectPage
                        ticketId={selectedTicketId}
                        onBack={() => setSelectedTicketId(null)}
                    />
                ) : (
                    <>
                        {activeTab === "tickets" && (
                            <Tickets onTicketClick={(id) => setSelectedTicketId(id)} />
                        )}
                        {activeTab === "analytics" && <Analytics />}
                        {activeTab === "reports" && <Reports />}
                    </>
                )}
            </div>
        </div>
    );
}

export default TicketDashboard;
