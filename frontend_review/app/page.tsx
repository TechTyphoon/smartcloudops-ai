import { DashboardLayout } from "@/components/dashboard-layout"
import WelcomeHero from "@/components/welcome-hero"
import { ProtectedRoute } from "@/components/auth/protected-route"

export default function HomePage() {
  return (
    <ProtectedRoute>
      <DashboardLayout>
        <WelcomeHero />
      </DashboardLayout>
    </ProtectedRoute>
  )
}
