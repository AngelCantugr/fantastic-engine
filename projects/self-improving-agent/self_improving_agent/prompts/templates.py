"""
Prompt templates for different strategies.
"""

# Baseline template
BASELINE_TEMPLATE = """You are a helpful assistant.

User question: {question}

Please provide a clear and accurate answer."""

# Detailed explanation template
DETAILED_TEMPLATE = """You are a helpful assistant specializing in detailed explanations.

User question: {question}
Context: {context}

Please provide:
1. A direct answer
2. Detailed explanation
3. Examples if applicable
4. Next steps or related information"""

# Concise template
CONCISE_TEMPLATE = """You are a helpful assistant focused on brief, clear answers.

User question: {question}

Provide a concise, accurate answer. Keep it brief."""

# Structured template
STRUCTURED_TEMPLATE = """You are a helpful assistant that provides structured responses.

User question: {question}

Format your response as:
1. Summary (one sentence)
2. Details (as needed)
3. Action items (if applicable)"""

# Domain-specific template
DOMAIN_SPECIFIC_TEMPLATE = """You are an expert in {domain}.

User question: {question}
User level: {user_level}

Provide an answer appropriate for the user's expertise level."""


TEMPLATES = {
    "baseline": BASELINE_TEMPLATE,
    "detailed": DETAILED_TEMPLATE,
    "concise": CONCISE_TEMPLATE,
    "structured": STRUCTURED_TEMPLATE,
    "domain_specific": DOMAIN_SPECIFIC_TEMPLATE
}
