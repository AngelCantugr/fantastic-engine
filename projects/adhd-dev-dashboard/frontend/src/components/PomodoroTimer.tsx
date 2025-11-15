import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Play, Pause, Square, Settings } from 'lucide-react'

const PomodoroTimer = () => {
  const [timeRemaining, setTimeRemaining] = useState(25 * 60)
  const [isRunning, setIsRunning] = useState(false)
  const [duration, setDuration] = useState(25)
  const [showSettings, setShowSettings] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    // Connect to WebSocket
    const ws = new WebSocket('ws://localhost:8000/ws')
    wsRef.current = ws

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)

      if (data.type === 'pomodoro_tick') {
        setTimeRemaining(data.time_remaining)
      } else if (data.type === 'pomodoro_complete') {
        setIsRunning(false)
        // Show celebration
        showCelebration()
      }
    }

    return () => ws.close()
  }, [])

  const startPomodoro = async () => {
    const response = await fetch('/api/pomodoro/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ duration }),
    })

    if (response.ok) {
      setIsRunning(true)
      setTimeRemaining(duration * 60)
    }
  }

  const pausePomodoro = async () => {
    await fetch('/api/pomodoro/pause', { method: 'POST' })
    setIsRunning(false)
  }

  const stopPomodoro = async () => {
    await fetch('/api/pomodoro/stop', { method: 'POST' })
    setIsRunning(false)
    setTimeRemaining(duration * 60)
  }

  const showCelebration = () => {
    // Trigger celebration animation
    const celebration = document.createElement('div')
    celebration.innerHTML = '🎉'
    celebration.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      font-size: 100px;
      animation: celebrate 2s ease-out;
    `
    document.body.appendChild(celebration)
    setTimeout(() => celebration.remove(), 2000)
  }

  const minutes = Math.floor(timeRemaining / 60)
  const seconds = timeRemaining % 60
  const percentage = ((duration * 60 - timeRemaining) / (duration * 60)) * 100

  return (
    <div className="glass-card p-8">
      <div className="flex justify-between items-center mb-8">
        <h2 className="text-3xl font-bold">🍅 Pomodoro Timer</h2>
        <button
          onClick={() => setShowSettings(!showSettings)}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <Settings size={24} />
        </button>
      </div>

      {showSettings && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mb-6 p-4 bg-gray-50 rounded-xl"
        >
          <label className="block mb-2 font-semibold">Duration (minutes)</label>
          <input
            type="number"
            value={duration}
            onChange={(e) => setDuration(parseInt(e.target.value))}
            className="w-full p-2 border-2 border-gray-300 rounded-lg"
            disabled={isRunning}
          />
        </motion.div>
      )}

      {/* Timer Display */}
      <div className="relative mb-8">
        <svg className="w-full h-64" viewBox="0 0 200 200">
          {/* Background circle */}
          <circle
            cx="100"
            cy="100"
            r="80"
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="10"
          />

          {/* Progress circle */}
          <motion.circle
            cx="100"
            cy="100"
            r="80"
            fill="none"
            stroke="url(#gradient)"
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={`${2 * Math.PI * 80}`}
            strokeDashoffset={`${2 * Math.PI * 80 * (1 - percentage / 100)}`}
            transform="rotate(-90 100 100)"
            className={isRunning ? 'active-timer' : ''}
          />

          <defs>
            <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="var(--color-primary)" />
              <stop offset="100%" stopColor="var(--color-secondary)" />
            </linearGradient>
          </defs>
        </svg>

        {/* Time display */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="text-6xl font-bold gradient-text">
              {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
            </div>
            <div className="text-gray-500 mt-2">
              {isRunning ? 'Focus Time' : 'Ready'}
            </div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex gap-4 justify-center">
        {!isRunning ? (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={startPomodoro}
            className="flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-secondary)] text-white rounded-xl font-semibold shadow-lg"
          >
            <Play size={24} />
            Start
          </motion.button>
        ) : (
          <>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={pausePomodoro}
              className="flex items-center gap-2 px-8 py-4 bg-yellow-500 text-white rounded-xl font-semibold shadow-lg"
            >
              <Pause size={24} />
              Pause
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={stopPomodoro}
              className="flex items-center gap-2 px-8 py-4 bg-red-500 text-white rounded-xl font-semibold shadow-lg"
            >
              <Square size={24} />
              Stop
            </motion.button>
          </>
        )}
      </div>
    </div>
  )
}

export default PomodoroTimer
