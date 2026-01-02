"use client";

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

// Thin wrapper: redirect /cases to /explorer with cases-only filter instructions
export default function CasesPage() {
    const router = useRouter();

    useEffect(() => {
        // Just navigate to explorer; user can use the document type / cases filters there
        router.replace('/explorer');
    }, [router]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <p className="text-gray-600 text-sm">
                Redirecting to the unified Explorer view…
            </p>
        </div>
    );
}
