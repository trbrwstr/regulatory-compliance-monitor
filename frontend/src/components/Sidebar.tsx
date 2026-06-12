import { NavLink } from 'react-router-dom'
import { LayoutDashboard, FileText, Bell, Users, Shield } from 'lucide-react'

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/regulations', label: 'Regulations', icon: FileText },
  { to: '/alerts', label: 'Alerts', icon: Bell },
  { to: '/subscribers', label: 'Subscribers', icon: Users },
]

export default function Sidebar() {
  return (
    <aside className="w-64 bg-slate-900 text-white flex flex-col">
      <div className="p-6 border-b border-slate-700">
        <div className="flex items-center gap-3">
          <Shield className="h-8 w-8 text-blue-400" />
          <div>
            <h1 className="font-bold text-lg leading-tight">RegComply</h1>
            <p className="text-xs text-slate-400">Compliance Monitor</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`
            }
          >
            <item.icon className="h-5 w-5" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-slate-700">
        <div className="text-xs text-slate-500 text-center">
          Monitoring Active
          <span className="inline-block w-2 h-2 bg-green-400 rounded-full ml-2 animate-pulse" />
        </div>
      </div>
    </aside>
  )
}
