import { useEffect, useState } from 'react'
import { api, DashboardStats, Regulation } from '../lib/api'
import { AlertTriangle, FileText, Bell, Users, TrendingUp, Play } from 'lucide-react'

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [recentRegulations, setRecentRegulations] = useState<Regulation[]>([])
  const [loading, setLoading] = useState(true)
  const [triggering, setTriggering] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    try {
      const [statsData, regsData] = await Promise.all([
        api.getDashboardStats(),
        api.getRegulations({ limit: 5 }),
      ])
      setStats(statsData)
      setRecentRegulations(regsData.regulations)
    } catch (err) {
      console.error('Failed to load dashboard data:', err)
    } finally {
      setLoading(false)
    }
  }

  async function handleTriggerMonitoring() {
    setTriggering(true)
    try {
      await api.triggerMonitoring()
      setTimeout(loadData, 3000)
    } catch (err) {
      console.error('Failed to trigger monitoring:', err)
    } finally {
      setTriggering(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 mt-1">Regulatory compliance overview</p>
        </div>
        <button
          onClick={handleTriggerMonitoring}
          disabled={triggering}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          <Play className="h-4 w-4" />
          {triggering ? 'Running...' : 'Run Monitor'}
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Regulations"
          value={stats?.total_regulations ?? 0}
          icon={FileText}
          color="blue"
        />
        <StatCard
          title="High Impact"
          value={stats?.high_impact_regulations ?? 0}
          icon={AlertTriangle}
          color="red"
        />
        <StatCard
          title="Alerts Sent"
          value={stats?.alerts_sent ?? 0}
          icon={Bell}
          color="amber"
        />
        <StatCard
          title="Active Subscribers"
          value={stats?.active_subscribers ?? 0}
          icon={Users}
          color="green"
        />
      </div>

      {/* Recent Regulations */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-gray-400" />
          <h2 className="text-lg font-semibold text-gray-900">Recent Regulations</h2>
        </div>
        <div className="divide-y divide-gray-100">
          {recentRegulations.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              No regulations yet. Click "Run Monitor" to fetch the latest updates.
            </div>
          ) : (
            recentRegulations.map((reg) => (
              <div key={reg.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-gray-900 truncate">{reg.title}</h3>
                    <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                      {reg.summary || reg.abstract || 'No summary available'}
                    </p>
                    <div className="flex items-center gap-3 mt-2">
                      {reg.industry && (
                        <span className="text-xs px-2 py-0.5 bg-blue-50 text-blue-700 rounded-full">
                          {reg.industry}
                        </span>
                      )}
                      {reg.publication_date && (
                        <span className="text-xs text-gray-400">
                          {new Date(reg.publication_date).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                  <ImpactBadge level={reg.impact_level} />
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

function StatCard({
  title,
  value,
  icon: Icon,
  color,
}: {
  title: string
  value: number
  icon: React.ComponentType<{ className?: string }>
  color: string
}) {
  const colorClasses: Record<string, string> = {
    blue: 'bg-blue-50 text-blue-600',
    red: 'bg-red-50 text-red-600',
    amber: 'bg-amber-50 text-amber-600',
    green: 'bg-green-50 text-green-600',
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color] || colorClasses.blue}`}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </div>
  )
}

function ImpactBadge({ level }: { level: string | null }) {
  const classes: Record<string, string> = {
    high: 'bg-red-100 text-red-700',
    medium: 'bg-amber-100 text-amber-700',
    low: 'bg-green-100 text-green-700',
  }

  if (!level) return null

  return (
    <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${classes[level] || classes.medium}`}>
      {level.toUpperCase()}
    </span>
  )
}
