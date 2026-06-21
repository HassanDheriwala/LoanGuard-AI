"""
True Cost Calculator — compares promised vs received vs total repayment.
"""

from dataclasses import dataclass


@dataclass
class CostResult:
    """Output of the true cost calculation."""

    promised_amount: float
    received_amount: float
    total_repayment: float
    hidden_charges: float
    extra_repayment: float
    effective_cost_pct: float
    risk_message: str


def calculate_true_cost(
    promised_amount: float,
    received_amount: float,
    total_repayment: float,
) -> CostResult:
    """
    Calculate hidden charges and extra repayment from loan figures.

    Args:
        promised_amount: Amount the lender said you would get.
        received_amount: Amount actually deposited to you.
        total_repayment: Total you must pay back (principal + interest + fees).

    Returns:
        CostResult with breakdown and a user-friendly risk message.
    """
    promised = max(0.0, float(promised_amount))
    received = max(0.0, float(received_amount))
    repayment = max(0.0, float(total_repayment))

    # Money never received vs what was promised
    hidden_charges = max(0.0, promised - received)

    # Total cost above what you actually received
    extra_repayment = max(0.0, repayment - received)

    # Effective extra cost as % of received amount
    if received > 0:
        effective_cost_pct = round((extra_repayment / received) * 100, 2)
    else:
        effective_cost_pct = 0.0

    risk_message = _build_risk_message(
        hidden_charges, extra_repayment, effective_cost_pct, promised, received, repayment
    )

    return CostResult(
        promised_amount=promised,
        received_amount=received,
        total_repayment=repayment,
        hidden_charges=hidden_charges,
        extra_repayment=extra_repayment,
        effective_cost_pct=effective_cost_pct,
        risk_message=risk_message,
    )


def _build_risk_message(
    hidden: float,
    extra: float,
    pct: float,
    promised: float,
    received: float,
    repayment: float,
) -> str:
    """Generate a simple risk message based on the numbers."""
    if promised == 0 and received == 0 and repayment == 0:
        return "Enter your loan amounts to see the true cost breakdown."

    if received > promised:
        return (
            "You received more than the promised amount — double-check these figures "
            "or confirm whether this includes rollover from a previous loan."
        )

    if hidden > 0 and pct >= 50:
        return (
            f"Warning: You did not receive ₹{hidden:,.0f} of the promised amount, "
            f"and you must repay ₹{extra:,.0f} above what you got ({pct}% extra). "
            "This is a very expensive loan — consider alternatives."
        )

    if hidden > 0:
        return (
            f"You received ₹{hidden:,.0f} less than promised — likely processing or hidden fees. "
            f"Total extra repayment over received amount: ₹{extra:,.0f} ({pct}%)."
        )

    if pct >= 30:
        return (
            f"No upfront deduction detected, but total repayment is {pct}% above what you received. "
            "Review the interest rate and tenure carefully."
        )

    if repayment <= received:
        return (
            "Repayment amount is less than or equal to received amount — verify these numbers "
            "include all interest and fees."
        )

    return (
        f"True cost looks moderate: you repay ₹{extra:,.0f} more than you received ({pct}%). "
        "Compare this with the agreement's stated interest rate."
    )
