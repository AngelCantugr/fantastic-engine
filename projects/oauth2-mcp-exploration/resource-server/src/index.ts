/**
 * Resource Server - Protected API
 *
 * This server hosts protected resources (user tasks) that require OAuth tokens.
 * MCP servers and AI agents will use their OAuth tokens to access these resources.
 *
 * Endpoints:
 * - GET /api/tasks - List all tasks (requires tasks:read)
 * - POST /api/tasks - Create task (requires tasks:write)
 * - GET /api/tasks/:id - Get task (requires tasks:read)
 * - PUT /api/tasks/:id - Update task (requires tasks:write)
 * - DELETE /api/tasks/:id - Delete task (requires tasks:write)
 * - GET /api/user - Get user info (requires user:read)
 */

import express from 'express';
import { requireAuth, requireScope } from './middleware.js';
import { TaskStorage } from './storage.js';
import { Task } from 'shared';

const app = express();
app.use(express.json());

// Initialize storage
TaskStorage.init();

/**
 * Health check (no auth required)
 */
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'resource-server' });
});

/**
 * List all tasks
 * Requires: tasks:read scope
 */
app.get('/api/tasks', requireAuth, requireScope('tasks:read'), (req, res) => {
  const tasks = TaskStorage.getAllTasks();

  console.log(`[RESOURCE] Listed ${tasks.length} tasks for ${req.token!.sub}`);

  res.json({
    tasks,
    total: tasks.length,
  });
});

/**
 * Create a new task
 * Requires: tasks:write scope
 */
app.post('/api/tasks', requireAuth, requireScope('tasks:write'), (req, res) => {
  const { title, description, user_id } = req.body;

  if (!title) {
    return res.status(400).json({
      error: 'invalid_request',
      error_description: 'Missing required field: title',
    });
  }

  // In a real app, you'd validate that the token subject matches user_id
  // or extract user_id from the token
  const targetUserId = user_id || 'user-123'; // Default to demo user

  const task: Task = {
    id: TaskStorage.generateId(),
    user_id: targetUserId,
    title,
    description: description || '',
    status: 'pending',
    created_at: new Date(),
    created_by: req.token!.client_id,
  };

  const created = TaskStorage.createTask(task);

  console.log(`[RESOURCE] ✓ Created task ${created.id} by ${req.token!.client_id} for user ${targetUserId}`);

  res.status(201).json(created);
});

/**
 * Get a specific task
 * Requires: tasks:read scope
 */
app.get('/api/tasks/:id', requireAuth, requireScope('tasks:read'), (req, res) => {
  const task = TaskStorage.getTask(req.params.id);

  if (!task) {
    return res.status(404).json({
      error: 'not_found',
      error_description: 'Task not found',
    });
  }

  console.log(`[RESOURCE] Retrieved task ${task.id}`);

  res.json(task);
});

/**
 * Update a task
 * Requires: tasks:write scope
 */
app.put('/api/tasks/:id', requireAuth, requireScope('tasks:write'), (req, res) => {
  const { title, description, status } = req.body;

  const updates: Partial<Task> = {};
  if (title !== undefined) updates.title = title;
  if (description !== undefined) updates.description = description;
  if (status !== undefined) {
    if (!['pending', 'in_progress', 'completed'].includes(status)) {
      return res.status(400).json({
        error: 'invalid_request',
        error_description: 'Invalid status value',
      });
    }
    updates.status = status;
  }

  const updated = TaskStorage.updateTask(req.params.id, updates);

  if (!updated) {
    return res.status(404).json({
      error: 'not_found',
      error_description: 'Task not found',
    });
  }

  console.log(`[RESOURCE] ✓ Updated task ${updated.id} by ${req.token!.client_id}`);

  res.json(updated);
});

/**
 * Delete a task
 * Requires: tasks:write scope
 */
app.delete('/api/tasks/:id', requireAuth, requireScope('tasks:write'), (req, res) => {
  const deleted = TaskStorage.deleteTask(req.params.id);

  if (!deleted) {
    return res.status(404).json({
      error: 'not_found',
      error_description: 'Task not found',
    });
  }

  console.log(`[RESOURCE] ✓ Deleted task ${req.params.id} by ${req.token!.client_id}`);

  res.status(204).send();
});

/**
 * Get user information
 * Requires: user:read scope
 */
app.get('/api/user', requireAuth, requireScope('user:read'), (req, res) => {
  // In a real app, extract user from token
  const user = TaskStorage.getUser('user-123');

  if (!user) {
    return res.status(404).json({
      error: 'not_found',
      error_description: 'User not found',
    });
  }

  console.log(`[RESOURCE] Retrieved user info for ${user.id}`);

  res.json(user);
});

const PORT = 4001;
app.listen(PORT, () => {
  console.log(`
╔══════════════════════════════════════════════════════════╗
║  📦 Resource Server (Protected API)                      ║
╟──────────────────────────────────────────────────────────╢
║  Port: ${PORT}                                            ║
║  Endpoints:                                              ║
║    GET    /api/tasks      - List tasks (tasks:read)      ║
║    POST   /api/tasks      - Create task (tasks:write)    ║
║    GET    /api/tasks/:id  - Get task (tasks:read)        ║
║    PUT    /api/tasks/:id  - Update task (tasks:write)    ║
║    DELETE /api/tasks/:id  - Delete task (tasks:write)    ║
║    GET    /api/user       - Get user (user:read)         ║
║    GET    /health         - Health check (public)        ║
╟──────────────────────────────────────────────────────────╢
║  🔐 All endpoints require OAuth 2.0 Bearer token         ║
╚══════════════════════════════════════════════════════════╝
  `);
});
