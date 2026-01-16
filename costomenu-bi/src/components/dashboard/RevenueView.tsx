"use client"

import { useMemo } from "react"
import { data, User } from "@/lib/data"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { AlertCircle, Euro, Send } from "lucide-react"
import { ParetoChart } from "./ParetoChart"

export function RevenueView() {
    // Logic to process data
    const { totalARR, arpu, potentialChurn, zombies, topRevenueUsers } = useMemo(() => {
        let totalPayments = 0
        let userCount = 0
        let churnRevenue = 0
        let zombieUsers: User[] = []

        // Sort for Pareto (top 20%) - simplified logic for finding top revenue
        // Actually we need aggregate metrics first

        // Date parsing helper
        const isExpired = (dateStr: string) => {
            // dateStr is DD/MM/YYYY or empty
            if (!dateStr) return false // Assume active if no date? Or ignore?
            const parts = dateStr.split('/')
            if (parts.length !== 3) return false
            // new Date(year, monthIndex, day)
            const exp = new Date(parseInt(parts[2]), parseInt(parts[1]) - 1, parseInt(parts[0]))
            const today = new Date() // Current date
            return exp < today
        }

        data.forEach(user => {
            totalPayments += user.TotalPayments
            if (user.TotalPayments > 0) userCount++

            // Zombie Logic: Active but Expired
            if (user.Status === "ACTIVE" && isExpired(user.ExpirationDate)) {
                zombieUsers.push(user)
                churnRevenue += user.TotalPayments // Revenue at risk? Or past revenue? Prompt says "Potential Churn Revenue"
            }
        })

        return {
            totalARR: totalPayments, // Prompt implies payments are annual or total? "TotalPayments"
            arpu: userCount > 0 ? totalPayments / userCount : 0,
            potentialChurn: churnRevenue,
            zombies: zombieUsers,
            topRevenueUsers: [...data].sort((a, b) => b.TotalPayments - a.TotalPayments).slice(0, 10)
        }
    }, [])

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold">Revenue Health</h1>

            {/* KPI Cards */}
            <div className="grid gap-4 md:grid-cols-3">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
                        <Euro className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">€{totalARR.toFixed(2)}</div>
                        <p className="text-xs text-muted-foreground">Across all users</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">ARPU</CardTitle>
                        <UsersIcon className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">€{arpu.toFixed(2)}</div>
                        <p className="text-xs text-muted-foreground">Average Revenue Per User</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Potential Churn (Zombies)</CardTitle>
                        <AlertCircle className="h-4 w-4 text-destructive" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-destructive">€{potentialChurn.toFixed(2)}</div>
                        <p className="text-xs text-muted-foreground"> expired active accounts</p>
                    </CardContent>
                </Card>
            </div>

            {/* Zombie Alert System */}
            <Card className="border-destructive/50">
                <CardHeader>
                    <CardTitle className="text-destructive flex items-center gap-2">
                        <AlertCircle /> Zombie User Alert
                    </CardTitle>
                    <CardDescription>
                        These {zombies.length} users have "Active" status but their license has expired.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Name</TableHead>
                                <TableHead>Company</TableHead>
                                <TableHead>Expiration</TableHead>
                                <TableHead>Revenue</TableHead>
                                <TableHead>Action</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {zombies.map(user => (
                                <TableRow key={user.UserID} className="bg-destructive/10 hover:bg-destructive/20">
                                    <TableCell className="font-medium">{user.Fullname}</TableCell>
                                    <TableCell>{user.Company}</TableCell>
                                    <TableCell>{user.ExpirationDate}</TableCell>
                                    <TableCell>€{user.TotalPayments.toFixed(2)}</TableCell>
                                    <TableCell>
                                        <Button size="sm" variant="destructive" onClick={() => alert(`Sending renewal reminder to ${user.Fullname}`)}>
                                            <Send className="mr-2 h-4 w-4" /> Renewal Reminder
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))}
                            {zombies.length === 0 && (
                                <TableRow>
                                    <TableCell colSpan={5} className="text-center h-24">
                                        No zombie users found.
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            <div className="pt-4">
                <ParetoChart />
            </div>
        </div>
    )
}

function UsersIcon(props: any) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
        </svg>
    )
}
