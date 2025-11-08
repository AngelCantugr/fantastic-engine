/**
 * Demo script showing the AI Agent using OAuth 2.0
 *
 * Run with: npm run demo
 */

import { TaskAgent } from './agent.js';

const AUTH_SERVER_URL = process.env.AUTH_SERVER_URL || 'http://localhost:4000';
const RESOURCE_SERVER_URL = process.env.RESOURCE_SERVER_URL || 'http://localhost:4001';
const CLIENT_ID = process.env.CLIENT_ID || 'ai-agent-assistant';
const CLIENT_SECRET = process.env.CLIENT_SECRET || 'agent-secret-67890';

async function main() {
  console.log(`
╔══════════════════════════════════════════════════════════╗
║  🤖 AI Agent OAuth 2.0 Demo                              ║
╟──────────────────────────────────────────────────────────╢
║  This demo shows an AI agent using OAuth 2.0 to          ║
║  perform actions on behalf of a user.                    ║
╚══════════════════════════════════════════════════════════╝
  `);

  const agent = new TaskAgent(
    AUTH_SERVER_URL,
    RESOURCE_SERVER_URL,
    CLIENT_ID,
    CLIENT_SECRET
  );

  try {
    // 1. Get user information
    console.log('\n--- Step 1: Get User Information ---');
    const user = await agent.getUser();
    console.log(`User: ${user.username} (${user.email})`);

    // 2. List existing tasks
    console.log('\n--- Step 2: List Existing Tasks ---');
    const tasks = await agent.listTasks();
    console.log(`Found ${tasks.length} tasks:`);
    tasks.forEach(task => {
      console.log(`  • [${task.status}] ${task.title}`);
    });

    // 3. Create a new task
    console.log('\n--- Step 3: Create New Task ---');
    const newTask = await agent.createTask(
      'Test OAuth 2.0 integration',
      'Verify that the agent can create tasks using OAuth tokens'
    );
    console.log(`Created task: ${newTask.id} - "${newTask.title}"`);

    // 4. Update the task
    console.log('\n--- Step 4: Update Task Status ---');
    const updatedTask = await agent.updateTask(newTask.id, {
      status: 'in_progress',
    });
    console.log(`Updated task status to: ${updatedTask.status}`);

    // 5. Get task summary
    console.log('\n--- Step 5: Get Task Summary ---');
    const summary = await agent.summarizeTasks();
    console.log(summary);

    // 6. Complete oldest pending task
    console.log('\n--- Step 6: Complete Oldest Pending Task ---');
    const completed = await agent.completeOldestPendingTask();
    if (completed) {
      console.log(`Completed task: ${completed.title}`);
    } else {
      console.log('No pending tasks to complete');
    }

    // 7. Get specific task
    console.log('\n--- Step 7: Get Specific Task ---');
    const task = await agent.getTask(newTask.id);
    console.log(`Task details:`, JSON.stringify(task, null, 2));

    console.log('\n✅ Demo completed successfully!');
  } catch (error) {
    console.error('\n❌ Demo failed:', error);
    process.exit(1);
  }
}

main();
