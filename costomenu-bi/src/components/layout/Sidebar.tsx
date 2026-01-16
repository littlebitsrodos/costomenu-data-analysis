"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { BarChart3, LayoutDashboard, LineChart, PieChart, Users } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

export function Sidebar() {
    const pathname = usePathname()

    const links = [
        {
            href: "/",
            label: "Overview",
            icon: LayoutDashboard,
        },
        {
            href: "/revenue",
            label: "Revenue Health",
            icon: BarChart3,
        },
        {
            href: "/complexity",
            label: "Operational Complexity",
            icon: LineChart,
        },
        {
            href: "/win-back",
            label: "Win-Back",
            icon: Users,
        },
    ]

    return (
        <div className="pb-12 w-64 border-r min-h-screen bg-card">
            <div className="space-y-4 py-4">
                <div className="px-3 py-2">
                    <h2 className="mb-2 px-4 text-lg font-semibold tracking-tight">
                        CostoMenu BI
                    </h2>
                    <div className="space-y-1">
                        {links.map((link) => (
                            <Button
                                key={link.href}
                                variant={pathname === link.href ? "secondary" : "ghost"}
                                className="w-full justify-start"
                                asChild
                            >
                                <Link href={link.href}>
                                    <link.icon className="mr-2 h-4 w-4" />
                                    {link.label}
                                </Link>
                            </Button>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}
