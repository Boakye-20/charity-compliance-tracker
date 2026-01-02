import { NextRequest, NextResponse } from 'next/server';
import {
    getAllPolicies,
    filterPolicies,
    sortPolicies,
    paginatePolicies
} from '@/lib/policies';
import type { PolicyFilters, ComplianceDomain, Regulator, DocumentType } from '@/types/policy';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
    try {
        const { searchParams } = new URL(request.url);

        // Build filters from query params
        const filters: PolicyFilters = {};

        const search = searchParams.get('search');
        if (search) filters.search = search;

        const regulator = searchParams.get('regulator');
        if (regulator) {
            filters.regulator = regulator.split(',') as Regulator[];
        }

        const domain = searchParams.get('domain');
        if (domain) {
            filters.domain = domain.split(',') as ComplianceDomain[];
        }

        const documentType = searchParams.get('document_type');
        if (documentType) {
            filters.document_type = documentType.split(',') as DocumentType[];
        }

        const dateFrom = searchParams.get('date_from');
        if (dateFrom) filters.date_from = dateFrom;

        const dateTo = searchParams.get('date_to');
        if (dateTo) filters.date_to = dateTo;

        const casesOnly = searchParams.get('cases_only');
        if (casesOnly === 'true') filters.has_case_id = true;

        const riskLevel = searchParams.get('risk_level');
        if (riskLevel) filters.risk_level = riskLevel;

        // Pagination and sorting params
        const page = parseInt(searchParams.get('page') || '1', 10);
        const perPage = parseInt(searchParams.get('per_page') || '20', 10);
        const sortBy = (searchParams.get('sort_by') || 'published_date') as 'published_date' | 'last_updated' | 'title';
        const sortOrder = (searchParams.get('sort_order') || 'desc') as 'asc' | 'desc';

        // Process data
        let policies = getAllPolicies();
        policies = filterPolicies(policies, filters);
        policies = sortPolicies(policies, sortBy, sortOrder);
        const result = paginatePolicies(policies, page, perPage);

        return NextResponse.json({
            success: true,
            ...result,
            filters: {
                applied: filters,
                available: {
                    regulators: ['CC', 'ICO', 'OFSI', 'HSE', 'HMRC', 'FR'],
                    domains: [
                        'governance', 'safeguarding', 'gdpr', 'health_safety',
                        'financial_reporting', 'risk_management', 'anti_fraud', 'sanctions'
                    ],
                    document_types: ['guidance', 'case', 'enforcement', 'regulation', 'alert', 'sanction']
                }
            }
        });

    } catch (error) {
        console.error('Policies API error:', error);
        return NextResponse.json(
            { success: false, error: 'Failed to fetch policies' },
            { status: 500 }
        );
    }
}
