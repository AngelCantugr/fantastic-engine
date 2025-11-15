/**
 * MCP Server Registry - Manage available MCP servers
 */

import { z } from 'zod';
import * as fs from 'fs/promises';
import * as path from 'path';

const MCPServerSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  version: z.string(),
  author: z.string().optional(),
  repository: z.string().url().optional(),
  command: z.string(),
  args: z.array(z.string()).optional(),
  env: z.record(z.string()).optional(),
  installed: z.boolean().default(false),
  tools: z.array(z.object({
    name: z.string(),
    description: z.string(),
    inputSchema: z.any(),
  })).optional(),
});

export type MCPServer = z.infer<typeof MCPServerSchema>;

export class MCPRegistry {
  private serversFile = path.join(process.cwd(), 'data', 'servers.json');
  private servers: Map<string, MCPServer> = new Map();

  constructor() {
    this.loadServers();
  }

  private async loadServers() {
    try {
      const data = await fs.readFile(this.serversFile, 'utf-8');
      const servers = JSON.parse(data);
      servers.forEach((server: MCPServer) => {
        this.servers.set(server.id, server);
      });
    } catch (error) {
      // Initialize with default servers
      await this.initializeDefaults();
    }
  }

  private async initializeDefaults() {
    const defaultServers: MCPServer[] = [
      {
        id: 'filesystem',
        name: 'File System MCP',
        description: 'Read and write files on the local filesystem',
        version: '1.0.0',
        command: 'npx',
        args: ['-y', '@modelcontextprotocol/server-filesystem', process.cwd()],
        installed: false,
        tools: [
          {
            name: 'read_file',
            description: 'Read contents of a file',
            inputSchema: {
              type: 'object',
              properties: {
                path: { type: 'string', description: 'File path' },
              },
              required: ['path'],
            },
          },
          {
            name: 'write_file',
            description: 'Write contents to a file',
            inputSchema: {
              type: 'object',
              properties: {
                path: { type: 'string', description: 'File path' },
                content: { type: 'string', description: 'File content' },
              },
              required: ['path', 'content'],
            },
          },
        ],
      },
      {
        id: 'github',
        name: 'GitHub MCP',
        description: 'Interact with GitHub API',
        version: '1.0.0',
        command: 'npx',
        args: ['-y', '@modelcontextprotocol/server-github'],
        env: {
          GITHUB_TOKEN: process.env.GITHUB_TOKEN || '',
        },
        installed: false,
        tools: [
          {
            name: 'create_issue',
            description: 'Create a GitHub issue',
            inputSchema: {
              type: 'object',
              properties: {
                repo: { type: 'string' },
                title: { type: 'string' },
                body: { type: 'string' },
              },
              required: ['repo', 'title'],
            },
          },
        ],
      },
      {
        id: 'postgres',
        name: 'PostgreSQL MCP',
        description: 'Query PostgreSQL databases',
        version: '1.0.0',
        command: 'npx',
        args: ['-y', '@modelcontextprotocol/server-postgres'],
        env: {
          DATABASE_URL: process.env.DATABASE_URL || '',
        },
        installed: false,
      },
    ];

    for (const server of defaultServers) {
      this.servers.set(server.id, server);
    }

    await this.saveServers();
  }

  private async saveServers() {
    await fs.mkdir(path.dirname(this.serversFile), { recursive: true });
    const servers = Array.from(this.servers.values());
    await fs.writeFile(this.serversFile, JSON.stringify(servers, null, 2));
  }

  async listServers(): Promise<MCPServer[]> {
    return Array.from(this.servers.values());
  }

  async getServer(id: string): Promise<MCPServer | undefined> {
    return this.servers.get(id);
  }

  async addServer(serverData: Partial<MCPServer>): Promise<MCPServer> {
    if (!serverData.id || !serverData.name || !serverData.command) {
      throw new Error('Missing required fields: id, name, command');
    }

    const server = MCPServerSchema.parse({
      ...serverData,
      installed: false,
    });

    this.servers.set(server.id, server);
    await this.saveServers();

    return server;
  }

  async updateServer(id: string, updates: Partial<MCPServer>): Promise<MCPServer> {
    const server = this.servers.get(id);
    if (!server) {
      throw new Error(`Server ${id} not found`);
    }

    const updated = { ...server, ...updates };
    this.servers.set(id, updated);
    await this.saveServers();

    return updated;
  }

  async deleteServer(id: string): Promise<void> {
    this.servers.delete(id);
    await this.saveServers();
  }

  async installServer(id: string): Promise<void> {
    const server = this.servers.get(id);
    if (!server) {
      throw new Error(`Server ${id} not found`);
    }

    // In a real implementation, this would:
    // 1. Download/install the server package
    // 2. Verify it works
    // 3. Update Claude Code config

    server.installed = true;
    await this.saveServers();
  }
}
