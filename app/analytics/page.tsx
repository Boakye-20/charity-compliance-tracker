'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface AnalyticsData {
    summary: {
        total_records: number;
        case_records: number;
        guidance_records: number;
        last_updated: string;
    };
    time_series: {
        by_month_domain: Array<{ month: string; domain: string; count: number }>;
        by_month_regulator: Array<{ month: string; regulator: string; count: number }>;
    };
    breakdowns: {
        by_regulator: Array<{ regulator: string; count: number }>;
        by_domain: Array<{ domain: string; count: number }>;
        by_document_type: Array<{ type: string; count: number }>;
        by_income_band: Array<{ band: string; count: number }>;
        by_status: Array<{ status: string; count: number }>;
        by_region: Array<{ region: string; count: number }>;
    };
    keywords: Record<string, Array<{ keyword: string; count: number }>>;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#FF6B9D'];

const DOMAIN_COLORS: Record<string, string> = {
    governance: '#3B82F6',
    safeguarding: '#EF4444',
    gdpr: '#8B5CF6',
    financial_reporting: '#10B981',
    anti_fraud: '#F59E0B',
    health_safety: '#EC4899',
    risk_management: '#6366F1',
    sanctions: '#DC2626',
};

export default function AnalyticsPage() {
    const [data, setData] = useState<AnalyticsData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetch('/data/analytics.json')
            .then(res => {
                if (!res.ok) throw new Error('Analytics data not found');
                return res.json();
            })
            .then(setData)
            .catch(err => setError(err.message))
            .finally(() => setLoading(false));
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Loading analytics...</p>
                </div>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="bg-red-50 text-red-700 p-6 rounded-lg max-w-md">
                    <h2 className="text-lg font-semibold mb-2">Analytics Not Available</h2>
                    <p className="text-sm mb-4">{error || 'Failed to load analytics data'}</p>
                    <p className="text-xs text-red-600">
                        Run <code className="bg-red-100 px-1 rounded">python3 python-scripts/build_analytics.py</code> to generate analytics.
                    </p>
                </div>
            </div>
        );
    }

    // Prepare time-series data (aggregate by month across all domains)
    const monthlyData = data.time_series.by_month_domain.reduce((acc, item) => {
        const existing = acc.find(d => d.month === item.month);
        if (existing) {
            existing.count += item.count;
            existing[item.domain] = (existing[item.domain] || 0) + item.count;
        } else {
            acc.push({ month: item.month, count: item.count, [item.domain]: item.count });
        }
        return acc;
    }, [] as any[]);

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <div className="bg-white border-b">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <h1 className="text-3xl font-bold text-gray-900">Compliance Analytics</h1>
                    <p className="mt-2 text-sm text-gray-600">
                        Insights from {data.summary.total_records} regulatory documents
                    </p>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div className="bg-white rounded-lg shadow p-6">
                        <div className="text-sm font-medium text-gray-600">Total Records</div>
                        <div className="mt-2 text-3xl font-bold text-gray-900">{data.summary.total_records}</div>
                    </div>
                    <div className="bg-white rounded-lg shadow p-6">
                        <div className="text-sm font-medium text-gray-600">Inquiry Cases</div>
                        <div className="mt-2 text-3xl font-bold text-indigo-600">{data.summary.case_records}</div>
                    </div>
                    <div className="bg-white rounded-lg shadow p-6">
                        <div className="text-sm font-medium text-gray-600">Guidance Documents</div>
                        <div className="mt-2 text-3xl font-bold text-green-600">{data.summary.guidance_records}</div>
                    </div>
                    <div className="bg-white rounded-lg shadow p-6">
                        <div className="text-sm font-medium text-gray-600">Regulators</div>
                        <div className="mt-2 text-3xl font-bold text-purple-600">{data.breakdowns.by_regulator.length}</div>
                    </div>
                </div>

                {/* Time Series Chart */}
                <div className="bg-white rounded-lg shadow p-6 mb-8">
                    <h2 className="text-xl font-semibold text-gray-900 mb-4">Inquiries Over Time</h2>
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={monthlyData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="month" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey="count" stroke="#4F46E5" strokeWidth={2} name="Total" />
                        </LineChart>
                    </ResponsiveContainer>
                </div>

                {/* Two Column Layout */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                    {/* Regulator Breakdown */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h2 className="text-xl font-semibold text-gray-900 mb-4">By Regulator</h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={data.breakdowns.by_regulator}
                                    dataKey="count"
                                    nameKey="regulator"
                                    cx="50%"
                                    cy="50%"
                                    outerRadius={100}
                                    label
                                >
                                    {data.breakdowns.by_regulator.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Domain Breakdown */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h2 className="text-xl font-semibold text-gray-900 mb-4">By Compliance Domain</h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={data.breakdowns.by_domain}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="domain" angle={-45} textAnchor="end" height={100} />
                                <YAxis />
                                <Tooltip />
                                <Bar dataKey="count" fill="#4F46E5" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Income Band Distribution (if enriched) */}
                {data.breakdowns.by_income_band.length > 0 && (
                    <div className="bg-white rounded-lg shadow p-6 mb-8">
                        <h2 className="text-xl font-semibold text-gray-900 mb-4">Cases by Charity Income Band</h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={data.breakdowns.by_income_band}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="band" />
                                <YAxis />
                                <Tooltip />
                                <Bar dataKey="count" fill="#10B981" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                )}

                {/* Status Distribution (if enriched) */}
                {data.breakdowns.by_status.length > 0 && (
                    <div className="bg-white rounded-lg shadow p-6 mb-8">
                        <h2 className="text-xl font-semibold text-gray-900 mb-4">Charity Status Distribution</h2>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            {data.breakdowns.by_status.map((item, idx) => (
                                <div key={idx} className="bg-gray-50 rounded p-4">
                                    <div className="text-sm text-gray-600">{item.status || 'Unknown'}</div>
                                    <div className="text-2xl font-bold text-gray-900 mt-1">{item.count}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Top Regions (if enriched) */}
                {data.breakdowns.by_region.length > 0 && (
                    <div className="bg-white rounded-lg shadow p-6 mb-8">
                        <h2 className="text-xl font-semibold text-gray-900 mb-4">Top Regions</h2>
                        <div className="space-y-2">
                            {data.breakdowns.by_region.map((item, idx) => (
                                <div key={idx} className="flex items-center justify-between py-2 border-b">
                                    <span className="text-gray-700">{item.region}</span>
                                    <span className="font-semibold text-gray-900">{item.count}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Keywords by Year */}
                {Object.keys(data.keywords).length > 0 && (
                    <div className="bg-white rounded-lg shadow p-6">
                        <h2 className="text-xl font-semibold text-gray-900 mb-4">Trending Keywords</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {Object.entries(data.keywords).reverse().slice(0, 3).map(([year, keywords]) => (
                                <div key={year}>
                                    <h3 className="font-semibold text-gray-700 mb-3">{year}</h3>
                                    <div className="flex flex-wrap gap-2">
                                        {keywords.slice(0, 10).map((kw, idx) => (
                                            <span
                                                key={idx}
                                                className="inline-block bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded"
                                            >
                                                {kw.keyword} ({kw.count})
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
