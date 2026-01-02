"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';

export default function Navbar() {
    const pathname = usePathname();
    const [menuOpen, setMenuOpen] = useState(false);

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
                        <button
                            onClick={() => setMenuOpen(prev => !prev)}
                            className="inline-flex items-center justify-center md:hidden text-gray-600 hover:text-blue-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded-md p-2"
                            aria-label="Toggle navigation menu"
                        >
                            <span className="sr-only">Open navigation</span>
                            <svg className="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
                                <path d="M4 6h16M4 12h16M4 18h16" />
                            </svg>
                        </button>
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
                {menuOpen && (
                    <div className="md:hidden mt-2 border-t border-gray-100">
                        <div className="flex flex-col px-2 py-3 space-y-2">
                            <Link href="/" className={`block px-3 py-2 rounded-md text-base font-medium ${isActive('/')}`}>
                                Home
                            </Link>
                            <Link href="/explorer" className={`block px-3 py-2 rounded-md text-base font-medium ${isActive('/explorer')}`}>
                                Explorer
                            </Link>
                            <Link href="/analytics" className={`block px-3 py-2 rounded-md text-base font-medium ${isActive('/analytics')}`}>
                                Analytics
                            </Link>
                            <Link href="/about" className={`block px-3 py-2 rounded-md text-base font-medium ${isActive('/about')}`}>
                                About
                            </Link>
                        </div>
                    </div>
                )}
            </div>
        </nav>
    );
}
