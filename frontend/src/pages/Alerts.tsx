import { useEffect, useState } from 'react'
import { api, Alert } from '../lib/api'
import { Bell, CheckCircle, Clock, XCircle, Mail } from 'lucide-react'

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('')
  const [stats, setStats] = useState<{ total: number; sent: number; pending: number; failed: number } | null>(null)

  useEffect(() => {
    loadAlerts()
    loadStats()
  }, [statusFilter])

  async function loadAlerts() {
    setLoading(true)
    try {
      const data = await api.getAlerts({
        status: statusFilter || undefined,
        limit: 50,
      })
      setAlerts(data.alerts)
      setTotal(data.total)
    } catch (err) {
      console.error('Failed to load alerts:', err)
    } finally {
      setLoading(false)
    }
  }

  async function loadStats() {
    try {
      const data = await api.getAlertStats()
      setStats(data)
    } catch (err) {
      console.error('Failed to load alert stats:', err)
    }
  }

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Alerts</h1>
        <p className="text-gray-500 mt-1">Email notifications sent to subscribers</p>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <MiniStat label="Total" value={stats.total} icon={Bell} />
          <MiniStat label="Sent" value={stats.sent} icon={CheckCircle} color="text-green-600" />
          <MiniStat label="Pending" value={stats.pending} icon={Clock} color="text-amber-600" />
          <MiniStat label="Failed" value={stats.failed} icon={XCircle} color="text-red-600" />
        </div>
      )}

      {/* Filter */}
      <div className="flex items-center gap-3 mb-6">
        <span className="text-sm text-gray-500">Filter:</span>
        {['', 'sent', 'pending', 'failed'].map((status) => (
          <button
            key={status}
            onClick={() => setStatusFilter(status)}
            className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
              statusFilter === status
                ? 'bg-blue-600 text-white'
                : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            {status || 'All'}
          </button>
        ))}
      </div>

      {/* Alert List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      ) : alerts.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
          <Mail className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">No alerts found.</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Subscriber</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Regulation</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Impact</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sent</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {alerts.map((alert) => (
                <tr key={alert.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">{alert.subscriber.name}</div>
                    <div className="text-xs text-gray-500">{alert.subscriber.email}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900 max-w-xs truncate">{alert.regulation.title}</div>
                  </td>
                  <td className="px-6 py-4">
                    <ImpactBadge level={alert.regulation.impact_level} />
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={alert.delivery_status} />
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {alert.sent_at ? new Date(alert.sent_at).toLocaleString() : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

function MiniStat({
  label,
  value,
  icon: Icon,
  color = 'text-gray-600',
}: {
  label: string
  value: number
  icon: React.ComponentType<{ className?: string }>
  color?: string
}) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 flex items-center gap-3">
      <Icon className={`h-5 w-5 ${color}`} />
      <div>
        <p className="text-xs text-gray-500">{label}</p>
        <p className="text-lg font-semibold text-gray-900">{value}</p>
      </div>
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const classes: Record<string, string> = {
    sent: 'bg-green-100 text-green-700',
    pending: 'bg-amber-100 text-amber-700',
    failed: 'bg-red-100 text-red-700',
  }
  return (
    <span className={`text-xs font-medium px-2.5 py-0.5 rounded-full ${classes[status] || 'bg-gray-100 text-gray-700'}`}>
      {status}
    </span>
  )
}

function ImpactBadge({ level }: { level: string }) {
  const classes: Record<string, string> = {
    high: 'bg-red-100 text-red-700',
    medium: 'bg-amber-100 text-amber-700',
    low: 'bg-green-100 text-green-700',
  }
  return (
    <span className={`text-xs font-medium px-2.5 py-0.5 rounded-full ${classes[level] || classes.medium}`}>
      {level}
    </span>
  )
}
