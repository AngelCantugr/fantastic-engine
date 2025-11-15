import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Plus, Check, Trash2, Clock } from 'lucide-react'

interface Task {
  id: number
  title: string
  description?: string
  priority: number
  energy_required: number
  estimated_minutes: number
  completed: boolean
  xp_reward: number
}

const TaskList = () => {
  const [tasks, setTasks] = useState<Task[]>([])
  const [newTask, setNewTask] = useState({ title: '', priority: 1, estimated_minutes: 25 })
  const [showForm, setShowForm] = useState(false)

  useEffect(() => {
    fetchTasks()
  }, [])

  const fetchTasks = async () => {
    const response = await fetch('/api/tasks')
    const data = await response.json()
    setTasks(data)
  }

  const createTask = async (e: React.FormEvent) => {
    e.preventDefault()

    const response = await fetch('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...newTask,
        energy_required: 5,
        xp_reward: newTask.priority * 10,
      }),
    })

    if (response.ok) {
      setNewTask({ title: '', priority: 1, estimated_minutes: 25 })
      setShowForm(false)
      fetchTasks()
    }
  }

  const completeTask = async (taskId: number) => {
    const response = await fetch(`/api/tasks/${taskId}/complete`, {
      method: 'POST',
    })

    if (response.ok) {
      const data = await response.json()
      // Show XP gained notification
      showNotification(`+${data.xp_earned} XP!`)
      fetchTasks()
    }
  }

  const deleteTask = async (taskId: number) => {
    await fetch(`/api/tasks/${taskId}`, { method: 'DELETE' })
    fetchTasks()
  }

  const showNotification = (message: string) => {
    const notification = document.createElement('div')
    notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-xl shadow-lg font-bold text-xl animate-bounce'
    notification.textContent = message
    document.body.appendChild(notification)
    setTimeout(() => notification.remove(), 2000)
  }

  const priorityColors = {
    1: 'bg-blue-100 border-blue-300',
    2: 'bg-green-100 border-green-300',
    3: 'bg-yellow-100 border-yellow-300',
    4: 'bg-orange-100 border-orange-300',
    5: 'bg-red-100 border-red-300',
  }

  return (
    <div className="glass-card p-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold">📝 Tasks</h2>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-secondary)] text-white rounded-lg font-semibold"
        >
          <Plus size={20} />
          New Task
        </motion.button>
      </div>

      {/* New Task Form */}
      <AnimatePresence>
        {showForm && (
          <motion.form
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            onSubmit={createTask}
            className="mb-6 p-4 bg-gray-50 rounded-xl space-y-4"
          >
            <input
              type="text"
              placeholder="Task title..."
              value={newTask.title}
              onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
              className="w-full p-3 border-2 border-gray-300 rounded-lg"
              required
            />

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block mb-2 font-semibold text-sm">Priority (1-5)</label>
                <select
                  value={newTask.priority}
                  onChange={(e) => setNewTask({ ...newTask, priority: parseInt(e.target.value) })}
                  className="w-full p-3 border-2 border-gray-300 rounded-lg"
                >
                  {[1, 2, 3, 4, 5].map((p) => (
                    <option key={p} value={p}>
                      {p} - {['Low', 'Medium-Low', 'Medium', 'Medium-High', 'High'][p - 1]}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block mb-2 font-semibold text-sm">Estimated Time (min)</label>
                <input
                  type="number"
                  value={newTask.estimated_minutes}
                  onChange={(e) => setNewTask({ ...newTask, estimated_minutes: parseInt(e.target.value) })}
                  className="w-full p-3 border-2 border-gray-300 rounded-lg"
                  min="5"
                  step="5"
                />
              </div>
            </div>

            <div className="flex gap-2">
              <button
                type="submit"
                className="flex-1 py-2 bg-green-500 text-white rounded-lg font-semibold hover:bg-green-600 transition-colors"
              >
                Add Task
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-400 transition-colors"
              >
                Cancel
              </button>
            </div>
          </motion.form>
        )}
      </AnimatePresence>

      {/* Task List */}
      <div className="space-y-3">
        <AnimatePresence>
          {tasks.filter(t => !t.completed).map((task) => (
            <motion.div
              key={task.id}
              layout
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, x: -100 }}
              className={`p-4 border-2 rounded-xl ${priorityColors[task.priority as keyof typeof priorityColors]} transition-all hover:shadow-md`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-bold text-lg mb-1">{task.title}</h3>
                  <div className="flex items-center gap-3 text-sm text-gray-600">
                    <span className="flex items-center gap-1">
                      <Clock size={14} />
                      {task.estimated_minutes} min
                    </span>
                    <span className="font-semibold text-purple-600">
                      +{task.xp_reward} XP
                    </span>
                    <span className="text-xs bg-white px-2 py-1 rounded">
                      Priority {task.priority}
                    </span>
                  </div>
                </div>

                <div className="flex gap-2">
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => completeTask(task.id)}
                    className="p-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                  >
                    <Check size={20} />
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => deleteTask(task.id)}
                    className="p-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                  >
                    <Trash2 size={20} />
                  </motion.button>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {tasks.filter(t => !t.completed).length === 0 && (
          <div className="text-center py-12 text-gray-400">
            <p className="text-xl">No active tasks</p>
            <p className="text-sm">Add a task to get started!</p>
          </div>
        )}
      </div>

      {/* Completed Tasks */}
      {tasks.filter(t => t.completed).length > 0 && (
        <div className="mt-8 pt-6 border-t-2 border-gray-200">
          <h3 className="text-xl font-bold mb-4 text-gray-600">✅ Completed</h3>
          <div className="space-y-2">
            {tasks.filter(t => t.completed).map((task) => (
              <div key={task.id} className="p-3 bg-gray-100 rounded-lg opacity-60 line-through">
                {task.title}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default TaskList
