import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import PomodoroTimer from './components/PomodoroTimer'
import TaskList from './components/TaskList'
import EnergyTracker from './components/EnergyTracker'
import StatsPanel from './components/StatsPanel'
import { Timer, CheckSquare, Zap, Trophy } from 'lucide-react'

function App() {
  const [activeTab, setActiveTab] = useState<'timer' | 'tasks' | 'energy' | 'stats'>('timer')

  return (
    <div className="min-h-screen p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-6 mb-6"
        >
          <h1 className="text-4xl font-bold gradient-text mb-2">
            🎯 ADHD Dev Dashboard
          </h1>
          <p className="text-gray-600">
            Visual task tracking with dopamine-driven progress gamification
          </p>
        </motion.header>

        {/* Tab Navigation */}
        <div className="glass-card p-2 mb-6 flex gap-2">
          {[
            { id: 'timer', label: 'Pomodoro', icon: Timer },
            { id: 'tasks', label: 'Tasks', icon: CheckSquare },
            { id: 'energy', label: 'Energy', icon: Zap },
            { id: 'stats', label: 'Stats', icon: Trophy },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-xl font-semibold transition-all ${
                activeTab === tab.id
                  ? 'bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-secondary)] text-white shadow-lg'
                  : 'hover:bg-gray-100 text-gray-600'
              }`}
            >
              <tab.icon size={20} />
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Content */}
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
        >
          {activeTab === 'timer' && <PomodoroTimer />}
          {activeTab === 'tasks' && <TaskList />}
          {activeTab === 'energy' && <EnergyTracker />}
          {activeTab === 'stats' && <StatsPanel />}
        </motion.div>
      </div>
    </div>
  )
}

export default App
