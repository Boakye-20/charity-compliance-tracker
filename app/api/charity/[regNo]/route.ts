import { NextResponse } from 'next/server';
import { getAllPolicies } from '@/lib/policies';

export async function GET(
    request: Request,
    { params }: { params: { regNo: string } }
) {
    try {
        const policies = getAllPolicies();

        // Filter policies for this charity
        const charityPolicies = policies.filter(p => {
            // Match by charity_number or cc_registered_number
            return (
                p.charity_number === params.regNo ||
                p.cc_registered_number === params.regNo
            );
        });

        // Get unique charity info from first matching policy
        const charityInfo = charityPolicies.length > 0 ? {
            charity_number: charityPolicies[0].charity_number || charityPolicies[0].cc_registered_number,
            charity_name: charityPolicies[0].charity_name,
            cc_status: charityPolicies[0].cc_status,
            cc_latest_income: charityPolicies[0].cc_latest_income,
            cc_primary_region: charityPolicies[0].cc_primary_region,
            cc_governing_document: charityPolicies[0].cc_governing_document,
        } : null;

        return NextResponse.json({
            success: true,
            charity: charityInfo,
            policies: charityPolicies,
            total: charityPolicies.length,
        });
    } catch (error) {
        console.error('Error fetching charity data:', error);
        return NextResponse.json(
            { success: false, error: 'Failed to fetch charity data' },
            { status: 500 }
        );
    }
}
