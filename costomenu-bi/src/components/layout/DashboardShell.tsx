import { Sidebar } from "@/components/layout/Sidebar"
import { Button } from "@/components/ui/button"
import { CalendarIcon } from "lucide-react"

export function DashboardShell({ children }: { children: React.ReactNode }) {
    return (
        <div className="flex min-h-screen">
            <Sidebar />
            <div className="flex-1 flex flex-col">
                <header className="border-b h-16 flex items-center justify-between px-8">
                    <h1 className="text-lg font-semibold">Executive Dashboard</h1>
                    <div className="flex items-center space-x-2">
                        <Button variant="outline" className="text-muted-foreground">
                            <CalendarIcon className="mr-2 h-4 w-4" />
                            Jan 01, 2026 - Dec 31, 2026
                        </Button>
                    </div>
                </header>
                <main className="flex-1 space-y-4 p-8 pt-6">
                    {children}
                </main>
            </div>
        </div>
    )
}
