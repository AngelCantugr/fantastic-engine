/**
 * MCP Server Hub - Central management for MCP servers
 */

import express from 'express';
import { WebSocketServer } from 'ws';
import { MCPRegistry } from './registry.js';
import { MCPPlayground } from './playground.js';
import { createServer } from 'http';

const app = express();
const server = createServer(app);
const wss = new WebSocketServer({ server });

app.use(express.json());
app.use(express.static('public'));

const registry = new MCPRegistry();
const playground = new MCPPlayground();

// API Routes
app.get('/api/servers', async (req, res) => {
  const servers = await registry.listServers();
  res.json(servers);
});

app.get('/api/servers/:id', async (req, res) => {
  const server = await registry.getServer(req.params.id);
  if (!server) {
    return res.status(404).json({ error: 'Server not found' });
  }
  res.json(server);
});

app.post('/api/servers', async (req, res) => {
  try {
    const server = await registry.addServer(req.body);
    res.status(201).json(server);
  } catch (error: any) {
    res.status(400).json({ error: error.message });
  }
});

app.post('/api/servers/:id/install', async (req, res) => {
  try {
    await registry.installServer(req.params.id);
    res.json({ status: 'installed' });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

app.delete('/api/servers/:id', async (req, res) => {
  await registry.deleteServer(req.params.id);
  res.json({ status: 'deleted' });
});

// Playground routes
app.post('/api/playground/test', async (req, res) => {
  try {
    const result = await playground.testServer(req.body.serverId, req.body.tool, req.body.args);
    res.json(result);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/playground/servers/:id/tools', async (req, res) => {
  try {
    const tools = await playground.getServerTools(req.params.id);
    res.json(tools);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// WebSocket for real-time updates
wss.on('connection', (ws) => {
  console.log('Client connected to MCP Hub');

  ws.on('message', async (message) => {
    try {
      const data = JSON.parse(message.toString());

      if (data.type === 'subscribe') {
        // Subscribe to server updates
        ws.send(JSON.stringify({ type: 'subscribed', serverId: data.serverId }));
      }
    } catch (error) {
      console.error('WebSocket error:', error);
    }
  });

  ws.on('close', () => {
    console.log('Client disconnected');
  });
});

const PORT = process.env.PORT || 3001;

server.listen(PORT, () => {
  console.log(`🔌 MCP Server Hub running on http://localhost:${PORT}`);
});

export { app, server };
