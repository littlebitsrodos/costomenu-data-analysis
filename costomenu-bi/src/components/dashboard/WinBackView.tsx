"use client"

import { useMemo } from "react"
import { data } from "@/lib/data"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ArrowUpCircle, RefreshCcw } from "lucide-react"

export function WinBackView() {
    const { winBackUsers } = useMemo(() => {
        // Filter: Beginner license but TotalPayments > 0
        const users = data.filter(u =>
            u.LicenseType.toLowerCase() === "beginner" && u.TotalPayments > 0
        )
        // Also add Upsell Targets: Beginner with >20 recipes
        // Prompt says "Action: Add a 'Target for Upsell' badge next to any 'Beginner' user who has >20 recipes"
        // Win-Back list specifically mentions payment history

        return {
            winBackUsers: users.sort((a, b) => b.TotalPayments - a.TotalPayments)
        }
    }, [])

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold">Win-Back & Upsell Opportunities</h1>

            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <RefreshCcw className="h-5 w-5" /> Win-Back Candidates
                    </CardTitle>
                    <CardDescription>
                        Users on "Beginner" plan who have previously paid (churned from paid tiers or bought add-ons).
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Name</TableHead>
                                <TableHead>Company</TableHead>
                                <TableHead>Recipes</TableHead>
                                <TableHead>Past Revenue</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead>Action</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {winBackUsers.map(user => {
                                const isUpsellTarget = user.RecipeCount > 20
                                return (
                                    <TableRow key={user.UserID}>
                                        <TableCell className="font-medium">{user.Fullname}</TableCell>
                                        <TableCell>{user.Company}</TableCell>
                                        <TableCell>
                                            {user.RecipeCount}
                                            {isUpsellTarget && (
                                                <Badge variant="outline" className="ml-2 border-orange-500 text-orange-500">
                                                    Hit Limit
                                                </Badge>
                                            )}
                                        </TableCell>
                                        <TableCell>€{user.TotalPayments.toFixed(2)}</TableCell>
                                        <TableCell>
                                            <Badge variant="secondary">{user.Status}</Badge>
                                        </TableCell>
                                        <TableCell>
                                            {isUpsellTarget ? (
                                                <Button size="sm" className="bg-orange-500 hover:bg-orange-600">
                                                    <ArrowUpCircle className="mr-2 h-4 w-4" /> Upsell Pro
                                                </Button>
                                            ) : (
                                                <Button size="sm" variant="outline">
                                                    Contact
                                                </Button>
                                            )}
                                        </TableCell>
                                    </TableRow>
                                )
                            })}
                            {winBackUsers.length === 0 && (
                                <TableRow>
                                    <TableCell colSpan={6} className="text-center h-24">
                                        No win-back opportunities found based on current criteria.
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>
    )
}
