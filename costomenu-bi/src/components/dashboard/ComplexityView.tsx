"use client"

import { MaturityScatterPlot } from "./MaturityScatterPlot"

export function ComplexityView() {
    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold">Operational Complexity</h1>
            <MaturityScatterPlot />
        </div>
    )
}
