import { NextRequest, NextResponse } from 'next/server';
import { getAllPolicies } from '@/lib/policies';

export const dynamic = 'force-dynamic';

/**
 * Specialized endpoint for sanctions name search.
 * Optimized for quick lookups against the OFSI list.
 */
export async function GET(request: NextRequest) {
    try {
        const { searchParams } = new URL(request.url);
        const name = searchParams.get('name');
        const regime = searchParams.get('regime');

        if (!name || name.length < 2) {
            return NextResponse.json({
                success: true,
                data: [],
                message: 'Provide at least 2 characters to search'
            });
        }

        // Get only sanctions entries
        const allPolicies = getAllPolicies();
        let sanctions = allPolicies.filter(p => p.domain === 'sanctions');

        // Search by name (case-insensitive, partial match)
        const nameLower = name.toLowerCase();
        let matches = sanctions.filter(s =>
            s.title.toLowerCase().includes(nameLower) ||
            (s.summary && s.summary.toLowerCase().includes(nameLower))
        );

        // Filter by regime if specified
        if (regime) {
            matches = matches.filter(s =>
                s.sanctions_regime?.toLowerCase().includes(regime.toLowerCase())
            );
        }

        // Format for response
        const results = matches.map(m => ({
            id: m.id,
            name: m.title.replace('Sanctions: ', ''),
            regime: m.sanctions_regime,
            designated_by: m.designated_by,
            listed_date: m.published_date,
            source_url: m.source_url
        }));

        return NextResponse.json({
            success: true,
            query: name,
            count: results.length,
            data: results.slice(0, 50),  // Limit to 50 results
            warning: results.length === 0 ? null :
                'This is for information only. Always verify against the official OFSI list.'
        });

    } catch (error) {
        console.error('Sanctions API error:', error);
        return NextResponse.json(
            { success: false, error: 'Failed to search sanctions' },
            { status: 500 }
        );
    }
}
