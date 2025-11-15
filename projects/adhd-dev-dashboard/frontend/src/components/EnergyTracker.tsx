import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface EnergyLog {
  id: number
  timestamp: string
  energy_level: number
  focus_level: number
  mood: string
}

const EnergyTracker = () => {
  const [energyLogs, setEnergyLogs] = useState<EnergyLog[]>([])
  const [newLog, setNewLog] = useState({
    energy_level: 5,
    focus_level: 5,
    mood: 'neutral',
    notes: '',
  })

  useEffect(() => {
    fetchEnergyLogs()
  }, [])

  const fetchEnergyLogs = async () => {
    const response = await fetch('/api/energy/today')
    const data = await response.json()
    setEnergyLogs(data)
  }

  const logEnergy = async (e: React.FormEvent) => {
    e.preventDefault()

    const response = await fetch('/api/energy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newLog),
    })

    if (response.ok) {
      setNewLog({ energy_level: 5, focus_level: 5, mood: 'neutral', notes: '' })
      fetchEnergyLogs()
    }
  }

  const chartData = energyLogs.map((log) => ({
    time: new Date(log.timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    }),
    energy: log.energy_level,
    focus: log.focus_level,
  }))

  const moods = [
    { value: 'happy', emoji: '😊', label: 'Happy' },
    { value: 'neutral', emoji: '😐', label: 'Neutral' },
    { value: 'stressed', emoji: '😰', label: 'Stressed' },
    { value: 'tired', emoji: '😴', label: 'Tired' },
  ]

  return (
    <div className="glass-card p-8">
      <h2 className="text-3xl font-bold mb-6">⚡ Energy Tracker</h2>

      {/* Log Form */}
      <form onSubmit={logEnergy} className="mb-8 p-6 bg-gray-50 rounded-xl space-y-6">
        <div>
          <label className="block mb-2 font-semibold">Energy Level: {newLog.energy_level}/10</label>
          <input
            type="range"
            min="1"
            max="10"
            value={newLog.energy_level}
            onChange={(e) => setNewLog({ ...newLog, energy_level: parseInt(e.target.value) })}
            className="w-full h-3 bg-gradient-to-r from-red-400 via-yellow-400 to-green-400 rounded-lg appearance-none cursor-pointer"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Low</span>
            <span>High</span>
          </div>
        </div>

        <div>
          <label className="block mb-2 font-semibold">Focus Level: {newLog.focus_level}/10</label>
          <input
            type="range"
            min="1"
            max="10"
            value={newLog.focus_level}
            onChange={(e) => setNewLog({ ...newLog, focus_level: parseInt(e.target.value) })}
            className="w-full h-3 bg-gradient-to-r from-orange-400 via-purple-400 to-blue-400 rounded-lg appearance-none cursor-pointer"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Scattered</span>
            <span>Laser</span>
          </div>
        </div>

        <div>
          <label className="block mb-3 font-semibold">Mood</label>
          <div className="grid grid-cols-4 gap-2">
            {moods.map((mood) => (
              <button
                key={mood.value}
                type="button"
                onClick={() => setNewLog({ ...newLog, mood: mood.value })}
                className={`p-4 rounded-xl text-center transition-all ${
                  newLog.mood === mood.value
                    ? 'bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-secondary)] text-white scale-105'
                    : 'bg-white hover:bg-gray-100'
                }`}
              >
                <div className="text-3xl mb-1">{mood.emoji}</div>
                <div className="text-sm font-semibold">{mood.label}</div>
              </button>
            ))}
          </div>
        </div>

        <button
          type="submit"
          className="w-full py-3 bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-secondary)] text-white rounded-xl font-semibold hover:shadow-lg transition-shadow"
        >
          Log Now
        </button>
      </form>

      {/* Chart */}
      {energyLogs.length > 0 ? (
        <div className="bg-white p-6 rounded-xl">
          <h3 className="text-xl font-bold mb-4">Today's Patterns</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis domain={[0, 10]} />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="energy"
                stroke="var(--color-primary)"
                strokeWidth={3}
                name="Energy"
              />
              <Line
                type="monotone"
                dataKey="focus"
                stroke="var(--color-secondary)"
                strokeWidth={3}
                name="Focus"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="text-center py-12 text-gray-400">
          <p className="text-xl">No energy logs yet today</p>
          <p className="text-sm">Log your first entry above!</p>
        </div>
      )}

      {/* Today's Logs */}
      {energyLogs.length > 0 && (
        <div className="mt-6 space-y-2">
          <h3 className="text-xl font-bold mb-3">Today's Check-ins</h3>
          {energyLogs.map((log) => (
            <div key={log.id} className="p-3 bg-white rounded-lg flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-2xl">
                  {moods.find((m) => m.value === log.mood)?.emoji || '😐'}
                </span>
                <div>
                  <div className="font-semibold">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </div>
                  <div className="text-sm text-gray-500">
                    Energy: {log.energy_level}/10 | Focus: {log.focus_level}/10
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default EnergyTracker
