import './globals.css';
import Navbar from '@/components/navbar';
import type { Metadata } from 'next';

export const metadata: Metadata = {
    title: 'Charity Compliance Tracker | UK Policy Monitor',
    description: 'A comprehensive tracker for UK charity compliance policies and regulations',
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <body className="min-h-screen bg-gray-50">
                <Navbar />
                <main>{children}</main>
                <footer className="bg-white border-t mt-auto py-6">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                        <p className="text-sm text-gray-500 text-center">
                            © {new Date().getFullYear()} Charity Compliance Tracker - Updated quarterly with regulatory data from UK sources
                        </p>
                    </div>
                </footer>
            </body>
        </html>
    );
}
