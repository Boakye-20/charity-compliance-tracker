'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, ExternalLink, Building2, TrendingUp, MapPin, FileText } from 'lucide-react';
import type { CharityPolicy } from '@/types/policy';

interface CharityData {
    charity: {
        charity_number?: string;
        charity_name?: string;
        cc_status?: string;
        cc_latest_income?: number;
        cc_primary_region?: string;
        cc_governing_document?: string;
    } | null;
    policies: CharityPolicy[];
    total: number;
}

const DOMAIN_COLORS: Record<string, string> = {
    governance: 'bg-blue-100 text-blue-800',
    safeguarding: 'bg-red-100 text-red-800',
    gdpr: 'bg-purple-100 text-purple-800',
    health_safety: 'bg-yellow-100 text-yellow-800',
    financial_reporting: 'bg-green-100 text-green-800',
    risk_management: 'bg-orange-100 text-orange-800',
    anti_fraud: 'bg-pink-100 text-pink-800',
    sanctions: 'bg-gray-100 text-gray-800'
};

export default function CharityProfilePage() {
    const params = useParams();
    const regNo = params.regNo as string;

    const [data, setData] = useState<CharityData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetch(`/api/charity/${regNo}`)
            .then(res => {
                if (!res.ok) throw new Error('Failed to fetch charity data');
                return res.json();
            })
            .then(setData)
            .catch(err => setError(err.message))
            .finally(() => setLoading(false));
    }, [regNo]);

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Loading charity profile...</p>
                </div>
            </div>
        );
    }

    if (error || !data || !data.charity) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="bg-red-50 text-red-700 p-6 rounded-lg max-w-md">
                    <h2 className="text-lg font-semibold mb-2">Charity Not Found</h2>
                    <p className="text-sm mb-4">{error || 'No data available for this charity'}</p>
                    <Link href="/explorer" className="text-sm text-red-600 hover:text-red-800 underline">
                        ← Back to Explorer
                    </Link>
                </div>
            </div>
        );
    }

    const { charity, policies } = data;
    const formatIncome = (income?: number) => {
        if (!income) return 'N/A';
        if (income >= 1_000_000) return `£${(income / 1_000_000).toFixed(1)}m`;
        if (income >= 1_000) return `£${(income / 1_000).toFixed(0)}k`;
        return `£${income}`;
    };

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <div className="bg-white border-b">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <Link href="/explorer" className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4">
                        <ArrowLeft className="w-4 h-4 mr-1" />
                        Back to Explorer
                    </Link>

                    <div className="flex items-start justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">{charity.charity_name || 'Unknown Charity'}</h1>
                            <p className="mt-2 text-sm text-gray-600">Charity Number: {charity.charity_number || regNo}</p>
                        </div>

                        {charity.cc_status && (
                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${charity.cc_status === 'Registered'
                                    ? 'bg-green-100 text-green-800'
                                    : 'bg-gray-100 text-gray-800'
                                }`}>
                                {charity.cc_status}
                            </span>
                        )}
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Overview Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    {charity.cc_latest_income && (
                        <div className="bg-white rounded-lg shadow p-6">
                            <div className="flex items-center">
                                <TrendingUp className="w-5 h-5 text-green-600 mr-2" />
                                <div className="text-sm font-medium text-gray-600">Latest Income</div>
                            </div>
                            <div className="mt-2 text-2xl font-bold text-gray-900">
                                {formatIncome(charity.cc_latest_income)}
                            </div>
                        </div>
                    )}

                    {charity.cc_primary_region && (
                        <div className="bg-white rounded-lg shadow p-6">
                            <div className="flex items-center">
                                <MapPin className="w-5 h-5 text-blue-600 mr-2" />
                                <div className="text-sm font-medium text-gray-600">Primary Region</div>
                            </div>
                            <div className="mt-2 text-lg font-semibold text-gray-900">
                                {charity.cc_primary_region}
                            </div>
                        </div>
                    )}

                    {charity.cc_governing_document && (
                        <div className="bg-white rounded-lg shadow p-6">
                            <div className="flex items-center">
                                <FileText className="w-5 h-5 text-purple-600 mr-2" />
                                <div className="text-sm font-medium text-gray-600">Governing Document</div>
                            </div>
                            <div className="mt-2 text-lg font-semibold text-gray-900">
                                {charity.cc_governing_document}
                            </div>
                        </div>
                    )}
                </div>

                {/* Compliance Timeline */}
                <div className="bg-white rounded-lg shadow">
                    <div className="px-6 py-4 border-b">
                        <h2 className="text-xl font-semibold text-gray-900">
                            Compliance History ({policies.length} {policies.length === 1 ? 'record' : 'records'})
                        </h2>
                    </div>

                    <div className="p-6">
                        {policies.length === 0 ? (
                            <p className="text-gray-600 text-center py-8">No compliance records found for this charity.</p>
                        ) : (
                            <div className="space-y-4">
                                {policies.map(policy => (
                                    <div key={policy.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                                        <div className="flex items-start justify-between mb-2">
                                            <div className="flex-1">
                                                <h3 className="font-semibold text-gray-900">{policy.title}</h3>
                                                <p className="text-sm text-gray-600 mt-1">{policy.summary}</p>
                                            </div>
                                            <a
                                                href={policy.source_url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="ml-4 text-indigo-600 hover:text-indigo-800"
                                            >
                                                <ExternalLink className="w-5 h-5" />
                                            </a>
                                        </div>

                                        <div className="flex flex-wrap gap-2 mt-3">
                                            <span className={`px-2 py-1 rounded text-xs font-medium ${DOMAIN_COLORS[policy.domain]}`}>
                                                {policy.domain}
                                            </span>
                                            <span className="px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700">
                                                {policy.document_type}
                                            </span>
                                            {policy.published_date && (
                                                <span className="px-2 py-1 rounded text-xs text-gray-600">
                                                    {policy.published_date}
                                                </span>
                                            )}
                                            {policy.outcome && (
                                                <span className="px-2 py-1 rounded text-xs font-medium bg-amber-100 text-amber-800">
                                                    {policy.outcome}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
