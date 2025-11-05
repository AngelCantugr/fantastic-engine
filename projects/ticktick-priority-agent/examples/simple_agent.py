"""
Simple Agent Example - Learn the Basics

This is the SIMPLEST possible LangChain agent to help you understand
how agents work before diving into the full priority agent.

Learning Goals:
1. Understand agent vs. chain
2. See how agents decide which tools to use
3. Observe the ReAct (Reasoning + Acting) loop
4. Learn how tool descriptions guide agent behavior
"""

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain_community.llms import Ollama

from rich.console import Console
from rich.panel import Panel

console = Console()


# Simple Tools for Learning
# These don't do anything complex - they're just for demonstration

def calculator_tool(expression: str) -> str:
    """
    A simple calculator tool.

    The agent can use this to perform math calculations.
    """
    try:
        # Evaluate simple math expressions
        result = eval(expression)  # Note: In production, use a safer approach!
        return f"The result is: {result}"
    except Exception as e:
        return f"Error calculating: {e}"


def greeting_tool(name: str) -> str:
    """
    A simple greeting tool.

    The agent can use this to greet people.
    """
    return f"Hello, {name}! Nice to meet you!"


def time_estimator_tool(num_tasks: str) -> str:
    """
    Estimate time needed for tasks.

    Simple heuristic: each task takes 30 minutes.
    """
    try:
        n = int(num_tasks)
        minutes = n * 30
        hours = minutes / 60
        return f"{n} tasks will take approximately {minutes} minutes ({hours:.1f} hours)"
    except:
        return "Please provide a number"


# Minimal Agent Prompt
# This is simpler than the production prompt to make it easier to understand
SIMPLE_AGENT_PROMPT = """Answer the user's question as best you can.

You have access to these tools:

{tools}

Use this format:

Question: the input question
Thought: think about what to do
Action: one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now know the final answer
Final Answer: the final answer

Question: {input}
{agent_scratchpad}
"""


def create_simple_agent():
    """
    Create a simple agent with basic tools.

    This demonstrates the minimum components needed for an agent:
    1. LLM (the "brain")
    2. Tools (the "hands")
    3. Prompt (the "instructions")
    4. Agent (the decision-maker)
    5. Executor (runs the agent)
    """
    console.print(Panel(
        "[bold]Creating a Simple Agent[/bold]\n\n"
        "This agent has 3 tools:\n"
        "  • calculator - do math\n"
        "  • greet - say hello\n"
        "  • estimate_time - estimate task duration",
        border_style="cyan"
    ))

    # 1. Create the LLM
    console.print("\n📦 [dim]Loading Ollama LLM...[/dim]")
    llm = Ollama(
        model="llama2",
        temperature=0  # Deterministic for learning
    )

    # 2. Create the tools
    # Tool descriptions are CRITICAL - the agent reads these!
    console.print("🔧 [dim]Setting up tools...[/dim]")
    tools = [
        Tool(
            name="calculator",
            func=calculator_tool,
            description=(
                "Useful for doing math calculations. "
                "Input should be a mathematical expression like '5 + 3' or '10 * 2'. "
                "Returns the numerical result."
            )
        ),
        Tool(
            name="greet",
            func=greeting_tool,
            description=(
                "Useful for greeting someone by name. "
                "Input should be a person's name. "
                "Returns a friendly greeting."
            )
        ),
        Tool(
            name="estimate_time",
            func=time_estimator_tool,
            description=(
                "Useful for estimating how long tasks will take. "
                "Input should be a number representing the number of tasks. "
                "Returns a time estimate."
            )
        ),
    ]

    # 3. Create the prompt
    console.print("📝 [dim]Creating prompt template...[/dim]")
    prompt = PromptTemplate.from_template(SIMPLE_AGENT_PROMPT)

    # 4. Create the agent
    console.print("🤖 [dim]Creating agent...[/dim]")
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    # 5. Create executor
    console.print("▶️  [dim]Creating agent executor...[/dim]")
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,  # Show the agent's thinking!
        max_iterations=3,
        handle_parsing_errors=True
    )

    console.print("\n✅ [green]Agent ready![/green]\n")

    return agent_executor


def demo_simple_queries():
    """
    Run a few demo queries to show how the agent works.

    Watch how the agent:
    1. Reads the question
    2. Thinks about which tool to use
    3. Uses the tool
    4. Observes the result
    5. Provides a final answer
    """
    agent = create_simple_agent()

    queries = [
        {
            "query": "What is 15 multiplied by 4?",
            "explanation": "Agent should use the calculator tool"
        },
        {
            "query": "Greet a person named Alice",
            "explanation": "Agent should use the greeting tool"
        },
        {
            "query": "If I have 5 tasks, how long will they take?",
            "explanation": "Agent should use the time estimator"
        },
        {
            "query": "Calculate 100 divided by 4, then greet Bob",
            "explanation": "Agent should use BOTH calculator and greeting tools!"
        }
    ]

    for i, item in enumerate(queries, 1):
        console.print("\n" + "="*80)
        console.print(f"[bold cyan]Example {i}:[/bold cyan]")
        console.print(f"[dim]{item['explanation']}[/dim]\n")

        console.print(Panel(
            item['query'],
            title="Question",
            border_style="yellow"
        ))

        # Run the agent
        result = agent.invoke({"input": item['query']})

        # Display final answer
        console.print("\n" + Panel(
            result['output'],
            title="Final Answer",
            border_style="green"
        ))

        if i < len(queries):
            input("\n[Press Enter to continue to next example...]")


def interactive_mode():
    """
    Let you try the simple agent with your own questions.
    """
    agent = create_simple_agent()

    console.print(Panel(
        "[bold]Interactive Mode[/bold]\n\n"
        "Ask the agent anything that involves:\n"
        "  • Math calculations\n"
        "  • Greeting someone\n"
        "  • Estimating task time\n\n"
        "Watch how it decides which tools to use!\n\n"
        "Type 'quit' to exit.",
        border_style="magenta"
    ))

    while True:
        try:
            query = input("\n> Your question: ").strip()

            if not query:
                continue

            if query.lower() in ['quit', 'exit', 'q']:
                break

            # Run agent
            result = agent.invoke({"input": query})

            console.print("\n" + Panel(
                result['output'],
                title="Answer",
                border_style="green"
            ))

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    console.print("\n[green]Thanks for learning about agents! 🎓[/green]")


def main():
    """Main entry point."""
    console.print(Panel.fit(
        "[bold magenta]Simple Agent Tutorial[/bold magenta]\n"
        "Learn how LangChain agents work!",
        border_style="magenta"
    ))

    console.print("\nChoose a mode:")
    console.print("  1. Demo mode (watch pre-made examples)")
    console.print("  2. Interactive mode (try your own questions)")

    choice = input("\nEnter 1 or 2: ").strip()

    if choice == "1":
        demo_simple_queries()
    elif choice == "2":
        interactive_mode()
    else:
        console.print("[yellow]Invalid choice. Running demo mode.[/yellow]")
        demo_simple_queries()


if __name__ == "__main__":
    main()
