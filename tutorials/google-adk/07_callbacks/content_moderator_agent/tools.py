from typing import Dict, Any
from google.adk.tools.tool_context import ToolContext

# ============================================================================
# TOOLS
# ============================================================================

def generate_text(
    topic: str,
    word_count: int,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Generate text on a topic with specified word count.

    Args:
        topic: The subject to write about
        word_count: Desired number of words
    """
    # Tool would normally generate text here
    # For demo, just return metadata

    return {
        'status': 'success',
        'topic': topic,
        'word_count': word_count,
        'message': f'Generated {word_count}-word article on "{topic}"'
    }


def check_grammar(
    text: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Check grammar and provide corrections.

    Args:
        text: Text to check
    """
    # Simulate grammar checking
    issues_found = len(text.split()) // 10  # Fake: 1 issue per 10 words

    return {
        'status': 'success',
        'issues_found': issues_found,
        'message': f'Found {issues_found} potential grammar issues'
    }


def get_usage_stats(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Get user's usage statistics from state.

    Shows how callbacks track metrics via state.
    """
    return {
        'status': 'success',
        'request_count': tool_context.state.get('user:request_count', 0),
        'llm_calls': tool_context.state.get('user:llm_calls', 0),
        'blocked_requests': tool_context.state.get('user:blocked_requests', 0),
        'tool_generate_text_count': tool_context.state.get('user:tool_generate_text_count', 0),
        'tool_check_grammar_count': tool_context.state.get('user:tool_check_grammar_count', 0)
    }
