'use client';

import { useState } from 'react';
import { Search, AlertTriangle, CheckCircle, ExternalLink } from 'lucide-react';

interface SanctionsResult {
    id: string;
    name: string;
    regime: string;
    designated_by: string;
    listed_date: string;
    source_url: string;
}

interface APIResponse {
    success: boolean;
    query: string;
    count: number;
    data: SanctionsResult[];
    warning: string | null;
}

export default function SanctionsPage() {
    const [searchName, setSearchName] = useState('');
    const [results, setResults] = useState<SanctionsResult[]>([]);
    const [searched, setSearched] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSearch = async () => {
        if (searchName.length < 2) return;

        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`/api/sanctions?name=${encodeURIComponent(searchName)}`);
            const data: APIResponse = await response.json();

            if (data.success) {
                setResults(data.data);
                setSearched(true);
            } else {
                throw new Error('Search failed');
            }
        } catch (err) {
            setError('Failed to search. Please try again.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <header className="bg-white border-b">
                <div className="max-w-3xl mx-auto px-4 py-6">
                    <h1 className="text-2xl font-bold text-gray-900">
                        UK Sanctions List Checker
                    </h1>
                    <p className="mt-1 text-gray-600">
                        Check names against the OFSI consolidated sanctions list
                    </p>
                </div>
            </header>

            <main className="max-w-3xl mx-auto px-4 py-8">
                {/* Warning banner */}
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                    <div className="flex gap-3">
                        <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                        <div className="text-sm text-yellow-800">
                            <p className="font-medium">For informational purposes only</p>
                            <p className="mt-1">
                                This tool searches a copy of the OFSI list. Always verify matches against the
                                {' '}
                                <a
                                    href="https://www.gov.uk/government/publications/financial-sanctions-consolidated-list-of-targets"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="underline"
                                >
                                    official OFSI consolidated list
                                </a>
                                {' '}
                                before taking action.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Search box */}
                <div className="bg-white rounded-lg shadow p-6 mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Enter name to check
                    </label>
                    <div className="flex gap-3">
                        <div className="relative flex-1">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
                            <input
                                type="text"
                                value={searchName}
                                onChange={(e) => setSearchName(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder="Individual or organisation name..."
                                className="w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-lg"
                            />
                        </div>
                        <button
                            onClick={handleSearch}
                            disabled={searchName.length < 2 || loading}
                            className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? 'Checking...' : 'Check'}
                        </button>
                    </div>
                    <p className="mt-2 text-sm text-gray-500">
                        Enter at least 2 characters. Partial matches will be shown.
                    </p>
                </div>

                {/* Error */}
                {error && (
                    <div className="bg-red-50 text-red-700 p-4 rounded-lg mb-6">
                        {error}
                    </div>
                )}

                {/* Results */}
                {searched && (
                    <div className="bg-white rounded-lg shadow">
                        {results.length === 0 ? (
                            <div className="p-8 text-center">
                                <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
                                <h3 className="text-lg font-medium text-gray-900 mb-2">
                                    No matches found
                                </h3>
                                <p className="text-gray-600">
                                    "{searchName}" does not appear on the UK sanctions list.
                                </p>
                                <p className="text-sm text-gray-500 mt-4">
                                    This does not guarantee the name is not sanctioned.
                                    Verify with the official OFSI list.
                                </p>
                            </div>
                        ) : (
                            <div>
                                <div className="p-4 border-b bg-red-50">
                                    <div className="flex items-center gap-2 text-red-700">
                                        <AlertTriangle className="w-5 h-5" />
                                        <span className="font-medium">
                                            {results.length} potential match{results.length > 1 ? 'es' : ''} found
                                        </span>
                                    </div>
                                </div>

                                <div className="divide-y">
                                    {results.map(result => (
                                        <div key={result.id} className="p-4">
                                            <div className="flex items-start justify-between">
                                                <div>
                                                    <h4 className="font-medium text-gray-900">
                                                        {result.name}
                                                    </h4>
                                                    <div className="mt-1 text-sm text-gray-600 space-y-1">
                                                        <p>Regime: {result.regime || 'Not specified'}</p>
                                                        <p>Designated by: {result.designated_by || 'UK'}</p>
                                                        <p>Listed: {result.listed_date}</p>
                                                    </div>
                                                </div>
                                                <a
                                                    href={result.source_url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="text-blue-600 hover:text-blue-800"
                                                >
                                                    <ExternalLink className="w-4 h-4" />
                                                </a>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </main>
        </div>
    );
}
