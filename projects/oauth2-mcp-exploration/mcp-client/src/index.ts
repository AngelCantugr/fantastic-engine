/**
 * MCP Server with OAuth 2.0 Authentication
 *
 * This MCP server uses OAuth 2.0 to authenticate with the resource server
 * and provides tools for managing tasks on behalf of the user.
 *
 * Tools:
 * - list_tasks: List all tasks
 * - create_task: Create a new task
 * - update_task: Update task status
 * - get_user: Get user information
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { OAuthClient } from './oauth-client.js';
import { Task, User } from 'shared';

const AUTH_SERVER_URL = process.env.AUTH_SERVER_URL || 'http://localhost:4000';
const RESOURCE_SERVER_URL = process.env.RESOURCE_SERVER_URL || 'http://localhost:4001';
const CLIENT_ID = process.env.CLIENT_ID || 'mcp-task-manager';
const CLIENT_SECRET = process.env.CLIENT_SECRET || 'mcp-secret-12345';

// Initialize OAuth client
const oauthClient = new OAuthClient(
  AUTH_SERVER_URL,
  CLIENT_ID,
  CLIENT_SECRET,
  ['tasks:read', 'tasks:write']
);

// Initialize MCP server
const server = new Server(
  {
    name: 'oauth2-task-manager',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

/**
 * List available tools
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'list_tasks',
        description: 'List all tasks from the task management system',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'create_task',
        description: 'Create a new task for the user',
        inputSchema: {
          type: 'object',
          properties: {
            title: {
              type: 'string',
              description: 'Task title',
            },
            description: {
              type: 'string',
              description: 'Task description',
            },
          },
          required: ['title'],
        },
      },
      {
        name: 'update_task',
        description: 'Update a task status',
        inputSchema: {
          type: 'object',
          properties: {
            task_id: {
              type: 'string',
              description: 'Task ID to update',
            },
            status: {
              type: 'string',
              enum: ['pending', 'in_progress', 'completed'],
              description: 'New status',
            },
          },
          required: ['task_id', 'status'],
        },
      },
      {
        name: 'get_task',
        description: 'Get details of a specific task',
        inputSchema: {
          type: 'object',
          properties: {
            task_id: {
              type: 'string',
              description: 'Task ID to retrieve',
            },
          },
          required: ['task_id'],
        },
      },
    ],
  };
});

/**
 * Handle tool calls
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'list_tasks': {
        console.error('[MCP] 📋 Listing tasks...');
        const result = await oauthClient.authenticatedRequest<{ tasks: Task[]; total: number }>(
          'GET',
          `${RESOURCE_SERVER_URL}/api/tasks`
        );

        console.error(`[MCP] ✓ Retrieved ${result.total} tasks`);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'create_task': {
        const { title, description } = args as { title: string; description?: string };

        console.error(`[MCP] ➕ Creating task: ${title}`);

        const result = await oauthClient.authenticatedRequest<Task>(
          'POST',
          `${RESOURCE_SERVER_URL}/api/tasks`,
          {
            title,
            description,
            user_id: 'user-123', // In real app, get from token
          }
        );

        console.error(`[MCP] ✓ Task created: ${result.id}`);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'update_task': {
        const { task_id, status } = args as { task_id: string; status: string };

        console.error(`[MCP] 🔄 Updating task ${task_id} to ${status}`);

        const result = await oauthClient.authenticatedRequest<Task>(
          'PUT',
          `${RESOURCE_SERVER_URL}/api/tasks/${task_id}`,
          { status }
        );

        console.error(`[MCP] ✓ Task updated`);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'get_task': {
        const { task_id } = args as { task_id: string };

        console.error(`[MCP] 🔍 Getting task ${task_id}`);

        const result = await oauthClient.authenticatedRequest<Task>(
          'GET',
          `${RESOURCE_SERVER_URL}/api/tasks/${task_id}`
        );

        console.error(`[MCP] ✓ Task retrieved`);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    console.error(`[MCP] ✗ Error: ${error}`);

    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        },
      ],
      isError: true,
    };
  }
});

/**
 * Start the server
 */
async function main() {
  console.error(`
╔══════════════════════════════════════════════════════════╗
║  🔧 MCP Server with OAuth 2.0                            ║
╟──────────────────────────────────────────────────────────╢
║  Client ID: ${CLIENT_ID}                   ║
║  Auth Server: ${AUTH_SERVER_URL}                ║
║  Resource Server: ${RESOURCE_SERVER_URL}            ║
║  Scopes: tasks:read, tasks:write                         ║
╟──────────────────────────────────────────────────────────╢
║  Available Tools:                                        ║
║    • list_tasks    - List all tasks                      ║
║    • create_task   - Create a new task                   ║
║    • update_task   - Update task status                  ║
║    • get_task      - Get task details                    ║
╚══════════════════════════════════════════════════════════╝
  `);

  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('[MCP] Server running on stdio');
}

main().catch((error) => {
  console.error('[MCP] Fatal error:', error);
  process.exit(1);
});
