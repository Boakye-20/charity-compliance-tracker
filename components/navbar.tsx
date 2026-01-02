"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Navbar() {
    const pathname = usePathname();

    const isActive = (path: string) => {
        return pathname === path ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600 hover:text-blue-600';
    };

    return (
        <nav className="bg-white border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    <div className="flex items-center">
                        <Link href="/" className="flex-shrink-0 flex items-center">
                            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                                Charity Compliance Tracker
                            </span>
                        </Link>
                    </div>

                    <div className="flex items-center">
                        <div className="hidden md:ml-6 md:flex md:space-x-8">
                            <Link href="/" className={`inline-flex items-center px-1 pt-1 ${isActive('/')}`}>
                                Home
                            </Link>
                            <Link href="/explorer" className={`inline-flex items-center px-1 pt-1 ${isActive('/explorer')}`}>
                                Explorer
                            </Link>
                            <Link href="/analytics" className={`inline-flex items-center px-1 pt-1 ${isActive('/analytics')}`}>
                                Analytics
                            </Link>
                            <Link href="/about" className={`inline-flex items-center px-1 pt-1 ${isActive('/about')}`}>
                                About
                            </Link>
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    );
}
