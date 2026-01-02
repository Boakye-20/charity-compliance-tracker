import Link from 'next/link';
import { Search, FileText, Shield, BarChart3, ExternalLink } from 'lucide-react';

export default function HomePage() {
    return (
        <div className="flex flex-col min-h-screen">
            {/* Hero Section */}
            <div className="bg-gradient-to-r from-blue-800 to-indigo-900 text-white py-16">
                <div className="max-w-6xl mx-auto px-4">
                    <div className="text-center mb-8">
                        <h1 className="text-4xl md:text-5xl font-bold mb-4">
                            Charity Compliance Tracker
                        </h1>
                        <p className="text-xl text-blue-100 max-w-2xl mx-auto">
                            Monitor UK charity regulation with live data from the Charity Commission Register.
                            One place for guidance, inquiries, and compliance analytics.
                        </p>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="py-12 bg-gray-50 flex-grow">
                <div className="max-w-6xl mx-auto px-4">
                    {/* Feature cards */}
                    <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto mb-12">
                        <Link
                            href="/explorer"
                            className="block bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow border border-gray-100"
                        >
                            <Search className="w-8 h-8 text-blue-600 mb-3" />
                            <h2 className="text-lg font-semibold text-gray-900 mb-2">
                                Policy Explorer
                            </h2>
                            <p className="text-gray-600 text-sm">
                                Search across all charity guidance and inquiry cases.
                                Now with live charity income and status data.
                            </p>
                        </Link>

                        <Link
                            href="/analytics"
                            className="block bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow border border-gray-100"
                        >
                            <BarChart3 className="w-8 h-8 text-green-600 mb-3" />
                            <h2 className="text-lg font-semibold text-gray-900 mb-2">
                                Compliance Analytics
                            </h2>
                            <p className="text-gray-600 text-sm">
                                Visual insights into regulatory trends.
                                Monitor risk patterns and geographic distributions.
                            </p>
                        </Link>

                        <div
                            className="block bg-white rounded-lg shadow p-6 border border-gray-100"
                        >
                            <Shield className="w-8 h-8 text-indigo-600 mb-3" />
                            <h2 className="text-lg font-semibold text-gray-900 mb-2">
                                Live Enrichment
                            </h2>
                            <p className="text-gray-600 text-sm">
                                Direct integration with the Charity Commission Register API
                                for real-time charity health metrics.
                            </p>
                        </div>
                    </div>

                    {/* Source info section */}
                    <div className="bg-white rounded-lg shadow p-6 border border-gray-100 mb-8">
                        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                            <ExternalLink className="w-5 h-5 mr-2 text-blue-600" />
                            Data Sources
                        </h2>
                        <div className="grid md:grid-cols-2 gap-6">
                            <div>
                                <h3 className="font-medium text-gray-800 mb-2">Primary Regulators</h3>
                                <ul className="space-y-1">
                                    <li className="flex items-center text-sm text-gray-600">
                                        <span className="w-2 h-2 bg-blue-600 rounded-full mr-2"></span>
                                        Charity Commission (governance, safeguarding)
                                    </li>
                                    <li className="flex items-center text-sm text-gray-600">
                                        <span className="w-2 h-2 bg-purple-600 rounded-full mr-2"></span>
                                        Information Commissioner's Office (data protection)
                                    </li>
                                    <li className="flex items-center text-sm text-gray-600">
                                        <span className="w-2 h-2 bg-green-600 rounded-full mr-2"></span>
                                        OSCR & CCNI (regional regulators)
                                    </li>
                                </ul>
                            </div>
                            <div>
                                <h3 className="font-medium text-gray-800 mb-2">Content Types</h3>
                                <ul className="space-y-1">
                                    <li className="flex items-center text-sm text-gray-600">
                                        <span className="w-2 h-2 bg-indigo-600 rounded-full mr-2"></span>
                                        Official guidance documents
                                    </li>
                                    <li className="flex items-center text-sm text-gray-600">
                                        <span className="w-2 h-2 bg-yellow-600 rounded-full mr-2"></span>
                                        Enforcement cases and decisions
                                    </li>
                                    <li className="flex items-center text-sm text-gray-600">
                                        <span className="w-2 h-2 bg-orange-600 rounded-full mr-2"></span>
                                        Fundraising & advertising standards
                                    </li>
                                </ul>
                            </div>
                        </div>
                        <div className="mt-4 text-xs text-gray-500">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
