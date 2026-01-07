// ============================================
// SETTINGS PAGE
// ============================================

'use client';

import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { Button, Card, Input } from '@/components/ui';

export default function SettingsPage() {
    const { user } = useAuth();
    const [notifications, setNotifications] = useState({
        email: true,
        ticketUpdates: true,
        weeklyDigest: false,
        mentionAlerts: true,
    });
    
    return (
        <div className="max-w-3xl mx-auto space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
                <p className="text-gray-500">Manage your account preferences</p>
            </div>
            
            {/* Notification Settings */}
            <Card className="p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Notifications</h2>
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="font-medium text-gray-900">Email Notifications</p>
                            <p className="text-sm text-gray-500">Receive notifications via email</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={notifications.email}
                                onChange={(e) => setNotifications({ ...notifications, email: e.target.checked })}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-[#D04A02]/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#D04A02]"></div>
                        </label>
                    </div>
                    
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="font-medium text-gray-900">Ticket Updates</p>
                            <p className="text-sm text-gray-500">Get notified when tickets are updated</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={notifications.ticketUpdates}
                                onChange={(e) => setNotifications({ ...notifications, ticketUpdates: e.target.checked })}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-[#D04A02]/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#D04A02]"></div>
                        </label>
                    </div>
                    
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="font-medium text-gray-900">Weekly Digest</p>
                            <p className="text-sm text-gray-500">Receive a weekly summary of activity</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={notifications.weeklyDigest}
                                onChange={(e) => setNotifications({ ...notifications, weeklyDigest: e.target.checked })}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-[#D04A02]/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#D04A02]"></div>
                        </label>
                    </div>
                    
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="font-medium text-gray-900">Mention Alerts</p>
                            <p className="text-sm text-gray-500">Get notified when you&apos;re mentioned</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={notifications.mentionAlerts}
                                onChange={(e) => setNotifications({ ...notifications, mentionAlerts: e.target.checked })}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-[#D04A02]/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#D04A02]"></div>
                        </label>
                    </div>
                </div>
            </Card>
            
            {/* Display Settings */}
            <Card className="p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Display</h2>
                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Date Format
                        </label>
                        <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#D04A02]">
                            <option>DD/MM/YYYY</option>
                            <option>MM/DD/YYYY</option>
                            <option>YYYY-MM-DD</option>
                        </select>
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Tickets Per Page
                        </label>
                        <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#D04A02]">
                            <option>10</option>
                            <option>25</option>
                            <option>50</option>
                            <option>100</option>
                        </select>
                    </div>
                </div>
            </Card>
            
            {/* Data Source Info */}
            <Card className="p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Data Source</h2>
                <div className="space-y-4">
                    <div className="p-4 bg-blue-50 rounded-lg">
                        <p className="text-sm text-blue-800 mb-2">
                            <strong>Data source is controlled by frontend-up/.env.local</strong>
                        </p>
                        <p className="text-xs text-blue-600">
                            Current mode: <code className="bg-blue-100 px-1 rounded">USE_DB={process.env.USE_DB || 'combined'}</code>
                        </p>
                        <p className="text-xs text-blue-600 mt-1">
                            To change data source, edit the USE_DB variable in frontend-up/.env.local
                        </p>
                    </div>
                </div>
            </Card>
            
            {/* Account Info */}
            <Card className="p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Account Information</h2>
                <div className="space-y-2 text-sm">
                    <div className="flex justify-between py-2 border-b border-gray-100">
                        <span className="text-gray-500">Email</span>
                        <span className="font-medium text-gray-900">{user?.email || 'user@pwc.com'}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-gray-100">
                        <span className="text-gray-500">Account Type</span>
                        <span className="font-medium text-gray-900">{user?.isAdmin ? 'Administrator' : 'Standard User'}</span>
                    </div>
                    <div className="flex justify-between py-2">
                        <span className="text-gray-500">Authentication</span>
                        <span className="font-medium text-gray-900">Microsoft SSO</span>
                    </div>
                </div>
            </Card>
            
            {/* Save Button */}
            <div className="flex justify-end">
                <Button>Save Changes</Button>
            </div>
        </div>
    );
}
