#!/usr/bin/env python3
"""Agent 28: Tech Blog Writer."""

from langchain_ollama import OllamaLLM
from rich.console import Console

console = Console()

class TechBlogWriter:
    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.llm = OllamaLLM(model=model, temperature=0.7)

    def generate_article(self, topic: str) -> str:
        """Generate technical blog post."""
        prompt = f"""Write a technical blog post about: {topic}

Structure:
1. Catchy title
2. Introduction (hook the reader)
3. Main content with code examples
4. Practical takeaways
5. Conclusion
6. Call to action

Make it:
- Easy to understand
- Code-heavy with explanations
- SEO-friendly
- Engaging for developers
"""
        return self.llm.invoke(prompt)

    def code_to_blog(self, code: str, project_desc: str) -> str:
        """Turn code into a blog post."""
        prompt = f"""Turn this code project into a blog post:

Project: {project_desc}

Code:
```python
{code}
```

Create an engaging technical article explaining:
- What problem it solves
- How it works
- Key implementation details
- Code walkthrough
- Lessons learned
"""
        return self.llm.invoke(prompt)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Tech Blog Writer")
    parser.add_argument("--topic", help="Blog topic")
    parser.add_argument("--code-to-blog", type=str, help="Convert code to blog")
    args = parser.parse_args()

    writer = TechBlogWriter()

    if args.topic:
        article = writer.generate_article(args.topic)
        console.print(article)
    elif args.code_to_blog:
        from pathlib import Path
        code = Path(args.code_to_blog).read_text()
        article = writer.code_to_blog(code, "My project")
        console.print(article)

if __name__ == "__main__":
    main()
