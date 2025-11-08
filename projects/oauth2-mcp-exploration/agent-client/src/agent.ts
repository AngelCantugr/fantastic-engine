/**
 * AI Agent with OAuth 2.0 Authentication
 *
 * This agent uses OAuth 2.0 to authenticate and perform actions
 * on behalf of the user.
 */

import { OAuthClient } from './oauth-client.js';
import { Task, User } from 'shared';

export class TaskAgent {
  private oauthClient: OAuthClient;

  constructor(
    private authServerUrl: string,
    private resourceServerUrl: string,
    private clientId: string,
    private clientSecret: string
  ) {
    this.oauthClient = new OAuthClient(
      authServerUrl,
      clientId,
      clientSecret,
      ['tasks:read', 'tasks:write', 'user:read']
    );
  }

  /**
   * List all tasks
   */
  async listTasks(): Promise<Task[]> {
    console.log('[Agent] 📋 Listing tasks...');

    const result = await this.oauthClient.authenticatedRequest<{ tasks: Task[]; total: number }>(
      'GET',
      `${this.resourceServerUrl}/api/tasks`
    );

    console.log(`[Agent] ✓ Retrieved ${result.total} tasks`);
    return result.tasks;
  }

  /**
   * Create a new task
   */
  async createTask(title: string, description?: string): Promise<Task> {
    console.log(`[Agent] ➕ Creating task: ${title}`);

    const result = await this.oauthClient.authenticatedRequest<Task>(
      'POST',
      `${this.resourceServerUrl}/api/tasks`,
      {
        title,
        description,
        user_id: 'user-123',
      }
    );

    console.log(`[Agent] ✓ Task created: ${result.id}`);
    return result;
  }

  /**
   * Get a specific task
   */
  async getTask(taskId: string): Promise<Task> {
    console.log(`[Agent] 🔍 Getting task ${taskId}`);

    const result = await this.oauthClient.authenticatedRequest<Task>(
      'GET',
      `${this.resourceServerUrl}/api/tasks/${taskId}`
    );

    console.log(`[Agent] ✓ Task retrieved`);
    return result;
  }

  /**
   * Update a task
   */
  async updateTask(
    taskId: string,
    updates: { title?: string; description?: string; status?: 'pending' | 'in_progress' | 'completed' }
  ): Promise<Task> {
    console.log(`[Agent] 🔄 Updating task ${taskId}`);

    const result = await this.oauthClient.authenticatedRequest<Task>(
      'PUT',
      `${this.resourceServerUrl}/api/tasks/${taskId}`,
      updates
    );

    console.log(`[Agent] ✓ Task updated`);
    return result;
  }

  /**
   * Delete a task
   */
  async deleteTask(taskId: string): Promise<void> {
    console.log(`[Agent] 🗑️  Deleting task ${taskId}`);

    await this.oauthClient.authenticatedRequest<void>(
      'DELETE',
      `${this.resourceServerUrl}/api/tasks/${taskId}`
    );

    console.log(`[Agent] ✓ Task deleted`);
  }

  /**
   * Get user information
   */
  async getUser(): Promise<User> {
    console.log('[Agent] 👤 Getting user information...');

    const result = await this.oauthClient.authenticatedRequest<User>(
      'GET',
      `${this.resourceServerUrl}/api/user`
    );

    console.log(`[Agent] ✓ User retrieved: ${result.username}`);
    return result;
  }

  /**
   * Agent action: Summarize user's tasks
   */
  async summarizeTasks(): Promise<string> {
    const tasks = await this.listTasks();

    const pending = tasks.filter(t => t.status === 'pending').length;
    const inProgress = tasks.filter(t => t.status === 'in_progress').length;
    const completed = tasks.filter(t => t.status === 'completed').length;

    return `
Task Summary:
- Total tasks: ${tasks.length}
- Pending: ${pending}
- In Progress: ${inProgress}
- Completed: ${completed}

Recent tasks:
${tasks.slice(0, 5).map(t => `  • [${t.status}] ${t.title}`).join('\n')}
    `.trim();
  }

  /**
   * Agent action: Complete oldest pending task
   */
  async completeOldestPendingTask(): Promise<Task | null> {
    const tasks = await this.listTasks();
    const pending = tasks
      .filter(t => t.status === 'pending')
      .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());

    if (pending.length === 0) {
      console.log('[Agent] No pending tasks to complete');
      return null;
    }

    const task = pending[0];
    return await this.updateTask(task.id, { status: 'completed' });
  }
}
