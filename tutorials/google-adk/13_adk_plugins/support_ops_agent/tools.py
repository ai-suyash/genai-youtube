from typing import Any

from google.adk.tools.tool_context import ToolContext

ORDER_DATA = {
    "ORD-1001": {
        "status": "Delivered",
        "shipping_carrier": "MapleExpress",
        "eta": "Delivered on 2026-03-10",
        "eligible_for_refund": True,
    },
    "ORD-2002": {
        "status": "In transit",
        "shipping_carrier": "NorthStar Logistics",
        "eta": "Expected by 2026-03-18",
        "eligible_for_refund": False,
    },
}


def lookup_order_status(order_id: str, tool_context: ToolContext) -> dict[str, Any]:
    """Look up mock shipping information for a given order.

    Args:
        order_id: External order identifier supplied by the user or agent.
        tool_context: ADK tool context used for reading and updating session state.

    Returns:
        A status payload containing shipping details when the order exists, or an
        error payload when the order cannot be found.
    """
    # The tutorial keeps tool data in memory so the focus stays on plugin behavior
    # rather than external integrations or database setup.
    order = ORDER_DATA.get(order_id.upper())
    if not order:
        return {
            "status": "error",
            "message": f"Order {order_id} was not found.",
        }

    lookup_count = tool_context.state.get("user:lookup_count", 0) + 1
    tool_context.state["user:lookup_count"] = lookup_count

    return {
        "status": "success",
        "order_id": order_id.upper(),
        "order_status": order["status"],
        "shipping_carrier": order["shipping_carrier"],
        "eta": order["eta"],
        "lookup_count": lookup_count,
    }


def refund_order(order_id: str, amount: float, reason: str, tool_context: ToolContext) -> dict[str, Any]:
    """Process a mock refund request for an eligible order.

    Args:
        order_id: External order identifier to refund.
        amount: Refund amount approved by the agent workflow.
        reason: Human-readable explanation for the refund.
        tool_context: ADK tool context used for shared state updates.

    Returns:
        A success payload with refund metadata when the request is valid, or an
        error payload when the order is missing, invalid, or not yet refundable.
    """
    # By the time this function runs, the guardrail plugin has already had a chance
    # to block oversized refunds. The tool only handles normal business validation.
    order = ORDER_DATA.get(order_id.upper())
    if not order:
        return {
            "status": "error",
            "message": f"Order {order_id} was not found.",
        }

    if amount <= 0:
        return {
            "status": "error",
            "message": "Refund amount must be greater than zero.",
        }

    if not order["eligible_for_refund"]:
        return {
            "status": "error",
            "message": f"Order {order_id.upper()} is not yet eligible for refund review.",
        }

    refund_count = tool_context.state.get("user:refund_count", 0) + 1
    tool_context.state["user:refund_count"] = refund_count

    return {
        "status": "success",
        "order_id": order_id.upper(),
        "amount": round(amount, 2),
        "reason": reason,
        "refund_id": f"RFD-{refund_count:04d}",
        "message": f"Refund for ${amount:.2f} has been approved for order {order_id.upper()}.",
    }
