from typing import Any

from google.adk.plugins.base_plugin import BasePlugin
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext


class RefundGuardrailPlugin(BasePlugin):
    """Blocks large refunds unless the runtime is explicitly in manager mode."""

    def __init__(self, max_refund_without_manager: float, manager_mode: bool = False) -> None:
        """Initialize the refund guardrail settings.

        Args:
            max_refund_without_manager: Maximum refund amount allowed without elevated approval.
            manager_mode: Whether the runtime should bypass the non-manager refund limit.
        """
        super().__init__(name="refund_guardrail_plugin")
        self.max_refund_without_manager = max_refund_without_manager
        self.manager_mode = manager_mode

    async def before_tool_callback(
        self,
        *,
        tool: BaseTool,
        tool_args: dict[str, Any],
        tool_context: ToolContext,
    ):
        """Inspect refund tool calls and block large refunds when policy requires it.

        Args:
            tool: Tool selected by the agent.
            tool_args: Parsed arguments that will be passed to the tool.
            tool_context: Tool execution context, including shared session state.

        Returns:
            `None` when execution should continue normally. A dict tool response when
            the refund is blocked so ADK can skip the underlying tool call.
        """
        # This hook runs before every tool call. We only intervene for the
        # sensitive refund tool and let all other tools pass through untouched.
        if tool.name != "refund_order":
            return None

        amount = float(tool_args.get("amount", 0.0))
        if amount <= self.max_refund_without_manager or self.manager_mode:
            return None

        # Returning a dict here short-circuits tool execution: ADK treats this as
        # the tool result, which makes the policy decision visible to the agent.
        order_id = tool_args.get("order_id", "unknown")
        print(
            "[plugin:guardrail] blocked refund_order "
            f"for {order_id} because ${amount:.2f} exceeds the "
            f"${self.max_refund_without_manager:.2f} limit."
        )
        tool_context.state["user:last_blocked_refund_amount"] = amount
        return {
            "status": "blocked",
            "order_id": order_id,
            "amount": amount,
            "message": (
                f"Refund blocked by runtime policy. Amount ${amount:.2f} exceeds the "
                f"${self.max_refund_without_manager:.2f} non-manager limit."
            ),
        }
