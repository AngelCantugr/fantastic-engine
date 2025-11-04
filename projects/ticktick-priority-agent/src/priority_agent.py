"""
TickTick Priority Agent

This is the main agent that helps prioritize your tasks.

It uses:
- LangChain's ReAct agent (Reasoning + Acting)
- Multiple tools for TickTick operations
- Ollama for local LLM inference

Learning Note: Agents are more powerful than chains because they can:
1. Decide which tools to use
2. Use tools multiple times
3. Adapt based on observations
4. Have emergent behavior
"""

import os
from typing import List

from dotenv import load_dotenv

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from ticktick_tools import create_tools_from_env

console = Console()


# Agent System Prompt
# This is CRITICAL - it defines the agent's behavior and capabilities
AGENT_SYSTEM_PROMPT = """You are a helpful productivity assistant that helps users prioritize their TickTick tasks.

Your goal is to analyze the user's tasks and provide actionable recommendations for what to work on next.

You have access to these tools:
{tools}

Tool descriptions:
{tool_names}

When the user asks for help:
1. First, fetch their tasks using the fetch_tasks tool
2. If needed, analyze specific tasks in detail
3. Consider multiple factors: urgency, importance, complexity
4. Provide clear, actionable recommendations

Use this format:

Question: the input question you must answer
Thought: think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Important guidelines:
- Be concise but thorough
- Explain your reasoning
- Use the Eisenhower Matrix (urgent/important) when relevant
- Consider the user's context (time of day, energy level if mentioned)
- Suggest starting with quick wins when appropriate
- Don't be afraid to recommend postponing or delegating tasks

Begin!

Question: {input}
Thought: {agent_scratchpad}
"""


class PriorityAgent:
    """
    Main agent for task prioritization.

    This agent uses ReAct (Reasoning + Acting) to decide which tools
    to use and how to analyze tasks.
    """

    def __init__(self, model: str = "llama2", verbose: bool = True):
        """
        Initialize the priority agent.

        Args:
            model: Ollama model name (e.g., "llama2", "mistral", "neural-chat")
            verbose: Whether to show agent's reasoning process
        """
        console.print("🤖 Initializing Priority Agent...")

        # Setup LLM
        self.llm = Ollama(
            model=model,
            temperature=0.1,  # Low temperature for consistent reasoning
        )
        console.print(f"  • Using model: {model}")

        # Setup tools
        self.tools_wrapper = create_tools_from_env()
        self.tools = self.tools_wrapper.get_langchain_tools()
        console.print(f"  • Loaded {len(self.tools)} tools")

        # Create prompt
        self.prompt = PromptTemplate.from_template(AGENT_SYSTEM_PROMPT)

        # Create agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )

        # Create executor (this runs the agent)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=verbose,
            max_iterations=5,  # Prevent infinite loops
            handle_parsing_errors=True,  # Graceful error handling
        )

        console.print("✅ Agent ready!\n")

    def prioritize_tasks(self, user_query: str = None) -> str:
        """
        Main method to get task prioritization recommendations.

        Args:
            user_query: Optional specific question from user

        Returns:
            Agent's response with prioritization recommendations
        """
        if not user_query:
            user_query = (
                "Please analyze my tasks and tell me what I should work on next. "
                "Provide a prioritized list with reasoning."
            )

        console.print(Panel(
            f"[bold]Query:[/bold] {user_query}",
            title="🎯 Task Prioritization",
            border_style="cyan"
        ))

        try:
            # Run the agent
            result = self.agent_executor.invoke({"input": user_query})

            # Extract and display answer
            answer = result.get("output", "No response generated")

            console.print("\n" + Panel(
                Markdown(answer),
                title="✨ Agent Response",
                border_style="green"
            ))

            return answer

        except Exception as e:
            error_msg = f"Error running agent: {str(e)}"
            console.print(f"\n[red]{error_msg}[/red]")
            return error_msg

    def interactive_mode(self):
        """
        Run the agent in interactive mode where users can ask questions.
        """
        console.print(Panel(
            "[bold cyan]Interactive Priority Agent[/bold cyan]\n\n"
            "Ask me anything about your tasks!\n\n"
            "Example questions:\n"
            "  • What should I work on next?\n"
            "  • Which tasks are most urgent?\n"
            "  • Give me some quick wins\n"
            "  • What's my most important task?\n\n"
            "Type 'quit' to exit.",
            border_style="magenta"
        ))

        while True:
            try:
                # Get user input
                user_input = console.input("\n[bold yellow]Your question:[/bold yellow] ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', 'q']:
                    console.print("\n[green]Thanks for using Priority Agent! Stay productive! 🚀[/green]")
                    break

                # Process query
                self.prioritize_tasks(user_input)

            except KeyboardInterrupt:
                console.print("\n[green]Goodbye! 👋[/green]")
                break
            except Exception as e:
                console.print(f"\n[red]Error: {e}[/red]")


def main():
    """Main entry point for the priority agent."""
    load_dotenv()

    console.print(Panel.fit(
        "[bold magenta]TickTick Priority Agent[/bold magenta]\n"
        "Your AI-powered productivity assistant",
        border_style="magenta"
    ))

    # Get configuration from environment
    model = os.getenv("OLLAMA_MODEL", "llama2")
    verbose = os.getenv("AGENT_VERBOSE", "true").lower() == "true"

    try:
        # Create agent
        agent = PriorityAgent(model=model, verbose=verbose)

        # Run in interactive mode
        agent.interactive_mode()

    except Exception as e:
        console.print(f"\n[red]Failed to start agent: {e}[/red]")
        console.print("\n[yellow]Make sure:[/yellow]")
        console.print("  1. Ollama is running (ollama serve)")
        console.print("  2. Model is pulled (ollama pull llama2)")
        console.print("  3. Environment variables are set (.env file)")
        console.print("  4. TickTick credentials are correct")


if __name__ == "__main__":
    main()
