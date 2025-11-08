"""
Production MCP Server
Provides resources, tools, and prompts to AI assistants via Model Context Protocol.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import os
from dataclasses import dataclass

# Note: This is a conceptual implementation
# In production, use the official MCP SDK: pip install mcp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Resource:
    """MCP Resource"""
    uri: str
    name: str
    description: str
    mime_type: str

    async def read(self) -> Dict[str, Any]:
        """Read resource content"""
        raise NotImplementedError


@dataclass
class Tool:
    """MCP Tool"""
    name: str
    description: str
    input_schema: Dict[str, Any]

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool"""
        raise NotImplementedError


@dataclass
class Prompt:
    """MCP Prompt Template"""
    name: str
    description: str
    arguments: List[Dict[str, str]]

    def render(self, **kwargs) -> str:
        """Render prompt with arguments"""
        raise NotImplementedError


class KnowledgeBaseResource(Resource):
    """Knowledge base article resource"""

    def __init__(self, article_id: str, content: str):
        super().__init__(
            uri=f"kb://articles/{article_id}",
            name=f"Article: {article_id}",
            description=f"Knowledge base article about {article_id}",
            mime_type="text/markdown"
        )
        self.content = content

    async def read(self) -> Dict[str, Any]:
        return {
            "uri": self.uri,
            "mimeType": self.mime_type,
            "text": self.content
        }


class SearchKnowledgeTool(Tool):
    """Search the knowledge base"""

    def __init__(self, knowledge_base: Dict[str, str]):
        super().__init__(
            name="search_knowledge",
            description="Search the knowledge base for relevant information",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    }
                },
                "required": ["query"]
            }
        )
        self.knowledge_base = knowledge_base

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        query = arguments["query"].lower()
        results = []

        for article_id, content in self.knowledge_base.items():
            if query in content.lower():
                results.append({
                    "article_id": article_id,
                    "snippet": content[:200] + "...",
                    "uri": f"kb://articles/{article_id}"
                })

        return {
            "results": results,
            "count": len(results)
        }


class CalculatorTool(Tool):
    """Safe calculator tool"""

    def __init__(self):
        super().__init__(
            name="calculate",
            description="Evaluate mathematical expressions safely",
            input_schema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression to evaluate (e.g., '2 + 2', '10 * 5')"
                    }
                },
                "required": ["expression"]
            }
        )

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        expression = arguments["expression"]

        # Validate expression (only allow safe characters)
        allowed_chars = set("0123456789+-*/()., ")
        if not all(c in allowed_chars for c in expression):
            return {
                "error": "Invalid characters in expression",
                "allowed": "Only numbers and operators (+, -, *, /, parentheses) allowed"
            }

        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return {
                "expression": expression,
                "result": result
            }
        except Exception as e:
            return {
                "error": str(e),
                "expression": expression
            }


class WebFetchTool(Tool):
    """Fetch web content (simulated)"""

    def __init__(self):
        super().__init__(
            name="web_fetch",
            description="Fetch content from a URL",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to fetch"
                    }
                },
                "required": ["url"]
            }
        )

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        url = arguments["url"]

        # In production, use aiohttp or httpx
        # This is a simulation
        return {
            "url": url,
            "content": f"Simulated content from {url}",
            "status": 200,
            "note": "In production, use aiohttp to actually fetch content"
        }


class ExplainConceptPrompt(Prompt):
    """Prompt for explaining concepts"""

    def __init__(self):
        super().__init__(
            name="explain_concept",
            description="Generate an explanation of a technical concept",
            arguments=[
                {"name": "concept", "description": "The concept to explain"}
            ]
        )

    def render(self, concept: str) -> str:
        return f"""Explain the concept of {concept} in a clear, concise way.

Structure your explanation as follows:
1. One-sentence definition
2. Why it's important
3. How it works (simplified)
4. Common use cases
5. Example

Concept: {concept}

Explanation:"""


class MCPServer:
    """MCP Server Implementation"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("MCP_API_KEY", "dev-key")

        # Knowledge base
        self.knowledge_base = {
            "mcp": """
            # Model Context Protocol (MCP)

            MCP is an open protocol by Anthropic that standardizes how AI
            assistants connect to data sources. It provides:

            - **Resources**: Read-only data (files, APIs, databases)
            - **Tools**: Executable functions
            - **Prompts**: Reusable templates

            Communication uses JSON-RPC 2.0. Think of it as "USB-C for AI" -
            a universal connector between AI and external systems.
            """,
            "rag": """
            # Retrieval-Augmented Generation (RAG)

            RAG enhances LLMs by retrieving relevant information before generation:

            1. **Index**: Store documents in vector database
            2. **Retrieve**: Find relevant chunks for query
            3. **Augment**: Add chunks to prompt context
            4. **Generate**: LLM creates grounded response

            Benefits: Reduces hallucinations, enables domain expertise, provides citations.
            """,
            "agents": """
            # Multi-Agent Frameworks

            Frameworks for coordinating multiple AI agents:

            - **LangGraph**: Graph-based, stateful workflows
            - **CrewAI**: Role-based agent teams
            - **AutoGen**: Conversational agents
            - **Swarm**: Lightweight coordination

            Each agent specializes in specific tasks, collaborating to solve complex problems.
            """
        }

        # Initialize resources
        self.resources: List[Resource] = [
            KnowledgeBaseResource(article_id, content)
            for article_id, content in self.knowledge_base.items()
        ]

        # Initialize tools
        self.tools: List[Tool] = [
            SearchKnowledgeTool(self.knowledge_base),
            CalculatorTool(),
            WebFetchTool()
        ]

        # Initialize prompts
        self.prompts: List[Prompt] = [
            ExplainConceptPrompt()
        ]

        # Request tracking
        self.request_count = 0
        self.start_time = datetime.now()

    def authenticate(self, api_key: str) -> bool:
        """Validate API key"""
        return api_key == self.api_key

    async def handle_list_resources(self) -> Dict[str, Any]:
        """List available resources"""
        return {
            "resources": [
                {
                    "uri": r.uri,
                    "name": r.name,
                    "description": r.description,
                    "mimeType": r.mime_type
                }
                for r in self.resources
            ]
        }

    async def handle_read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a specific resource"""
        for resource in self.resources:
            if resource.uri == uri:
                return await resource.read()

        return {"error": f"Resource not found: {uri}"}

    async def handle_list_tools(self) -> Dict[str, Any]:
        """List available tools"""
        return {
            "tools": [
                {
                    "name": t.name,
                    "description": t.description,
                    "inputSchema": t.input_schema
                }
                for t in self.tools
            ]
        }

    async def handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool"""
        for tool in self.tools:
            if tool.name == name:
                logger.info(f"Calling tool: {name} with args: {arguments}")
                result = await tool.execute(arguments)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        return {"error": f"Tool not found: {name}"}

    async def handle_list_prompts(self) -> Dict[str, Any]:
        """List available prompts"""
        return {
            "prompts": [
                {
                    "name": p.name,
                    "description": p.description,
                    "arguments": p.arguments
                }
                for p in self.prompts
            ]
        }

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request"""
        self.request_count += 1

        # Authenticate
        api_key = request.get("api_key")
        if not self.authenticate(api_key):
            return {"error": "Authentication failed", "code": 401}

        method = request.get("method")

        # Route to handlers
        if method == "resources/list":
            return await self.handle_list_resources()
        elif method == "resources/read":
            return await self.handle_read_resource(request["params"]["uri"])
        elif method == "tools/list":
            return await self.handle_list_tools()
        elif method == "tools/call":
            return await self.handle_call_tool(
                request["params"]["name"],
                request["params"]["arguments"]
            )
        elif method == "prompts/list":
            return await self.handle_list_prompts()
        else:
            return {"error": f"Unknown method: {method}"}

    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            "uptime_seconds": uptime,
            "requests_handled": self.request_count,
            "resources_available": len(self.resources),
            "tools_available": len(self.tools),
            "prompts_available": len(self.prompts)
        }


async def main():
    """Test the MCP server"""

    server = MCPServer()

    print("=" * 60)
    print("MCP Server - Testing")
    print("=" * 60)

    # Test 1: List resources
    print("\n1. List Resources")
    request = {
        "method": "resources/list",
        "api_key": "dev-key"
    }
    result = await server.handle_request(request)
    print(f"Found {len(result['resources'])} resources:")
    for r in result['resources']:
        print(f"  - {r['uri']}: {r['name']}")

    # Test 2: Read resource
    print("\n2. Read Resource")
    request = {
        "method": "resources/read",
        "params": {"uri": "kb://articles/mcp"},
        "api_key": "dev-key"
    }
    result = await server.handle_request(request)
    print(f"Content:\n{result['text'][:200]}...")

    # Test 3: List tools
    print("\n3. List Tools")
    request = {
        "method": "tools/list",
        "api_key": "dev-key"
    }
    result = await server.handle_request(request)
    print(f"Found {len(result['tools'])} tools:")
    for t in result['tools']:
        print(f"  - {t['name']}: {t['description']}")

    # Test 4: Call search tool
    print("\n4. Call Search Tool")
    request = {
        "method": "tools/call",
        "params": {
            "name": "search_knowledge",
            "arguments": {"query": "RAG"}
        },
        "api_key": "dev-key"
    }
    result = await server.handle_request(request)
    print(f"Result:\n{result['content'][0]['text']}")

    # Test 5: Call calculator
    print("\n5. Call Calculator")
    request = {
        "method": "tools/call",
        "params": {
            "name": "calculate",
            "arguments": {"expression": "2 + 2 * 10"}
        },
        "api_key": "dev-key"
    }
    result = await server.handle_request(request)
    print(f"Result:\n{result['content'][0]['text']}")

    # Test 6: Server stats
    print("\n6. Server Statistics")
    stats = server.get_stats()
    print(json.dumps(stats, indent=2))

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
