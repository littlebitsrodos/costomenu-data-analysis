"use client"

import { useMemo } from "react"
import { CartesianGrid, Legend, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis, ZAxis } from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { data } from "@/lib/data"

export function MaturityScatterPlot() {
    const chartData = useMemo(() => {
        return data.map(u => ({
            x: u.RecipeCount,
            y: u.DistributorCount,
            name: u.Fullname,
            company: u.Company,
            license: u.LicenseType,
            z: 1 // Default size
        }))
    }, [])

    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>Maturity Matrix: Operational Complexity</CardTitle>
                <CardDescription>
                    High Distributor Count correlates with "Expert" usage.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div className="h-[500px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                            <CartesianGrid />
                            <XAxis type="number" dataKey="x" name="Recipe Volume" unit="" label={{ value: 'Recipe Count', position: 'insideBottomRight', offset: -10 }} />
                            <YAxis type="number" dataKey="y" name="Complexity (Distributors)" unit="" label={{ value: 'Distributor Count', angle: -90, position: 'insideLeft' }} />
                            <Tooltip cursor={{ strokeDasharray: '3 3' }} content={({ active, payload }) => {
                                if (active && payload && payload.length) {
                                    const d = payload[0].payload
                                    return (
                                        <div className="rounded-lg border bg-background p-2 shadow-sm">
                                            <div className="grid grid-cols-2 gap-2">
                                                <div className="flex flex-col">
                                                    <span className="text-[0.70rem] uppercase text-muted-foreground">
                                                        User
                                                    </span>
                                                    <span className="font-bold text-muted-foreground">
                                                        {d.name}
                                                    </span>
                                                </div>
                                                <div className="flex flex-col">
                                                    <span className="text-[0.70rem] uppercase text-muted-foreground">
                                                        Company
                                                    </span>
                                                    <span className="font-bold text-muted-foreground">
                                                        {d.company}
                                                    </span>
                                                </div>
                                                <div className="flex flex-col">
                                                    <span className="text-[0.70rem] uppercase text-muted-foreground">
                                                        License
                                                    </span>
                                                    <span className="font-bold">
                                                        {d.license}
                                                    </span>
                                                </div>
                                                <div className="flex flex-col">
                                                    <span className="text-[0.70rem] uppercase text-muted-foreground">
                                                        Complexity
                                                    </span>
                                                    <span className="font-bold text-muted-foreground">
                                                        {d.y} Dist / {d.x} Rec
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    )
                                }
                                return null
                            }} />
                            <Legend />
                            <Scatter name="Users" data={chartData} fill="hsl(var(--primary))" />
                        </ScatterChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
    )
}
