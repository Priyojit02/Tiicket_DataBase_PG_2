// ============================================
// NEW TICKET CREATION PAGE
// ============================================

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { createTicket } from '@/lib/ticket-service';
import { Button, Input, Select, Card, CardHeader, CardTitle, CardContent } from '@/components/ui';
import { Ticket, TicketPriority, SAPModule } from '@/types';

const priorityOptions = [
    { value: 'Low', label: 'Low' },
    { value: 'Medium', label: 'Medium' },
    { value: 'High', label: 'High' },
    { value: 'Critical', label: 'Critical' },
];

const categoryOptions = [
    { value: 'MM', label: 'MM - Materials Management' },
    { value: 'SD', label: 'SD - Sales & Distribution' },
    { value: 'FICO', label: 'FICO - Finance & Controlling' },
    { value: 'PP', label: 'PP - Production Planning' },
    { value: 'HCM', label: 'HCM - Human Capital Management' },
    { value: 'WM', label: 'WM - Warehouse Management' },
    { value: 'QM', label: 'QM - Quality Management' },
    { value: 'PM', label: 'PM - Plant Maintenance' },
    { value: 'PS', label: 'PS - Project System' },
    { value: 'Other', label: 'Other' },
];

export default function NewTicketPage() {
    const router = useRouter();
    const { user } = useAuth();
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        priority: 'Medium' as TicketPriority,
        category: 'Other' as SAPModule,
        completionBy: '',
    });
    const [errors, setErrors] = useState<Record<string, string>>({});

    const handleInputChange = (field: string, value: string) => {
        setFormData(prev => ({ ...prev, [field]: value }));
        // Clear error when user starts typing
        if (errors[field]) {
            setErrors(prev => ({ ...prev, [field]: '' }));
        }
    };

    const validateForm = () => {
        const newErrors: Record<string, string> = {};

        if (!formData.title.trim()) {
            newErrors.title = 'Title is required';
        } else if (formData.title.length < 5) {
            newErrors.title = 'Title must be at least 5 characters';
        }

        if (!formData.description.trim()) {
            newErrors.description = 'Description is required';
        } else if (formData.description.length < 10) {
            newErrors.description = 'Description must be at least 10 characters';
        }

        if (!formData.completionBy) {
            newErrors.completionBy = 'Completion date is required';
        } else {
            const selectedDate = new Date(formData.completionBy);
            const today = new Date();
            today.setHours(0, 0, 0, 0);

            if (selectedDate < today) {
                newErrors.completionBy = 'Completion date cannot be in the past';
            }
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        setIsSubmitting(true);

        try {
            const { category, ...formDataWithoutCategory } = formData;
            const ticketData = {
                ...formDataWithoutCategory,
                module: category,
                assignedTo: user?.name || 'Unassigned',
                raisedBy: user?.name || 'Unknown',
                createdBy: user?.name || 'Unknown',
            };

            const response = await createTicket(ticketData);

            if (response.success && response.data) {
                router.push(`/tickets/${response.data.id}`);
            } else {
                setErrors({ submit: response.error || 'Failed to create ticket' });
            }
        } catch (error) {
            setErrors({ submit: 'An unexpected error occurred' });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto space-y-6">
            {/* Page Header */}
            <div className="flex items-center gap-4">
                <Link
                    href="/tickets"
                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                </Link>
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Create New Ticket</h1>
                    <p className="text-gray-500 mt-1">
                        Fill in the details below to create a new support ticket
                    </p>
                </div>
            </div>

            {/* Form */}
            <Card>
                <CardHeader>
                    <CardTitle>Ticket Information</CardTitle>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="space-y-6">
                        {/* Title */}
                        <div>
                            <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
                                Title *
                            </label>
                            <Input
                                id="title"
                                type="text"
                                placeholder="Brief description of the issue"
                                value={formData.title}
                                onChange={(e) => handleInputChange('title', e.target.value)}
                                error={errors.title}
                                maxLength={200}
                            />
                        </div>

                        {/* Description */}
                        <div>
                            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                                Description *
                            </label>
                            <textarea
                                id="description"
                                rows={6}
                                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-[#D04A02] focus:border-transparent resize-vertical ${
                                    errors.description ? 'border-red-300' : 'border-gray-300'
                                }`}
                                placeholder="Detailed description of the issue, steps to reproduce, expected behavior, etc."
                                value={formData.description}
                                onChange={(e) => handleInputChange('description', e.target.value)}
                                maxLength={2000}
                            />
                            {errors.description && (
                                <p className="mt-1 text-sm text-red-600">{errors.description}</p>
                            )}
                        </div>

                        {/* Priority and Category */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                                <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-2">
                                    Priority *
                                </label>
                                <Select
                                    id="priority"
                                    options={priorityOptions}
                                    value={formData.priority}
                                    onChange={(e) => handleInputChange('priority', e.target.value)}
                                    placeholder="Select priority"
                                />
                            </div>

                            <div>
                                <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
                                    SAP Module *
                                </label>
                                <Select
                                    id="category"
                                    options={categoryOptions}
                                    value={formData.category}
                                    onChange={(e) => handleInputChange('category', e.target.value)}
                                    placeholder="Select SAP module"
                                />
                            </div>
                        </div>

                        {/* Completion Date */}
                        <div>
                            <label htmlFor="completionBy" className="block text-sm font-medium text-gray-700 mb-2">
                                Target Completion Date *
                            </label>
                            <Input
                                id="completionBy"
                                type="date"
                                value={formData.completionBy}
                                onChange={(e) => handleInputChange('completionBy', e.target.value)}
                                error={errors.completionBy}
                                min={new Date().toISOString().split('T')[0]}
                            />
                        </div>

                        {/* Submit Error */}
                        {errors.submit && (
                            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                                <p className="text-sm text-red-600">{errors.submit}</p>
                            </div>
                        )}

                        {/* Form Actions */}
                        <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
                            <Link href="/tickets">
                                <Button type="button" variant="outline">
                                    Cancel
                                </Button>
                            </Link>
                            <Button
                                type="submit"
                                isLoading={isSubmitting}
                                disabled={isSubmitting}
                            >
                                {isSubmitting ? 'Creating Ticket...' : 'Create Ticket'}
                            </Button>
                        </div>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}