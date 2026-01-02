'use client';

import { useState, useEffect, useCallback } from 'react';
import { Search, Filter, ChevronLeft, ChevronRight, ExternalLink, Shield } from 'lucide-react';
import type { CharityPolicy, ComplianceDomain, Regulator, DocumentType } from '@/types/policy';

// Domain display configuration
const DOMAIN_LABELS: Record<ComplianceDomain, string> = {
    governance: 'Governance',
    safeguarding: 'Safeguarding',
    gdpr: 'Data Protection',
    health_safety: 'Health & Safety',
    financial_reporting: 'Financial',
    risk_management: 'Risk',
    anti_fraud: 'Anti-Fraud',
    sanctions: 'Sanctions'
};

const DOMAIN_COLORS: Record<ComplianceDomain, string> = {
    governance: 'bg-blue-100 text-blue-800',
    safeguarding: 'bg-red-100 text-red-800',
    gdpr: 'bg-purple-100 text-purple-800',
    health_safety: 'bg-yellow-100 text-yellow-800',
    financial_reporting: 'bg-green-100 text-green-800',
    risk_management: 'bg-orange-100 text-orange-800',
    anti_fraud: 'bg-pink-100 text-pink-800',
    sanctions: 'bg-gray-100 text-gray-800'
};

const DOCUMENT_TYPE_LABELS: Record<DocumentType, string> = {
    guidance: 'Guidance',
    case: 'Inquiry case',
    enforcement: 'Enforcement',
    regulation: 'Regulation',
    alert: 'Alert',
    sanction: 'Sanction',
};

const REGULATOR_LABELS: Record<Regulator, string> = {
    CC: 'Charity Commission',
    ICO: 'ICO',
    HMRC: 'HMRC',
    FR: 'Fundraising Regulator',
    OSCR: 'OSCR (Scotland)',
    CCNI: 'CCNI (Northern Ireland)',
    ASA: 'ASA',
    OFSI: 'OFSI',
    HSE: 'HSE'
};

interface APIResponse {
    success: boolean;
    data: CharityPolicy[];
    total: number;
    page: number;
    totalPages: number;
}

export default function ExplorerPage() {
    // State
    const [policies, setPolicies] = useState<CharityPolicy[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Filters
    const [search, setSearch] = useState('');
    const [selectedDomains, setSelectedDomains] = useState<ComplianceDomain[]>([]);
    const [selectedRegulators, setSelectedRegulators] = useState<Regulator[]>([]);
    const [selectedTypes, setSelectedTypes] = useState<DocumentType[]>([]);
    const [casesOnly, setCasesOnly] = useState(false);
    const [dateFrom, setDateFrom] = useState('');
    const [dateTo, setDateTo] = useState('');

    // Pagination
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [total, setTotal] = useState(0);
    const perPage = 20;

    // Fetch policies
    const fetchPolicies = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            const params = new URLSearchParams();

            if (search) params.set('search', search);
            if (selectedDomains.length) params.set('domain', selectedDomains.join(','));
            if (selectedRegulators.length) params.set('regulator', selectedRegulators.join(','));
            if (selectedTypes.length) params.set('document_type', selectedTypes.join(','));
            if (casesOnly) params.set('cases_only', 'true');
            if (dateFrom) params.set('date_from', dateFrom);
            if (dateTo) params.set('date_to', dateTo);
            params.set('page', String(page));
            params.set('per_page', String(perPage));

            const response = await fetch(`/api/policies?${params}`);
            const data: APIResponse = await response.json();

            if (data.success) {
                setPolicies(data.data);
                setTotal(data.total);
                setTotalPages(data.totalPages);
            } else {
                throw new Error('API returned error');
            }
        } catch (err) {
            setError('Failed to load policies. Please try again.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, [search, selectedDomains, selectedRegulators, selectedTypes, casesOnly, dateFrom, dateTo, page]);

    // Debounced search
    useEffect(() => {
        const timer = setTimeout(() => {
            setPage(1); // Reset to first page on filter change
            fetchPolicies();
        }, 300);

        return () => clearTimeout(timer);
    }, [search, selectedDomains, selectedRegulators, selectedTypes, casesOnly, dateFrom, dateTo]);

    // Fetch on page change (no debounce)
    useEffect(() => {
        fetchPolicies();
    }, [page, fetchPolicies]);

    // Toggle helpers
    const toggleDomain = (domain: ComplianceDomain) => {
        setSelectedDomains(prev =>
            prev.includes(domain)
                ? prev.filter(d => d !== domain)
                : [...prev, domain]
        );
    };

    const toggleRegulator = (reg: Regulator) => {
        setSelectedRegulators(prev =>
            prev.includes(reg)
                ? prev.filter(r => r !== reg)
                : [...prev, reg]
        );
    };

    const toggleType = (docType: DocumentType) => {
        setSelectedTypes(prev =>
            prev.includes(docType)
                ? prev.filter(t => t !== docType)
                : [...prev, docType]
        );
    };

    const clearFilters = () => {
        setSearch('');
        setSelectedDomains([]);
        setSelectedRegulators([]);
        setSelectedTypes([]);
        setCasesOnly(false);
        setDateFrom('');
        setDateTo('');
        setPage(1);
    };

    // Helper to determine if a date should be displayed
    const shouldShowDate = (date: string | undefined): boolean => {
        return !!date;
    };

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white border-b">
                <div className="max-w-7xl mx-auto px-4 py-6">
                    <h1 className="text-2xl font-bold text-gray-900">
                        Charity Compliance Policy Explorer
                    </h1>
                    <p className="mt-1 text-gray-600">
                        Search regulatory guidance, cases, and enforcement across UK charity regulators
                    </p>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-4 py-6">
                {/* Search bar */}
                <div className="bg-white rounded-lg shadow p-4 mb-6">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
                        <input
                            type="text"
                            placeholder="Search policies, cases, charities..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                    </div>
                </div>

                {/* Filters */}
                <div className="bg-white rounded-lg shadow p-4 mb-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2">
                            <Filter className="w-4 h-4 text-gray-500" />
                            <span className="font-medium text-gray-700">Filters</span>
                        </div>
                        <button
                            onClick={clearFilters}
                            className="text-sm text-blue-600 hover:text-blue-800"
                        >
                            Clear all
                        </button>
                    </div>

                    {/* Document type filters - Primary Section */}
                    <div className="mb-6 p-4 bg-indigo-50/50 rounded-lg border border-indigo-100">
                        <div className="text-sm font-bold text-indigo-900 mb-3 flex items-center">
                            <Shield className="w-4 h-4 mr-2" />
                            Primary Content Type
                        </div>
                        <div className="flex flex-wrap gap-3">
                            {(['guidance', 'case'] as DocumentType[]).map((type) => (
                                <button
                                    key={type}
                                    onClick={() => toggleType(type)}
                                    className={`flex-1 min-w-[140px] px-4 py-3 rounded-xl text-sm font-bold transition-all border-2 ${selectedTypes.includes(type)
                                        ? 'bg-indigo-600 text-white border-indigo-600 shadow-md transform scale-[1.02]'
                                        : 'bg-white text-gray-700 border-gray-200 hover:border-indigo-300 hover:bg-indigo-50/30'
                                        }`}
                                >
                                    <div className="flex flex-col items-center gap-1">
                                        <span className="text-base">
                                            {DOCUMENT_TYPE_LABELS[type] === 'Inquiry case' ? 'Inquiry Case' : DOCUMENT_TYPE_LABELS[type]}
                                        </span>
                                        <span className="text-[10px] font-medium opacity-80 uppercase tracking-wider">
                                            {type === 'guidance' ? 'Proactive Best Practice' : 'Reactive Investigation'}
                                        </span>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Domain filters */}
                        <div>
                            <div className="text-sm font-medium text-gray-600 mb-2">Compliance Domain</div>
                            <div className="flex flex-wrap gap-2">
                                {(Object.entries(DOMAIN_LABELS) as [ComplianceDomain, string][]).map(([key, label]) => (
                                    <button
                                        key={key}
                                        onClick={() => toggleDomain(key)}
                                        className={`px-3 py-1 rounded-full text-sm transition-colors ${selectedDomains.includes(key)
                                            ? DOMAIN_COLORS[key]
                                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                            }`}
                                    >
                                        {label}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Regulator filters */}
                        <div>
                            <div className="text-sm font-medium text-gray-600 mb-2">Regulator</div>
                            <div className="flex flex-wrap gap-2">
                                {(Object.entries(REGULATOR_LABELS) as [Regulator, string][]).map(([key, label]) => (
                                    <button
                                        key={key}
                                        onClick={() => toggleRegulator(key)}
                                        className={`px-3 py-1 rounded-full text-sm transition-colors ${selectedRegulators.includes(key)
                                            ? 'bg-blue-600 text-white'
                                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                            }`}
                                    >
                                        {label}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Date range */}
                    <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <div className="text-sm font-medium text-gray-600 mb-1">From date</div>
                            <input
                                type="date"
                                value={dateFrom}
                                onChange={e => setDateFrom(e.target.value)}
                                className="w-full border rounded px-2 py-1 text-sm"
                            />
                        </div>
                        <div>
                            <div className="text-sm font-medium text-gray-600 mb-1">To date</div>
                            <input
                                type="date"
                                value={dateTo}
                                onChange={e => setDateTo(e.target.value)}
                                className="w-full border rounded px-2 py-1 text-sm"
                            />
                        </div>
                    </div>
                </div>

                {/* Results count */}
                <div className="flex items-center justify-between mb-4">
                    <span className="text-gray-600">
                        {loading ? 'Loading...' : `${total} results`}
                    </span>
                </div>

                {/* Error state */}
                {error && (
                    <div className="bg-red-50 text-red-700 p-4 rounded-lg mb-6">
                        {error}
                    </div>
                )}

                {/* Results list */}
                <div className="space-y-4">
                    {policies.map(policy => (
                        <div key={policy.id} className="bg-white rounded-lg shadow p-4">
                            <div className="flex items-start justify-between">
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-2">
                                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${DOMAIN_COLORS[policy.domain]}`}>
                                            {DOMAIN_LABELS[policy.domain]}
                                        </span>
                                        <span className="text-xs text-gray-500">
                                            {REGULATOR_LABELS[policy.regulator]}
                                        </span>
                                        {policy.risk_level && (
                                            <span className={`px-2 py-0.5 rounded text-xs font-medium ${policy.risk_level === 'critical' ? 'bg-red-600 text-white' :
                                                policy.risk_level === 'high' ? 'bg-orange-500 text-white' :
                                                    'bg-gray-200 text-gray-700'
                                                }`}>
                                                {policy.risk_level}
                                            </span>
                                        )}
                                    </div>

                                    <h3 className="font-semibold text-gray-900 mb-1">
                                        {policy.title}
                                    </h3>

                                    <p className="text-sm text-gray-600 mb-2">
                                        {policy.summary}
                                    </p>

                                    <div className="flex flex-wrap items-center gap-3 text-xs text-gray-500">
                                        {/* Document type badge */}
                                        <span className={`px-2 py-0.5 rounded font-medium ${policy.document_type === 'guidance'
                                            ? 'bg-blue-100 text-blue-800'
                                            : 'bg-green-100 text-green-700'
                                            }`}>
                                            {policy.document_type === 'guidance' ? 'Guidance' : 'Inquiry Case'}
                                        </span>
                                        {shouldShowDate(policy.last_updated || policy.published_date) && (
                                            <span>{policy.last_updated || policy.published_date}</span>
                                        )}
                                        {policy.charity_name && (
                                            <span className="font-medium text-gray-700">
                                                {policy.charity_name}
                                                {policy.charity_number && (
                                                    <a
                                                        href={`/charity/${policy.charity_number}`}
                                                        className="ml-1 text-indigo-600 hover:text-indigo-800 underline"
                                                        onClick={(e) => e.stopPropagation()}
                                                    >
                                                        #{policy.charity_number}
                                                    </a>
                                                )}
                                            </span>
                                        )}
                                        {policy.cc_status && (
                                            <span className={`px-2 py-0.5 rounded ${policy.cc_status === 'Registered'
                                                ? 'bg-green-100 text-green-700'
                                                : 'bg-gray-100 text-gray-600'
                                                }`}>
                                                {policy.cc_status}
                                            </span>
                                        )}
                                        {policy.cc_latest_income && (
                                            <span className="text-gray-600">
                                                Income: £{policy.cc_latest_income >= 1_000_000
                                                    ? `${(policy.cc_latest_income / 1_000_000).toFixed(1)}m`
                                                    : policy.cc_latest_income >= 1_000
                                                        ? `${(policy.cc_latest_income / 1_000).toFixed(0)}k`
                                                        : policy.cc_latest_income}
                                            </span>
                                        )}
                                        {policy.cc_primary_region && (
                                            <span className="text-gray-600">📍 {policy.cc_primary_region}</span>
                                        )}
                                        {policy.fine_amount && (
                                            <span className="text-red-600 font-medium">
                                                Fine: £{policy.fine_amount.toLocaleString()}
                                            </span>
                                        )}
                                    </div>
                                </div>
                                <a
                                    href={policy.source_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="ml-4 text-blue-600 hover:text-blue-800"
                                >
                                    <ExternalLink className="w-4 h-4" />
                                </a>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Empty state */}
                {!loading && policies.length === 0 && (
                    <div className="text-center py-12 text-gray-500">
                        No policies found matching your filters.
                    </div>
                )}

                {/* Pagination */}
                {totalPages > 1 && (
                    <div className="flex items-center justify-center gap-4 mt-8">
                        <button
                            onClick={() => setPage(p => Math.max(1, p - 1))}
                            disabled={page === 1}
                            className="flex items-center gap-1 px-3 py-2 rounded border disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                        >
                            <ChevronLeft className="w-4 h-4" />
                            Previous
                        </button>

                        <span className="text-sm text-gray-600">
                            Page {page} of {totalPages}
                        </span>

                        <button
                            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                            disabled={page === totalPages}
                            className="flex items-center gap-1 px-3 py-2 rounded border disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                        >
                            Next
                            <ChevronRight className="w-4 h-4" />
                        </button>
                    </div>
                )}
            </main>
        </div>
    );
}
