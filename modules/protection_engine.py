"""
LoanGuard AI — Protection Engine
Adds five borrower-protection features on top of existing RiskAnalysisResult:

  1. Final Verdict Engine      → SAFE TO SIGN / REVIEW REQUIRED / DO NOT SIGN YET
  2. Safer Clause Generator    → borrower-friendly rewrites of risky clauses
  3. Negotiation Assistant     → questions borrower should ask the lender
  4. Safe Loan Comparison      → current agreement vs fair lending benchmark
  5. Family Alert Simulation   → plain-language SMS-style warning message
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ─────────────────────────────────────────────────────────────────────────────
# Data structures
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Verdict:
    label: str          # SAFE TO SIGN | REVIEW REQUIRED | DO NOT SIGN YET
    color: str          # low | medium | high  (maps to score-banner CSS classes)
    icon:  str
    reasons: list[str]
    actions: list[str]  # concrete steps before signing


@dataclass
class SaferClause:
    category:  str
    original:  str      # risky snippet from the agreement
    suggested: str      # borrower-friendly rewrite


@dataclass
class NegotiationQuestion:
    category: str
    question: str
    why:      str       # why asking this protects the borrower


@dataclass
class ComparisonRow:
    criterion:  str
    current:    str     # what this agreement says
    benchmark:  str     # what a fair agreement should say
    status:     str     # ok | warn | bad


@dataclass
class ProtectionBundle:
    verdict:      Verdict
    safer_clauses: list[SaferClause]
    questions:    list[NegotiationQuestion]
    comparison:   list[ComparisonRow]
    family_alert: str


# ─────────────────────────────────────────────────────────────────────────────
# Knowledge base — safer clause rewrites
# ─────────────────────────────────────────────────────────────────────────────
_SAFER_CLAUSES: dict[str, str] = {
    "Hidden Fees": (
        "All fees and charges applicable to this loan are fully disclosed in Schedule A attached hereto. "
        "No additional charges shall be levied without prior written consent of the borrower."
    ),
    "Processing Charges": (
        "A processing fee of ₹_______ (fixed) shall be deducted from the disbursed amount. "
        "The net disbursal amount shall be ₹_______ and shall be communicated to the borrower "
        "in writing before loan acceptance."
    ),
    "High Penalty": (
        "A late payment fee not exceeding ₹500 or 1% of the overdue instalment, whichever is lower, "
        "shall apply after a grace period of 7 calendar days from the due date."
    ),
    "Contact Access Permission": (
        "The lender shall contact the borrower only through the registered mobile number and email "
        "provided in this agreement. No access to the borrower's device contacts or third-party "
        "individuals shall be required."
    ),
    "Data Sharing": (
        "Borrower's personal data shall be used solely for loan processing and servicing purposes. "
        "Data shall not be shared with any third party except as required by law or with "
        "explicit written consent of the borrower."
    ),
    "Aggressive Recovery Terms": (
        "Recovery communication shall be limited to calls, SMS, and email between 8 AM and 7 PM IST. "
        "Recovery agents, if engaged, shall carry valid identity proof and provide 48 hours' prior notice "
        "before any visit, in compliance with RBI Fair Practice Code."
    ),
    "Unclear Repayment Terms": (
        "The repayment schedule, including EMI amount, tenure, and total interest payable, "
        "is fixed as stated in Schedule B and shall not be altered without written consent of the borrower. "
        "The annual percentage rate (APR) is _______% per annum."
    ),
    "Variable Interest Rate": (
        "The interest rate shall be fixed at _______% per annum for the entire loan tenure "
        "and shall not change without the borrower's written agreement."
    ),
    "Unilateral Changes": (
        "Any change to the terms of this agreement requires mutual written consent. "
        "The lender shall provide at least 30 days' written notice before any proposed change "
        "and the borrower retains the right to reject such changes and foreclose at par."
    ),
    "Foreclosure Penalty": (
        "The borrower may foreclose this loan at any time without any prepayment penalty "
        "after completion of the lock-in period of _______ months, as per RBI guidelines."
    ),
}

# ─────────────────────────────────────────────────────────────────────────────
# Knowledge base — negotiation questions
# ─────────────────────────────────────────────────────────────────────────────
_NEGOTIATION_Qs: dict[str, tuple[str, str]] = {
    "Hidden Fees": (
        "Can you provide a complete written list of all fees — processing, insurance, stamp duty, "
        "and any other charges — before I accept this loan?",
        "Lenders are required to disclose all costs upfront. If they refuse, that is a red flag."
    ),
    "Processing Charges": (
        "What is the exact net amount that will be credited to my account after all deductions?",
        "The disbursal amount is the real loan. You repay the full principal, so hidden deductions "
        "effectively raise your interest rate."
    ),
    "High Penalty": (
        "Can the late payment penalty be reduced or capped at a fixed amount rather than a percentage? "
        "What is the grace period before penalty applies?",
        "A single missed payment with a high % penalty can spiral your debt rapidly."
    ),
    "Contact Access Permission": (
        "Why does this agreement require access to my phone contacts? "
        "Can this clause be removed or limited to a single guarantor's contact?",
        "Contact access is used for public shaming during recovery — a known predatory tactic."
    ),
    "Data Sharing": (
        "With whom exactly will my personal data be shared, and for what purposes? "
        "Can I get a written data-sharing policy?",
        "Uncontrolled data sharing can lead to spam, fraud, and privacy violations."
    ),
    "Aggressive Recovery Terms": (
        "Under what circumstances would recovery agents visit my home or workplace? "
        "What notice will be given, and what identification will agents carry?",
        "RBI Fair Practice Code mandates proper notice and professional conduct during recovery."
    ),
    "Unclear Repayment Terms": (
        "Can you give me a fixed EMI schedule in writing with the exact amount, date, and tenure? "
        "Under what conditions can the interest rate or EMI change?",
        "Variable or undisclosed terms make budgeting impossible and can lead to shock increases."
    ),
    "Variable Interest Rate": (
        "Is the interest rate fixed or floating? If floating, what index is it linked to, "
        "and what is the maximum it can rise to?",
        "Floating rates with no cap can dramatically increase your repayment burden."
    ),
    "Unilateral Changes": (
        "Can you remove or modify the clause allowing you to change loan terms without my consent? "
        "I would like 30 days' notice and the right to foreclose at no penalty if terms change.",
        "One-sided change clauses give the lender unlimited power to increase costs post-disbursement."
    ),
    "Foreclosure Penalty": (
        "What is the prepayment or foreclosure penalty? Is it waived after a certain period?",
        "RBI guidelines restrict foreclosure penalties on floating rate loans. "
        "A high penalty traps you even if you find a better option later."
    ),
}

# ─────────────────────────────────────────────────────────────────────────────
# Comparison benchmark
# ─────────────────────────────────────────────────────────────────────────────
def _build_comparison(findings_by_id: set[str]) -> list[ComparisonRow]:
    rows = [
        ComparisonRow(
            criterion="Fee Transparency",
            current="All fees not disclosed upfront" if "Hidden Fees" in findings_by_id or "Processing Charges" in findings_by_id
                    else "Fees appear disclosed",
            benchmark="All charges listed in writing before disbursal",
            status="bad" if ("Hidden Fees" in findings_by_id or "Processing Charges" in findings_by_id) else "ok",
        ),
        ComparisonRow(
            criterion="Penalty Rate",
            current="High % penalty per month" if "High Penalty" in findings_by_id
                    else "Penalty terms not detected",
            benchmark="≤ ₹500 or 1% of EMI, with 7-day grace period",
            status="bad" if "High Penalty" in findings_by_id else "ok",
        ),
        ComparisonRow(
            criterion="Privacy Protection",
            current="Contact access and/or data sharing clause found" if (
                "Contact Access Permission" in findings_by_id or "Data Sharing" in findings_by_id)
                    else "No explicit contact/data clause detected",
            benchmark="No device access required; data used only for loan servicing",
            status="bad" if ("Contact Access Permission" in findings_by_id or "Data Sharing" in findings_by_id) else "ok",
        ),
        ComparisonRow(
            criterion="Recovery Practices",
            current="Aggressive recovery / no-notice visits allowed" if "Aggressive Recovery Terms" in findings_by_id
                    else "Recovery terms not flagged",
            benchmark="RBI Fair Practice Code: prior notice, daytime only, no harassment",
            status="bad" if "Aggressive Recovery Terms" in findings_by_id else "ok",
        ),
        ComparisonRow(
            criterion="Repayment Clarity",
            current="Terms can change at lender's discretion" if "Unclear Repayment Terms" in findings_by_id
                    else "Repayment terms appear stable",
            benchmark="Fixed EMI schedule with APR stated clearly in the agreement",
            status="warn" if "Unclear Repayment Terms" in findings_by_id else "ok",
        ),
        ComparisonRow(
            criterion="Interest Rate",
            current="Rate may vary without notice" if "Variable Interest Rate" in findings_by_id
                    else "Fixed rate or rate not flagged",
            benchmark="Fixed rate or floating with a stated cap and index reference",
            status="warn" if "Variable Interest Rate" in findings_by_id else "ok",
        ),
        ComparisonRow(
            criterion="Foreclosure Rights",
            current="Foreclosure penalty or restriction found" if "Foreclosure Penalty" in findings_by_id
                    else "No foreclosure restriction detected",
            benchmark="No penalty after lock-in period (as per RBI floating rate loans)",
            status="warn" if "Foreclosure Penalty" in findings_by_id else "ok",
        ),
    ]
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────
def generate_protection_bundle(analysis) -> ProtectionBundle:
    """
    Given a RiskAnalysisResult, produce the full ProtectionBundle.
    Compatible with the existing RiskAnalysisResult/RiskFinding dataclasses.
    """
    findings = analysis.findings
    categories = {f.category for f in findings}
    high_count = sum(1 for f in findings if f.severity == "high")
    med_count  = sum(1 for f in findings if f.severity == "medium")

    # ── 1. Verdict ──
    verdict = _build_verdict(analysis.score, analysis.category, high_count, med_count, categories)

    # ── 2. Safer clauses ──
    safer: list[SaferClause] = []
    for finding in findings:
        suggested = _SAFER_CLAUSES.get(finding.category)
        if suggested:
            safer.append(SaferClause(
                category=finding.category,
                original=finding.snippet,
                suggested=suggested,
            ))

    # ── 3. Negotiation questions ──
    questions: list[NegotiationQuestion] = []
    for finding in findings:
        q_data = _NEGOTIATION_Qs.get(finding.category)
        if q_data:
            questions.append(NegotiationQuestion(
                category=finding.category,
                question=q_data[0],
                why=q_data[1],
            ))

    # ── 4. Comparison ──
    comparison = _build_comparison(categories)

    # ── 5. Family alert ──
    family_alert = _build_family_alert(analysis, high_count, med_count)

    return ProtectionBundle(
        verdict=verdict,
        safer_clauses=safer,
        questions=questions,
        comparison=comparison,
        family_alert=family_alert,
    )


def _build_verdict(
    score: float,
    category: str,
    high_count: int,
    med_count: int,
    categories: set[str],
) -> Verdict:
    dangerous_flags = {"Contact Access Permission", "Aggressive Recovery Terms", "Hidden Fees"}
    has_dangerous = bool(categories & dangerous_flags)

    if category == "HIGH" or (high_count >= 2) or has_dangerous:
        return Verdict(
            label="DO NOT SIGN YET",
            color="high",
            icon="🚫",
            reasons=[
                f"{high_count} HIGH severity clause(s) detected — these pose serious financial or privacy risks.",
                "Contact access and/or aggressive recovery terms are red flags for predatory lending.",
                f"Safety score of {score}/10 is below the safe threshold.",
            ] if has_dangerous else [
                f"{high_count} HIGH severity clause(s) found in this agreement.",
                f"Safety score of {score}/10 indicates significant risk.",
                "Multiple clauses need removal or renegotiation before this is safe to sign.",
            ],
            actions=[
                "Request written explanations for every flagged clause from the lender.",
                "Demand removal of contact access, data sharing, and aggressive recovery terms.",
                "Compare total repayment cost with at least 2 other lenders.",
                "Consult a financial advisor or legal aid clinic before signing.",
                "Do not accept verbal assurances — all changes must be in the signed document.",
            ],
        )

    elif category == "MEDIUM" or med_count >= 2:
        return Verdict(
            label="REVIEW REQUIRED",
            color="medium",
            icon="⚠️",
            reasons=[
                f"{med_count} MEDIUM severity clause(s) need clarification.",
                f"Safety score of {score}/10 — some concerns, not immediately dangerous.",
                "Certain terms lack clarity and could be unfavourable at repayment time.",
            ],
            actions=[
                "Get a fixed, signed EMI repayment schedule before accepting the loan.",
                "Ask for the exact net disbursal amount after all fee deductions.",
                "Ensure the penalty clause has a fixed cap, not an open-ended percentage.",
                "Request a copy of the lender's data-privacy policy.",
                "Keep a copy of the signed agreement and sanction letter.",
            ],
        )

    else:
        return Verdict(
            label="SAFE TO SIGN",
            color="low",
            icon="✅",
            reasons=[
                f"Safety score of {score}/10 — no major red flags detected.",
                "No predatory or aggressive clauses found in this agreement.",
                f"Only {len(categories)} low-severity item(s) to note.",
            ],
            actions=[
                "Confirm all verbally promised amounts appear in the signed document.",
                "Keep a copy of the signed agreement and all payment receipts.",
                "Note the foreclosure terms in case you want to repay early.",
                "Set up autopay to avoid accidental late fees.",
            ],
        )


def _build_family_alert(analysis, high_count: int, med_count: int) -> str:
    score = analysis.score
    category = analysis.category
    risk_items = [f.category for f in analysis.findings[:3]]
    items_str = ", ".join(risk_items) if risk_items else "general terms"
    extra = f" and {len(analysis.findings) - 3} more" if len(analysis.findings) > 3 else ""

    if category == "HIGH":
        urgency = "⛔ URGENT ALERT"
        body = (
            f"This loan agreement has {high_count} HIGH RISK clause(s). "
            f"Issues found: {items_str}{extra}. "
            f"Safety Score: {score}/10. "
            "DO NOT sign until a trusted person or advisor reviews it. "
            "This lender may be using predatory practices."
        )
    elif category == "MEDIUM":
        urgency = "⚠️ CAUTION ALERT"
        body = (
            f"This loan agreement has some concerns. "
            f"Issues found: {items_str}{extra}. "
            f"Safety Score: {score}/10. "
            "Please review the flagged clauses carefully or ask someone to help "
            "before signing."
        )
    else:
        urgency = "✅ LOW RISK"
        body = (
            f"This loan agreement looks relatively safe. Safety Score: {score}/10. "
            "No major risks detected. Verify all amounts match what was promised "
            "and keep a signed copy."
        )

    return (
        f"─────────────────────────────────\n"
        f"🛡️ LoanGuard AI — Family Alert\n"
        f"─────────────────────────────────\n"
        f"{urgency}\n\n"
        f"{body}\n\n"
        f"Scanned by LoanGuard AI. Share this with a trusted family member or friend.\n"
        f"─────────────────────────────────"
    )