#!/usr/bin/env python3
"""Agent 18: Infrastructure Generator - Generate IaC (Terraform, K8s, etc.)."""

import sys
from pathlib import Path
from langchain_ollama import OllamaLLM
from rich.console import Console
from rich.syntax import Syntax

console = Console()

class InfrastructureGenerator:
    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.llm = OllamaLLM(model=model, temperature=0.2)

    def generate_terraform(self, description: str, cloud: str = "aws") -> str:
        """Generate Terraform configuration."""
        prompt = f"""Generate Terraform configuration for {cloud}:

Application description: {description}

Include:
1. Provider configuration
2. Network setup (VPC, subnets)
3. Compute resources
4. Load balancers
5. Security groups
6. Outputs

Provide complete, production-ready Terraform code.
"""
        return self.llm.invoke(prompt)

    def generate_kubernetes(self, app_name: str, replicas: int = 3) -> str:
        """Generate Kubernetes manifests."""
        prompt = f"""Generate Kubernetes manifests for application: {app_name}

Requirements:
- {replicas} replicas
- Deployment, Service, Ingress
- ConfigMap and Secrets
- Resource limits
- Health checks
- HPA (Horizontal Pod Autoscaler)

Provide complete YAML manifests.
"""
        return self.llm.invoke(prompt)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Infrastructure Generator")
    parser.add_argument("--type", choices=["terraform", "k8s", "docker-compose"], required=True)
    parser.add_argument("--app", required=True, help="Application name/description")
    parser.add_argument("--cloud", default="aws", choices=["aws", "gcp", "azure"])
    parser.add_argument("--replicas", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    generator = InfrastructureGenerator()

    if args.type == "terraform":
        console.print("[cyan]Generating Terraform configuration...[/cyan]\n")
        code = generator.generate_terraform(args.app, args.cloud)
    elif args.type == "k8s":
        console.print("[cyan]Generating Kubernetes manifests...[/cyan]\n")
        code = generator.generate_kubernetes(args.app, args.replicas)

    if args.output:
        args.output.write_text(code)
        console.print(f"[green]✓ Saved to {args.output}[/green]")
    else:
        console.print(Syntax(code, "yaml", theme="monokai"))

if __name__ == "__main__":
    main()
