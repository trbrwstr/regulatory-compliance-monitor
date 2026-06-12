import { useEffect, useState } from 'react'
import { api, Regulation } from '../lib/api'
import { FileText, ExternalLink, Filter } from 'lucide-react'

export default function Regulations() {
  const [regulations, setRegulations] = useState<Regulation[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [industryFilter, setIndustryFilter] = useState('')
  const [impactFilter, setImpactFilter] = useState('')

  useEffect(() => {
    loadRegulations()
  }, [industryFilter, impactFilter])

  async function loadRegulations() {
    setLoading(true)
    try {
      const data = await api.getRegulations({
        industry: industryFilter || undefined,
        impact_level: impactFilter || undefined,
        limit: 50,
      })
      setRegulations(data.regulations)
      setTotal(data.total)
    } catch (err) {
      console.error('Failed to load regulations:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Regulations</h1>
          <p className="text-gray-500 mt-1">{total} regulatory updates tracked</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4 mb-6">
        <Filter className="h-4 w-4 text-gray-400" />
        <select
          value={industryFilter}
          onChange={(e) => setIndustryFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">All Industries</option>
          <option value="fintech">Fintech</option>
          <option value="healthcare">Healthcare</option>
          <option value="food_service">Food Service</option>
          <option value="general">General</option>
        </select>
        <select
          value={impactFilter}
          onChange={(e) => setImpactFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">All Impact Levels</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      {/* Regulation List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      ) : regulations.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
          <FileText className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">No regulations found matching your filters.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {regulations.map((reg) => (
            <RegulationCard key={reg.id} regulation={reg} />
          ))}
        </div>
      )}
    </div>
  )
}

function RegulationCard({ regulation }: { regulation: Regulation }) {
  const [expanded, setExpanded] = useState(false)

  const impactClasses: Record<string, string> = {
    high: 'bg-red-100 text-red-700 border-red-200',
    medium: 'bg-amber-100 text-amber-700 border-amber-200',
    low: 'bg-green-100 text-green-700 border-green-200',
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div className="p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-gray-900">{regulation.title}</h3>
            <div className="flex items-center gap-3 mt-2">
              {regulation.impact_level && (
                <span
                  className={`text-xs font-medium px-2.5 py-0.5 rounded-full border ${
                    impactClasses[regulation.impact_level] || impactClasses.medium
                  }`}
                >
                  {regulation.impact_level.toUpperCase()} IMPACT
                </span>
              )}
              {regulation.industry && (
                <span className="text-xs px-2.5 py-0.5 bg-blue-50 text-blue-700 rounded-full border border-blue-200">
                  {regulation.industry}
                </span>
              )}
              {regulation.publication_date && (
                <span className="text-xs text-gray-400">
                  Published: {new Date(regulation.publication_date).toLocaleDateString()}
                </span>
              )}
              {regulation.effective_date && (
                <span className="text-xs text-gray-400">
                  Effective: {new Date(regulation.effective_date).toLocaleDateString()}
                </span>
              )}
            </div>
          </div>
          {regulation.source_url && (
            <a
              href={regulation.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-700 p-2"
            >
              <ExternalLink className="h-4 w-4" />
            </a>
          )}
        </div>

        {/* Summary */}
        {regulation.summary && (
          <div className="mt-4">
            <button
              onClick={() => setExpanded(!expanded)}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              {expanded ? 'Hide Summary' : 'Show AI Summary'}
            </button>
            {expanded && (
              <div className="mt-3 p-4 bg-blue-50 rounded-lg border border-blue-100">
                <p className="text-sm text-gray-700 whitespace-pre-wrap">{regulation.summary}</p>
              </div>
            )}
          </div>
        )}

        {!regulation.summary && regulation.abstract && (
          <p className="mt-3 text-sm text-gray-600 line-clamp-3">{regulation.abstract}</p>
        )}
      </div>
    </div>
  )
}
