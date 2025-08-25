import { DashboardLayout } from "@/components/dashboard-layout"
import { ChatOpsInterface } from "@/components/chatops-interface"

export default function ChatOpsPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">ChatOps</h1>
          <p className="text-muted-foreground">AI-powered conversational cloud operations interface</p>
        </div>
        <ChatOpsInterface />
      </div>
    </DashboardLayout>
  )
}
