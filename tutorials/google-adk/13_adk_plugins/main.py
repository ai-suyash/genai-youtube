import argparse
import asyncio

from google.adk.events import Event
from google.adk.plugins.logging_plugin import LoggingPlugin
from google.adk.runners import InMemoryRunner
from google.genai import types
from dotenv import load_dotenv

from support_ops_agent.agent import root_agent
from support_ops_agent.plugins import RefundGuardrailPlugin

APP_NAME = "support_ops_plugins_demo"
USER_ID = "demo_user"
SESSION_ID = "support_ops_session"


def parse_args() -> argparse.Namespace:
    """Parse command-line options for the plugin tutorial demo.

    Returns:
        Parsed CLI arguments controlling prompt selection and guardrail behavior.
    """
    parser = argparse.ArgumentParser(description="Run the Google ADK plugins tutorial demo.")
    parser.add_argument(
        "--prompt",
        help="Single prompt to run. If omitted, an interactive terminal session is started.",
    )
    parser.add_argument(
        "--manager-mode",
        action="store_true",
        help="Allow refunds above the guardrail threshold.",
    )
    parser.add_argument(
        "--refund-threshold",
        type=float,
        default=100.0,
        help="Maximum refund amount allowed without manager approval.",
    )
    return parser.parse_args()


def event_to_lines(event: Event) -> list[str]:
    """Convert an ADK event into readable terminal output lines.

    Args:
        event: Event emitted by the ADK runner during execution.

    Returns:
        A list of formatted strings representing model text, tool results,
        and any state changes attached to the event.
    """
    # ADK emits structured events; this helper flattens the pieces we care about
    # into simple terminal-friendly lines for the tutorial walkthrough.
    lines: list[str] = []
    author = getattr(event, "author", "unknown")
    content = getattr(event, "content", None)
    if content and getattr(content, "parts", None):
        for part in content.parts:
            text = getattr(part, "text", None)
            if text:
                lines.append(f"[{author}] {text}")
            function_response = getattr(part, "function_response", None)
            if function_response:
                name = getattr(function_response, "name", "tool")
                response = getattr(function_response, "response", {})
                lines.append(f"[{author}] {name} -> {response}")
    actions = getattr(event, "actions", None)
    state_delta = getattr(actions, "state_delta", None) if actions else None
    if state_delta:
        lines.append(f"[state] {state_delta}")
    return lines


async def run_prompt(runner: InMemoryRunner, prompt: str) -> None:
    """Send a single user prompt through the runner and print streamed events.

    Args:
        runner: Configured in-memory ADK runner.
        prompt: User prompt to execute against the demo agent.
    """
    # We stream runner events so viewers can see the agent response, tool activity,
    # and plugin side effects as they happen.
    print(f"\n=== User ===\n{prompt}")
    user_message = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=user_message,
    ):
        for line in event_to_lines(event):
            print(line)


async def run_interactive_shell(runner: InMemoryRunner) -> None:
    """Start a simple terminal loop for manually testing prompts.

    Args:
        runner: Configured in-memory ADK runner.
    """
    # This keeps the tutorial demo hands-on: viewers can try prompts one by one
    # without editing code or replaying a fixed sequence each time.
    print("\nEnter a prompt and press Enter. Type 'exit' or 'quit' to stop.")

    while True:
        prompt = input("\nPrompt> ").strip()
        if not prompt:
            continue
        if prompt.lower() in {"exit", "quit"}:
            print("Exiting interactive demo.")
            break
        await run_prompt(runner, prompt)


async def main() -> None:
    """Create the session and runner, then execute either one prompt or an interactive shell."""
    # Load local environment variables when a tutorial-specific .env file exists.
    load_dotenv()

    args = parse_args()

    # Plugins are attached at the runner level, so both the built-in logger and
    # our custom refund guardrail apply across the full execution flow.
    plugins = [
        LoggingPlugin(),
        RefundGuardrailPlugin(
            max_refund_without_manager=args.refund_threshold,
            manager_mode=args.manager_mode,
        ),
    ]
    runner = InMemoryRunner(
        agent=root_agent,
        app_name=APP_NAME,
        plugins=plugins,
    )

    # InMemoryRunner owns its in-memory session service in this ADK version, so
    # we create the demo session directly through the runner after construction.
    await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    print("=== ADK Plugins Demo ===")
    print(f"Manager mode: {args.manager_mode}")
    print(f"Refund threshold without manager approval: ${args.refund_threshold:.2f}")

    if args.prompt:
        await run_prompt(runner, args.prompt)
        return

    await run_interactive_shell(runner)


if __name__ == "__main__":
    asyncio.run(main())
