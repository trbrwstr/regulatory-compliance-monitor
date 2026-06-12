import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Regulations from './pages/Regulations'
import Alerts from './pages/Alerts'
import Subscribers from './pages/Subscribers'

export default function App() {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/regulations" element={<Regulations />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/subscribers" element={<Subscribers />} />
        </Routes>
      </main>
    </div>
  )
}
