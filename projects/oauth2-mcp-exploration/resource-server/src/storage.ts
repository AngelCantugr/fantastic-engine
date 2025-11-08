/**
 * In-memory storage for user tasks
 */

import { Task, User } from 'shared';
import { randomBytes } from 'crypto';

export class TaskStorage {
  private static tasks = new Map<string, Task>();
  private static users = new Map<string, User>();

  static init() {
    // Create demo user
    this.users.set('user-123', {
      id: 'user-123',
      username: 'demo-user',
      email: 'demo@example.com',
      created_at: new Date(),
    });

    // Create some initial tasks
    this.createTask({
      id: 'task-1',
      user_id: 'user-123',
      title: 'Learn OAuth 2.0',
      description: 'Understand how OAuth 2.0 works with MCP and agents',
      status: 'in_progress',
      created_at: new Date(),
      created_by: 'system',
    });

    this.createTask({
      id: 'task-2',
      user_id: 'user-123',
      title: 'Build demo project',
      description: 'Create a working OAuth 2.0 demo',
      status: 'completed',
      created_at: new Date(Date.now() - 86400000), // 1 day ago
      created_by: 'system',
    });
  }

  // Task methods
  static createTask(task: Task): Task {
    this.tasks.set(task.id, task);
    return task;
  }

  static getTask(taskId: string): Task | undefined {
    return this.tasks.get(taskId);
  }

  static getUserTasks(userId: string): Task[] {
    return Array.from(this.tasks.values()).filter(task => task.user_id === userId);
  }

  static getAllTasks(): Task[] {
    return Array.from(this.tasks.values());
  }

  static updateTask(taskId: string, updates: Partial<Task>): Task | null {
    const task = this.tasks.get(taskId);
    if (!task) return null;

    const updated = { ...task, ...updates };
    this.tasks.set(taskId, updated);
    return updated;
  }

  static deleteTask(taskId: string): boolean {
    return this.tasks.delete(taskId);
  }

  static generateId(): string {
    return `task-${randomBytes(8).toString('hex')}`;
  }

  // User methods
  static getUser(userId: string): User | undefined {
    return this.users.get(userId);
  }
}
