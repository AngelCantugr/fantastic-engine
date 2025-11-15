import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Trophy, Flame, Target, Zap } from 'lucide-react'

interface UserStats {
  total_xp: number
  level: number
  current_streak: number
  longest_streak: number
  total_tasks: number
  total_pomodoros: number
}

const StatsPanel = () => {
  const [stats, setStats] = useState<UserStats>({
    total_xp: 0,
    level: 1,
    current_streak: 0,
    longest_streak: 0,
    total_tasks: 0,
    total_pomodoros: 0,
  })

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    const response = await fetch('/api/stats')
    const data = await response.json()
    setStats(data)
  }

  const xpForNextLevel = Math.floor(100 + stats.level * 50)
  const xpProgress = (stats.total_xp % xpForNextLevel) / xpForNextLevel * 100

  const statCards = [
    {
      icon: Trophy,
      label: 'Level',
      value: stats.level,
      color: 'from-yellow-400 to-orange-500',
      subtext: `${Math.floor(xpProgress)}% to Level ${stats.level + 1}`,
    },
    {
      icon: Flame,
      label: 'Current Streak',
      value: `${stats.current_streak} days`,
      color: 'from-red-400 to-pink-500',
      subtext: `Best: ${stats.longest_streak} days`,
    },
    {
      icon: Target,
      label: 'Tasks Completed',
      value: stats.total_tasks,
      color: 'from-green-400 to-teal-500',
      subtext: 'All time',
    },
    {
      icon: Zap,
      label: 'Pomodoros',
      value: stats.total_pomodoros,
      color: 'from-purple-400 to-indigo-500',
      subtext: 'Total sessions',
    },
  ]

  return (
    <div className="glass-card p-8">
      <h2 className="text-3xl font-bold mb-6">🏆 Your Stats</h2>

      {/* XP Progress Bar */}
      <div className="mb-8 p-6 bg-gray-50 rounded-xl">
        <div className="flex justify-between mb-2">
          <span className="font-semibold">Total XP</span>
          <span className="font-bold text-purple-600">{stats.total_xp} XP</span>
        </div>
        <div className="w-full h-6 bg-gray-200 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${xpProgress}%` }}
            className="h-full bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-secondary)]"
          />
        </div>
        <div className="text-sm text-gray-500 mt-2 text-center">
          {xpForNextLevel - (stats.total_xp % xpForNextLevel)} XP to next level
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        {statCards.map((card, index) => (
          <motion.div
            key={card.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`p-6 rounded-xl bg-gradient-to-br ${card.color} text-white`}
          >
            <div className="flex items-start justify-between mb-4">
              <card.icon size={32} />
              <div className="text-right">
                <div className="text-3xl font-bold">{card.value}</div>
                <div className="text-sm opacity-90">{card.label}</div>
              </div>
            </div>
            <div className="text-sm opacity-75">{card.subtext}</div>
          </motion.div>
        ))}
      </div>

      {/* Achievements */}
      <div>
        <h3 className="text-2xl font-bold mb-4">🎖️ Achievements</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { icon: '🎯', name: 'First Steps', unlocked: stats.total_tasks > 0 },
            { icon: '🔥', name: 'Week Warrior', unlocked: stats.current_streak >= 7 },
            { icon: '⚡', name: 'Focus Master', unlocked: stats.total_pomodoros >= 50 },
            { icon: '🏆', name: 'Task Terminator', unlocked: stats.total_tasks >= 100 },
            { icon: '🌟', name: 'Early Bird', unlocked: false },
            { icon: '🦉', name: 'Night Owl', unlocked: false },
            { icon: '💪', name: 'Pro', unlocked: stats.level >= 10 },
            { icon: '🚀', name: 'Marathon', unlocked: stats.longest_streak >= 30 },
          ].map((achievement) => (
            <div
              key={achievement.name}
              className={`p-4 rounded-xl text-center transition-all ${
                achievement.unlocked
                  ? 'bg-gradient-to-br from-yellow-400 to-orange-500 text-white scale-105'
                  : 'bg-gray-100 opacity-50 grayscale'
              }`}
            >
              <div className="text-3xl mb-1">{achievement.icon}</div>
              <div className="text-xs font-semibold">{achievement.name}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Motivational Message */}
      <div className="mt-8 p-6 bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-secondary)] text-white rounded-xl text-center">
        <p className="text-lg font-semibold">
          {stats.current_streak > 0
            ? `🔥 Amazing! You're on a ${stats.current_streak} day streak!`
            : "🎯 Start your streak today! Complete a task to begin."}
        </p>
      </div>
    </div>
  )
}

export default StatsPanel
