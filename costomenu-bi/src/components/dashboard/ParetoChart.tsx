"use client"

import { useMemo } from "react"
import { Bar, BarChart, CartesianGrid, ComposedChart, Legend, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { data } from "@/lib/data"

export function ParetoChart() {
    const chartData = useMemo(() => {
        // 1. Sort users by revenue desc
        const sorted = [...data].sort((a, b) => b.TotalPayments - a.TotalPayments).filter(u => u.TotalPayments > 0)

        // 2. Calculate cumulative
        const totalRevenue = sorted.reduce((sum, u) => sum + u.TotalPayments, 0)
        let cumulative = 0

        // 3. Map to chart data
        const top30 = sorted.slice(0, 30).map((u, i) => {
            cumulative += u.TotalPayments
            return {
                name: u.Fullname.split(' ')[0], // First name for brevity
                revenue: u.TotalPayments,
                cumulativePercentage: (cumulative / totalRevenue) * 100,
                full_name: u.Fullname
            }
        })

        return top30
    }, [])

    return (
        <Card>
            <CardHeader>
                <CardTitle>Revenue Pareto Principle</CardTitle>
                <CardDescription>
                    Top contributors to revenue (Whales vs Long Tail).
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div className="h-[300px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <ComposedChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} />
                            <XAxis
                                dataKey="name"
                                stroke="#888888"
                                fontSize={12}
                                tickLine={false}
                                axisLine={false}
                            />
                            <YAxis
                                yAxisId="left"
                                orientation="left"
                                stroke="#888888"
                                fontSize={12}
                                tickLine={false}
                                axisLine={false}
                                tickFormatter={(value) => `€${value}`}
                            />
                            <YAxis
                                yAxisId="right"
                                orientation="right"
                                stroke="#888888"
                                fontSize={12}
                                tickLine={false}
                                axisLine={false}
                                unit="%"
                            />
                            <Tooltip
                                formatter={(value: any, name: any) => {
                                    if (name === "cumulativePercentage") return `${Number(value).toFixed(1)}%`
                                    return `€${Number(value).toFixed(2)}`
                                }}
                                labelStyle={{ color: "black" }}
                            />
                            <Legend />
                            <Bar yAxisId="left" dataKey="revenue" name="Revenue" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                            <Line yAxisId="right" type="monotone" dataKey="cumulativePercentage" name="Cumulative %" stroke="hsl(var(--destructive))" strokeWidth={2} dot={false} />
                        </ComposedChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
    )
}
