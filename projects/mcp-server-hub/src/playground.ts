/**
 * MCP Playground - Test MCP servers and tools
 */

import { spawn } from 'child_process';
import { MCPRegistry } from './registry.js';

export class MCPPlayground {
  private registry: MCPRegistry;

  constructor() {
    this.registry = new MCPRegistry();
  }

  async getServerTools(serverId: string) {
    const server = await this.registry.getServer(serverId);
    if (!server) {
      throw new Error(`Server ${serverId} not found`);
    }

    return server.tools || [];
  }

  async testServer(serverId: string, toolName: string, args: any) {
    const server = await this.registry.getServer(serverId);
    if (!server) {
      throw new Error(`Server ${serverId} not found`);
    }

    // Simulate MCP protocol communication
    const result = await this.executeTool(server, toolName, args);
    return result;
  }

  private async executeTool(server: any, toolName: string, args: any): Promise<any> {
    return new Promise((resolve, reject) => {
      const child = spawn(server.command, server.args || [], {
        env: { ...process.env, ...server.env },
      });

      let stdout = '';
      let stderr = '';

      child.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      child.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      // Send MCP request
      const request = {
        jsonrpc: '2.0',
        id: 1,
        method: 'tools/call',
        params: {
          name: toolName,
          arguments: args,
        },
      };

      child.stdin.write(JSON.stringify(request) + '\n');
      child.stdin.end();

      child.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`Tool execution failed: ${stderr}`));
        } else {
          try {
            const response = JSON.parse(stdout);
            resolve(response.result);
          } catch (error) {
            resolve({ output: stdout });
          }
        }
      });

      setTimeout(() => {
        child.kill();
        reject(new Error('Tool execution timed out'));
      }, 30000);
    });
  }

  async discoverTools(serverId: string) {
    const server = await this.registry.getServer(serverId);
    if (!server) {
      throw new Error(`Server ${serverId} not found`);
    }

    // Send tools/list request to MCP server
    return new Promise((resolve, reject) => {
      const child = spawn(server.command, server.args || [], {
        env: { ...process.env, ...server.env },
      });

      const request = {
        jsonrpc: '2.0',
        id: 1,
        method: 'tools/list',
      };

      child.stdin.write(JSON.stringify(request) + '\n');
      child.stdin.end();

      let stdout = '';

      child.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      child.on('close', () => {
        try {
          const response = JSON.parse(stdout);
          resolve(response.result?.tools || []);
        } catch (error) {
          reject(error);
        }
      });
    });
  }
}
