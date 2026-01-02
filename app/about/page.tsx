import { Shield, Database, Search, BarChart3, Globe, Lock } from 'lucide-react';

export default function AboutPage() {
    return (
        <div className="min-h-screen bg-gray-50">
            {/* Hero Section */}
            <div className="bg-white border-b">
                <div className="max-w-4xl mx-auto px-4 py-16 text-center">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">About Charity Compliance Tracker</h1>
                    <p className="text-xl text-gray-600">
                        A comprehensive regtech explorer designed to bring transparency and clarity to the UK charity regulatory landscape.
                    </p>
                </div>
            </div>

            <div className="max-w-4xl mx-auto px-4 py-12">
                {/* Mission Statement */}
                <div className="prose prose-blue max-w-none mb-16">
                    <h2 className="text-2xl font-bold text-gray-900 mb-4 text-center">Our Mission</h2>
                    <p className="text-lg text-gray-700 text-center italic">
                        "To empower trustees, donors, and the public by centralizing and enriching regulatory data from multiple UK authorities into a single, searchable intelligence platform."
                    </p>
                </div>

                {/* Core Pillars */}
                <div className="grid md:grid-cols-2 gap-8 mb-16">
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <Database className="w-8 h-8 text-blue-600 mb-4" />
                        <h3 className="text-lg font-bold text-gray-900 mb-2">Aggregated Data</h3>
                        <p className="text-gray-600">
                            We collect data from the Charity Commission, ICO, HMRC, and other UK regulators. Instead of searching multiple portals, you find everything here.
                        </p>
                    </div>
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <Shield className="w-8 h-8 text-green-600 mb-4" />
                        <h3 className="text-lg font-bold text-gray-900 mb-2">Live Enrichment</h3>
                        <p className="text-gray-600">
                            Our system integrates directly with the Charity Commission Register API to provide live status, income metrics, and geographic data for every charity case.
                        </p>
                    </div>
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <Search className="w-8 h-8 text-purple-600 mb-4" />
                        <h3 className="text-lg font-bold text-gray-900 mb-2">Advanced Search</h3>
                        <p className="text-gray-600">
                            Filter by regulatory domain, document type, income band, or region. Our unified schema makes cross-regulator comparison simple.
                        </p>
                    </div>
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <BarChart3 className="w-8 h-8 text-orange-600 mb-4" />
                        <h3 className="text-lg font-bold text-gray-900 mb-2">Regulatory Insights</h3>
                        <p className="text-gray-600">
                            Our analytics dashboard visualizes trends in regulatory activity, helping you understand emerging risks in the sector.
                        </p>
                    </div>
                </div>

                {/* Understanding Document Types */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 mb-16">
                    <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Understanding Content Types</h2>
                    <div className="grid md:grid-cols-2 gap-12">
                        <div>
                            <div className="flex items-center mb-4">
                                <span className="w-4 h-4 bg-blue-100 border border-blue-200 rounded-full mr-2"></span>
                                <h3 className="text-xl font-bold text-blue-800">Guidance</h3>
                            </div>
                            <p className="text-gray-700 leading-relaxed">
                                <strong>Guidance</strong> documents are proactive, educational resources published by regulators. They outline <em>how</em> charities should operate to stay compliant.
                            </p>
                            <ul className="mt-4 space-y-2 text-sm text-gray-600">
                                <li className="flex items-start">
                                    <span className="text-blue-500 mr-2">•</span>
                                    Explains legal requirements and best practices.
                                </li>
                                <li className="flex items-start">
                                    <span className="text-blue-500 mr-2">•</span>
                                    Applicable to all charities within a specific domain.
                                </li>
                                <li className="flex items-start">
                                    <span className="text-blue-500 mr-2">•</span>
                                    Focuses on prevention and healthy governance.
                                </li>
                            </ul>
                        </div>
                        <div>
                            <div className="flex items-center mb-4">
                                <span className="w-4 h-4 bg-green-100 border border-green-200 rounded-full mr-2"></span>
                                <h3 className="text-xl font-bold text-green-800">Inquiry Case</h3>
                            </div>
                            <p className="text-gray-700 leading-relaxed">
                                <strong>Inquiry Cases</strong> are reactive reports following a formal investigation into a specific charity. They detail <em>what went wrong</em> and the lessons learned.
                            </p>
                            <ul className="mt-4 space-y-2 text-sm text-gray-600">
                                <li className="flex items-start">
                                    <span className="text-green-500 mr-2">•</span>
                                    Details specific failures in governance or finance.
                                </li>
                                <li className="flex items-start">
                                    <span className="text-green-500 mr-2">•</span>
                                    Enriched with live metadata for the investigated charity.
                                </li>
                                <li className="flex items-start">
                                    <span className="text-green-500 mr-2">•</span>
                                    Focuses on accountability and corrective actions.
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>

                {/* Data Sources Section */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 mb-16">
                    <h2 className="text-2xl font-bold text-gray-900 mb-6">Data & Transparency</h2>
                    <div className="space-y-6">
                        <div className="flex items-start">
                            <div className="bg-blue-50 p-3 rounded-lg mr-4">
                                <Globe className="w-6 h-6 text-blue-600" />
                            </div>
                            <div>
                                <h4 className="font-bold text-gray-900">Official Sources</h4>
                                <p className="text-gray-600 text-sm">
                                    All data is sourced directly from official UK Government publications, including GOV.UK, the Charity Commission, and the Information Commissioner's Office.
                                </p>
                            </div>
                        </div>
                        <div className="flex items-start">
                            <div className="bg-green-50 p-3 rounded-lg mr-4">
                                <Lock className="w-6 h-6 text-green-600" />
                            </div>
                            <div>
                                <h4 className="font-bold text-gray-900">Integrity & Accuracy</h4>
                                <p className="text-gray-600 text-sm">
                                    We use custom scrapers and API adapters to ensure data is normalized correctly. We maintain high standards of data hygiene, including deduplication and date verification.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Footer info */}
                <div className="mt-16 pt-8 border-t border-gray-200 text-center text-gray-500 text-sm">
                </div>
            </div>
        </div>
    );
}
