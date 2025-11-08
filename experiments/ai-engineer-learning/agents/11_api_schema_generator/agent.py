#!/usr/bin/env python3
"""
Agent 11: API Schema Generator
================================

Learning Objectives:
- Generate OpenAPI/Swagger specifications
- Infer API schemas from code
- Understand REST API documentation
- Use Pydantic for schema validation

Complexity: ⭐ Beginner-Intermediate
Framework: pydantic + ollama
"""

import sys
import ast
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from langchain_ollama import OllamaLLM
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


@dataclass
class APIEndpoint:
    """Represents an API endpoint."""
    path: str
    method: str
    function_name: str
    parameters: List[Dict[str, Any]]
    returns: Optional[str]
    description: Optional[str]


class APISchemaGenerator:
    """
    Generate OpenAPI schemas from Python code.

    Demonstrates:
    1. Code analysis for API endpoints
    2. Schema inference from type hints
    3. OpenAPI spec generation
    4. Documentation automation
    """

    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.llm = OllamaLLM(model=model, temperature=0.2)
        self.endpoints: List[APIEndpoint] = []

    def analyze_file(self, file_path: Path) -> List[APIEndpoint]:
        """Analyze Python file for API endpoints."""
        code = file_path.read_text()
        tree = ast.parse(code)

        endpoints = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for route decorators (Flask/FastAPI style)
                endpoint = self._extract_endpoint(node)
                if endpoint:
                    endpoints.append(endpoint)

        return endpoints

    def _extract_endpoint(self, node: ast.FunctionDef) -> Optional[APIEndpoint]:
        """Extract API endpoint info from function."""
        # Look for route decorators
        route_info = None
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if hasattr(decorator.func, 'attr'):
                    # @app.get('/path'), @app.post('/path'), etc.
                    method = decorator.func.attr.upper()
                    if decorator.args and isinstance(decorator.args[0], ast.Constant):
                        path = decorator.args[0].value
                        route_info = (path, method)

        if not route_info:
            return None

        path, method = route_info

        # Extract parameters
        parameters = []
        for arg in node.args.args:
            param_info = {
                "name": arg.arg,
                "type": ast.unparse(arg.annotation) if arg.annotation else "any",
                "required": True
            }
            parameters.append(param_info)

        # Extract return type
        returns = ast.unparse(node.returns) if node.returns else None

        # Extract docstring
        description = ast.get_docstring(node)

        return APIEndpoint(
            path=path,
            method=method,
            function_name=node.name,
            parameters=parameters,
            returns=returns,
            description=description
        )

    def generate_openapi_spec(
        self,
        endpoints: List[APIEndpoint],
        title: str = "Generated API",
        version: str = "1.0.0"
    ) -> Dict[str, Any]:
        """Generate OpenAPI 3.0 specification."""

        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": title,
                "version": version,
                "description": "Auto-generated API documentation"
            },
            "paths": {}
        }

        for endpoint in endpoints:
            if endpoint.path not in spec["paths"]:
                spec["paths"][endpoint.path] = {}

            # Build operation
            operation = {
                "summary": endpoint.function_name.replace('_', ' ').title(),
                "description": endpoint.description or "No description provided",
                "parameters": [],
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        }
                    }
                }
            }

            # Add parameters
            for param in endpoint.parameters:
                if param["name"] not in ["self", "request", "response"]:
                    operation["parameters"].append({
                        "name": param["name"],
                        "in": "query",
                        "required": param["required"],
                        "schema": {"type": self._map_type(param["type"])}
                    })

            spec["paths"][endpoint.path][endpoint.method.lower()] = operation

        return spec

    def _map_type(self, python_type: str) -> str:
        """Map Python types to OpenAPI types."""
        type_map = {
            "str": "string",
            "int": "integer",
            "float": "number",
            "bool": "boolean",
            "list": "array",
            "dict": "object",
            "List": "array",
            "Dict": "object",
        }
        return type_map.get(python_type, "string")

    def enhance_with_ai(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to enhance descriptions and add examples."""

        prompt = f"""Analyze this OpenAPI specification and enhance it with:
1. Better descriptions for each endpoint
2. Example request/response payloads
3. Common error codes

Current spec:
{json.dumps(spec, indent=2)}

Return the enhanced OpenAPI spec as valid JSON."""

        try:
            response = self.llm.invoke(prompt)
            # Try to extract JSON from response
            enhanced = json.loads(response)
            return enhanced
        except Exception as e:
            console.print(f"[yellow]Could not enhance with AI: {e}[/yellow]")
            return spec


def main():
    import argparse

    parser = argparse.ArgumentParser(description="API Schema Generator")
    parser.add_argument("--file", type=Path, help="Python file with API routes")
    parser.add_argument("--output", type=Path, help="Output file (JSON or YAML)")
    parser.add_argument("--title", default="My API", help="API title")
    parser.add_argument("--enhance", action="store_true", help="Enhance with AI")
    parser.add_argument("--model", default="qwen2.5-coder:7b")

    args = parser.parse_args()

    if not args.file:
        console.print("[red]Error: --file is required[/red]")
        parser.print_help()
        sys.exit(1)

    try:
        generator = APISchemaGenerator(model=args.model)

        console.print(Panel.fit(
            "[bold cyan]API Schema Generator[/bold cyan]\n\n"
            f"File: [yellow]{args.file}[/yellow]"
        ))

        # Analyze file
        console.print("\n[cyan]Analyzing API endpoints...[/cyan]")
        endpoints = generator.analyze_file(args.file)

        if not endpoints:
            console.print("[yellow]No API endpoints found. "
                         "Make sure your code has route decorators.[/yellow]")
            sys.exit(0)

        console.print(f"[green]Found {len(endpoints)} endpoints[/green]")
        for ep in endpoints:
            console.print(f"  • {ep.method} {ep.path} - {ep.function_name}")

        # Generate spec
        console.print("\n[cyan]Generating OpenAPI specification...[/cyan]")
        spec = generator.generate_openapi_spec(endpoints, title=args.title)

        # Enhance with AI if requested
        if args.enhance:
            console.print("[cyan]Enhancing with AI...[/cyan]")
            spec = generator.enhance_with_ai(spec)

        # Output
        if args.output:
            output_format = args.output.suffix.lower()
            if output_format == '.yaml' or output_format == '.yml':
                args.output.write_text(yaml.dump(spec, sort_keys=False))
            else:
                args.output.write_text(json.dumps(spec, indent=2))
            console.print(f"\n[green]✓ Saved to {args.output}[/green]")
        else:
            # Print to console
            console.print("\n[bold]Generated OpenAPI Spec:[/bold]\n")
            console.print(Syntax(json.dumps(spec, indent=2), "json", theme="monokai"))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
