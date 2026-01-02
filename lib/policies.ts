import fs from 'fs';
import path from 'path';
import { parse } from 'csv-parse/sync';
import type { CharityPolicy, PolicyFilters, ComplianceDomain, Regulator, DocumentType } from '@/types/policy';

const DATA_PATH = path.join(process.cwd(), 'data', 'charity_policies.csv');

/**
 * Load all policies from CSV.
 * Caches in memory for the duration of the serverless function.
 */
export function getAllPolicies(): CharityPolicy[] {
    if (!fs.existsSync(DATA_PATH)) {
        console.warn('Policy data file not found:', DATA_PATH);
        return [];
    }

    const fileContent = fs.readFileSync(DATA_PATH, 'utf-8');

    const records = parse(fileContent, {
        columns: true,
        skip_empty_lines: true,
        trim: true,
    });

    return records.map((row: Record<string, string>) => ({
        id: row.id,
        title: row.title,
        summary: row.summary,
        source_url: row.source_url,
        published_date: row.published_date,
        last_updated: row.last_updated,
        regulator: row.regulator as Regulator,
        domain: row.domain as ComplianceDomain,
        document_type: row.document_type as DocumentType,
        charity_number: row.charity_number || undefined,
        charity_name: row.charity_name || undefined,
        charity_income_band: row.charity_income_band as CharityPolicy['charity_income_band'] || undefined,
        risk_level: row.risk_level as CharityPolicy['risk_level'] || undefined,
        case_id: row.case_id || undefined,
        case_status: row.case_status as CharityPolicy['case_status'] || undefined,
        outcome: row.outcome || undefined,
        issues_identified: row.issues_identified ? row.issues_identified.split('|') : undefined,
        sanctions_regime: row.sanctions_regime || undefined,
        designated_by: row.designated_by || undefined,
        fine_amount: row.fine_amount ? parseFloat(row.fine_amount) : undefined,
        keywords: row.keywords ? row.keywords.split('|') : undefined,
        cc_registered_number: row.cc_registered_number || undefined,
        cc_suffix: row.cc_suffix || undefined,
        cc_status: row.cc_status || undefined,
        cc_latest_income: row.cc_latest_income ? parseFloat(row.cc_latest_income) : undefined,
        cc_governing_document: row.cc_governing_document || undefined,
        cc_primary_region: row.cc_primary_region || undefined,
    }));
}

/**
 * Filter policies based on query parameters.
 */
export function filterPolicies(
    policies: CharityPolicy[],
    filters: PolicyFilters
): CharityPolicy[] {
    let result = [...policies];

    // Text search across title, summary, charity name
    if (filters.search) {
        const searchLower = filters.search.toLowerCase();
        result = result.filter(p =>
            p.title.toLowerCase().includes(searchLower) ||
            p.summary.toLowerCase().includes(searchLower) ||
            (p.charity_name && p.charity_name.toLowerCase().includes(searchLower)) ||
            (p.keywords && p.keywords.some(k => k.toLowerCase().includes(searchLower)))
        );
    }

    // Regulator filter
    if (filters.regulator) {
        const regulators = Array.isArray(filters.regulator)
            ? filters.regulator
            : [filters.regulator];
        result = result.filter(p => regulators.includes(p.regulator));
    }

    // Domain filter
    if (filters.domain) {
        const domains = Array.isArray(filters.domain)
            ? filters.domain
            : [filters.domain];
        result = result.filter(p => domains.includes(p.domain));
    }

    // Document type filter
    if (filters.document_type) {
        const types = Array.isArray(filters.document_type)
            ? filters.document_type
            : [filters.document_type];
        result = result.filter(p => types.includes(p.document_type));
    }

    // Date range filters
    if (filters.date_from) {
        result = result.filter(p => p.published_date >= filters.date_from!);
    }
    if (filters.date_to) {
        result = result.filter(p => p.published_date <= filters.date_to!);
    }

    // Cases only filter
    if (filters.has_case_id) {
        result = result.filter(
            p =>
                p.case_id ||
                p.document_type === 'case' ||
                p.document_type === 'enforcement'
        );
    }

    // Risk level filter
    if (filters.risk_level) {
        result = result.filter(p => p.risk_level === filters.risk_level);
    }

    return result;
}

/**
 * Sort policies by field.
 */
export function sortPolicies(
    policies: CharityPolicy[],
    sortBy: 'published_date' | 'last_updated' | 'title' = 'published_date',
    order: 'asc' | 'desc' = 'desc'
): CharityPolicy[] {
    return [...policies].sort((a, b) => {
        let comparison = 0;

        if (sortBy === 'title') {
            comparison = a.title.localeCompare(b.title);
        } else {
            comparison = a[sortBy].localeCompare(b[sortBy]);
        }

        return order === 'desc' ? -comparison : comparison;
    });
}

/**
 * Paginate results.
 */
export function paginatePolicies(
    policies: CharityPolicy[],
    page: number = 1,
    perPage: number = 20
): { data: CharityPolicy[]; total: number; page: number; totalPages: number } {
    const total = policies.length;
    const totalPages = Math.ceil(total / perPage);
    const start = (page - 1) * perPage;
    const data = policies.slice(start, start + perPage);

    return { data, total, page, totalPages };
}
