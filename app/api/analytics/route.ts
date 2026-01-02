import { NextResponse } from 'next/server';
import { getAllPolicies } from '@/lib/policies';
import type { CharityPolicy, ComplianceDomain, Regulator } from '@/types/policy';

export const dynamic = 'force-dynamic';

export async function GET() {
    try {
        const policies = getAllPolicies();

        // Count by regulator
        const byRegulator: Record<Regulator, number> = {
            CC: 0, ICO: 0, OFSI: 0, HSE: 0, HMRC: 0, FR: 0
        };

        // Count by domain
        const byDomain: Record<ComplianceDomain, number> = {
            governance: 0,
            safeguarding: 0,
            gdpr: 0,
            health_safety: 0,
            financial_reporting: 0,
            risk_management: 0,
            anti_fraud: 0,
            sanctions: 0
        };

        // Count by document type
        const byType: Record<string, number> = {
            guidance: 0,
            case: 0,
            enforcement: 0,
            regulation: 0,
            alert: 0,
            sanction: 0
        };

        // Timeline data (last 12 months)
        const timeline: Record<string, number> = {};
        const now = new Date();
        for (let i = 11; i >= 0; i--) {
            const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
            const key = d.toISOString().slice(0, 7); // YYYY-MM
            timeline[key] = 0;
        }

        // Process each policy
        policies.forEach(p => {
            // By regulator
            if (p.regulator in byRegulator) {
                byRegulator[p.regulator]++;
            }

            // By domain
            if (p.domain in byDomain) {
                byDomain[p.domain]++;
            }

            // By type
            if (p.document_type in byType) {
                byType[p.document_type]++;
            }

            // Timeline
            const month = p.published_date.slice(0, 7);
            if (month in timeline) {
                timeline[month]++;
            }
        });

        // Recent high-risk items
        const highRisk = policies
            .filter(p => p.risk_level === 'high' || p.risk_level === 'critical')
            .sort((a, b) => b.published_date.localeCompare(a.published_date))
            .slice(0, 10);

        return NextResponse.json({
            success: true,
            summary: {
                total: policies.length,
                last_updated: policies.length > 0
                    ? Math.max(...policies.map(p => new Date(p.last_updated).getTime()))
                    : null
            },
            by_regulator: byRegulator,
            by_domain: byDomain,
            by_type: byType,
            timeline: Object.entries(timeline).map(([month, count]) => ({ month, count })),
            high_risk_recent: highRisk.map(p => ({
                id: p.id,
                title: p.title,
                domain: p.domain,
                risk_level: p.risk_level,
                date: p.published_date
            }))
        });

    } catch (error) {
        console.error('Analytics API error:', error);
        return NextResponse.json(
            { success: false, error: 'Failed to generate analytics' },
            { status: 500 }
        );
    }
}
