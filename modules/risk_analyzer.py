"""
Loan Risk Analyzer — NLP-style keyword and pattern analysis for loan agreements.
Detects risky clauses and produces a safety score and plain-language summary.
"""

import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class RiskFinding:
    """One detected risk in the agreement."""
    category: str
    severity: str      # low | medium | high
    snippet:  str
    explanation: str


@dataclass
class RiskAnalysisResult:
    """Full output of the risk analyzer."""
    score:    float
    category: str                     # LOW | MEDIUM | HIGH
    findings: List[RiskFinding] = field(default_factory=list)
    summary:  str = ""
    explanations: List[str] = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# Risk rule definitions
# ─────────────────────────────────────────────────────────────────────────────
RISK_RULES = [
    {
        "id": "hidden_fees",
        "label": "Hidden Fees",
        "patterns": [
            r"hidden\s+fee",
            r"undisclosed\s+(?:fee|charge|cost)",
            r"additional\s+fee[s]?\s+(?:may|shall|will)\s+apply",
            r"service\s+charge[s]?\s+(?:not\s+included|extra)",
            r"miscellaneous\s+charge[s]?",
            r"other\s+charges?\s+as\s+applicable",
        ],
        "severity": "high",
        "explanation": (
            "The agreement mentions fees that may not be clearly disclosed upfront. "
            "These can silently reduce the money you actually receive."
        ),
    },
    {
        "id": "processing_charges",
        "label": "Processing Charges",
        "patterns": [
            r"processing\s+(?:fee|charge|cost)",
            r"origination\s+fee",
            r"documentation\s+(?:fee|charge)",
            r"admin(?:istrative)?\s+(?:fee|charge)",
            r"handling\s+charge",
            r"processing\s+amount\s+(?:shall\s+be\s+)?deducted",
            r"deducted\s+from\s+the\s+disbursed",
        ],
        "severity": "medium",
        "explanation": (
            "Processing or admin charges are deducted before you receive the money — "
            "so you repay a larger loan than you actually got."
        ),
    },
    {
        "id": "high_penalty",
        "label": "High Penalty",
        "patterns": [
            r"(?:penalty|penalties)\s+(?:of|up\s+to|at\s+least)\s+\d+\s*%",
            r"late\s+(?:payment\s+)?(?:fee|penalty|charge).{0,50}\d+\s*%",
            r"default\s+(?:fee|penalty|charge).{0,50}\d+\s*%",
            r"penal\s+interest",
            r"compound(?:ed)?\s+(?:interest|penalty)",
            r"penalty\s+.*per\s+(?:month|day|week)",
        ],
        "severity": "high",
        "explanation": (
            "Strict or percentage-based penalties can make a single missed payment "
            "extremely costly and trigger a debt spiral."
        ),
    },
    {
        "id": "contact_access",
        "label": "Contact Access Permission",
        "patterns": [
            r"access\s+(?:to\s+)?(?:your\s+)?(?:phone\s+)?contact[s]?",
            r"read\s+(?:your\s+)?contact[s]?",
            r"phone\s+book\s+access",
            r"call\s+(?:your\s+)?(?:references|contacts|family|friends)",
            r"contact\s+(?:list|book)\s+(?:access|permission)",
        ],
        "severity": "high",
        "explanation": (
            "Granting contact access lets the lender contact your friends, family, and colleagues "
            "for recovery — a serious privacy and harassment risk."
        ),
    },
    {
        "id": "data_sharing",
        "label": "Data Sharing",
        "patterns": [
            r"share\s+(?:your\s+)?(?:personal\s+)?data",
            r"third\s+party\s+(?:access|sharing|disclosure|partner)",
            r"sell\s+(?:your\s+)?(?:data|information)",
            r"disclose\s+(?:to\s+)?(?:third\s+parties|partners|affiliates)",
            r"data\s+(?:may\s+be\s+)?shared",
            r"personal\s+information\s+(?:may\s+be\s+)?(?:transferred|disclosed|shared)",
        ],
        "severity": "medium",
        "explanation": (
            "Your personal data, including contact details and financial history, may be shared "
            "with third parties without clear limits on how it is used."
        ),
    },
    {
        "id": "aggressive_recovery",
        "label": "Aggressive Recovery Terms",
        "patterns": [
            r"without\s+(?:prior\s+)?notice.{0,40}(?:recover|demand|legal|visit)",
            r"engage\s+(?:collection\s+)?agent[s]?",
            r"visit\s+(?:your\s+)?(?:home|workplace|office|premises)",
            r"recovery\s+(?:agent|team)\s+(?:may|shall|will)",
            r"immediate\s+(?:legal\s+)?(?:action|recovery|demand)",
            r"doorstep\s+(?:collection|recovery|visit)",
        ],
        "severity": "high",
        "explanation": (
            "Recovery terms allow agents to contact or visit you without notice — "
            "this can constitute harassment and may violate RBI Fair Practice Code."
        ),
    },
    {
        "id": "unclear_repayment",
        "label": "Unclear Repayment Terms",
        "patterns": [
            r"repayment\s+(?:terms\s+)?(?:may\s+)?(?:vary|change|be\s+modified)",
            r"subject\s+to\s+(?:change|revision|modification)",
            r"at\s+(?:the\s+)?lender['\u2019]?s\s+(?:sole\s+)?discretion",
            r"as\s+determined\s+by\s+(?:the\s+)?lender",
            r"terms\s+(?:may\s+be\s+)?revised\s+(?:without|at\s+any\s+time)",
            r"emi\s+(?:amount\s+)?(?:may|can|shall)\s+(?:vary|change|differ)",
            r"repayment\s+schedule\s+(?:is\s+)?(?:indicative|approximate|subject)",
        ],
        "severity": "medium",
        "explanation": (
            "The EMI or repayment schedule is not fixed — the lender can change amounts "
            "at any time, making it impossible for you to plan your finances reliably."
        ),
    },
    {
        "id": "variable_interest",
        "label": "Variable Interest Rate",
        "patterns": [
            r"interest\s+rate\s+(?:may\s+)?(?:vary|change|float|fluctuate)",
            r"floating\s+(?:interest\s+)?rate",
            r"variable\s+(?:interest\s+)?rate",
            r"rate\s+of\s+interest\s+(?:is\s+)?subject\s+to\s+(?:change|revision|market)",
            r"interest\s+(?:rate\s+)?(?:linked|pegged|tied)\s+to\s+(?:market|repo|base|mclr|prime)",
            r"revised\s+interest\s+rate\s+(?:shall|will|may)\s+(?:apply|be\s+charged)",
        ],
        "severity": "medium",
        "explanation": (
            "The interest rate is not fixed and can rise without notice. "
            "A floating rate without a cap can significantly increase your monthly payments "
            "and total repayment burden."
        ),
    },
    {
        "id": "unilateral_changes",
        "label": "Unilateral Changes",
        "patterns": [
            r"lender\s+(?:reserves?|has)\s+(?:the\s+)?right\s+to\s+(?:amend|modify|change|alter)\s+(?:these\s+)?terms",
            r"may\s+(?:amend|modify|change|alter|revise)\s+(?:this\s+)?agreement\s+(?:at\s+any\s+time|without\s+consent)",
            r"without\s+(?:the\s+)?(?:borrower['\u2019]?s\s+)?consent\s+(?:or\s+)?(?:approval|agreement)",
            r"sole\s+(?:and\s+absolute\s+)?discretion\s+(?:of\s+the\s+lender|to\s+modify)",
            r"terms?\s+and\s+conditions?\s+(?:may\s+be\s+)?changed\s+(?:by\s+the\s+lender|unilaterally|at\s+will)",
            r"lender\s+(?:may|can|shall)\s+(?:at\s+any\s+time\s+)?revise\s+(?:the\s+)?(?:loan\s+)?terms",
        ],
        "severity": "high",
        "explanation": (
            "The lender can change the loan terms — including rates, fees, or conditions — "
            "without your agreement. This means you may end up with very different obligations "
            "than what was signed at the start."
        ),
    },
    {
        "id": "unusual_charges",
        "label": "Unusual Charges",
        "patterns": [
            r"miscellaneous\s+charge[s]?",
            r"convenience\s+fee",
            r"service\s+tax",
            r"gst\s+charged",
            r"insurance\s+premium\s+applicable",
        ],
        "severity": "medium",
        "explanation": (
            "The agreement includes various miscellaneous or convenience charges which may not be standard. "
            "These can inflate the effective cost of borrowing without clear disclosure."
        ),
    },
    {
        "id": "foreclosure_penalty",
        "label": "Foreclosure Penalty",
        "patterns": [
            r"prepayment\s+(?:penalty|charge|fee)",
            r"foreclosure\s+(?:penalty|charge|fee)",
            r"early\s+(?:repayment|closure)\s+(?:penalty|charge|fee|not\s+permitted)",
            r"part\s+(?:prepayment|payment)\s+(?:charge|fee|penalty|not\s+allowed)",
            r"lock.?in\s+period.{0,40}(?:penalty|charge|foreclosure)",
            r"may\s+not\s+(?:prepay|foreclose|close)\s+(?:the\s+loan\s+)?before",
        ],
        "severity": "low",
        "explanation": (
            "A foreclosure or prepayment penalty means you will be charged for paying off the loan "
            "early — this restricts your financial freedom and can cost thousands if you find "
            "a better deal or come into money."
        ),
    },
]

# Penalty weights
PENALTY_MAP = {"high": 1.5, "medium": 1.0, "low": 0.5}


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────
def _normalize(text: str) -> str:
    """Lowercase and collapse whitespace for matching."""
    return re.sub(r"\s+", " ", text.lower()).strip()


def _find_snippet(text: str, match: re.Match, window: int = 160) -> str:
    """Return a context window around the matched phrase (original casing).

    Strategy: extend left/right to the nearest sentence boundary when possible,
    then cap at `window` chars each side for readability.
    """
    m_start, m_end = match.start(), match.end()

    # Extend left to start of sentence
    left_text = text[max(0, m_start - window): m_start]
    last_stop = max(left_text.rfind("."), left_text.rfind("।"), left_text.rfind("\n"))
    start = (m_start - window + last_stop + 1) if last_stop != -1 else max(0, m_start - window)
    start = max(0, start)

    # Extend right to end of sentence
    right_text = text[m_end: min(len(text), m_end + window)]
    first_stop = min(
        (right_text.find(".") if right_text.find(".") != -1 else len(right_text)),
        (right_text.find("।") if right_text.find("।") != -1 else len(right_text)),
    )
    end = min(len(text), m_end + first_stop + 1)

    snippet = text[start:end].strip()

    # Hard cap at 220 chars to keep cards readable
    if len(snippet) > 220:
        snippet = snippet[:220].rsplit(" ", 1)[0] + "…"

    prefix = "…" if start > 0 else ""
    return f"{prefix}{snippet}"


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────
def analyze_loan_text(text: str) -> RiskAnalysisResult:
    """
    Analyze loan agreement text and return score, category, and findings.

    Score starts at 10 and decreases by severity weight per detected risk.
    """
    if not text or not text.strip() or text.strip().startswith("[PDF Error]"):
        return RiskAnalysisResult(
            score=0.0,
            category="HIGH",
            findings=[],
            summary=(
                "No valid agreement text was provided. "
                "Please paste text or upload a readable PDF."
            ),
        )

    normalized = _normalize(text)
    findings: list[RiskFinding] = []
    seen: set[str] = set()

    for rule in RISK_RULES:
        for pattern in rule["patterns"]:
            m = re.search(pattern, normalized, re.IGNORECASE)
            if m and rule["id"] not in seen:
                # Re-search on original text to preserve casing for snippet
                orig_m = re.search(pattern, text, re.IGNORECASE)
                snippet = _find_snippet(text, orig_m) if orig_m else rule["label"]
                findings.append(RiskFinding(
                    category=rule["label"],
                    severity=rule["severity"],
                    snippet=snippet,
                    explanation=rule["explanation"],
                ))
                seen.add(rule["id"])
                break

    # ── Additional heuristic checks ──
    # Detect numeric interest rates mentioned and flag extremely high rates
    percents = [float(p) for p in re.findall(r"(\d{1,2}(?:\.\d+)?)\s*%", text) if p]
    if percents:
        try:
            max_rate = max(percents)
            if max_rate >= 24.0:
                findings.append(RiskFinding(
                    category="Extremely High Interest Rate",
                    severity="high",
                    snippet=f"Interest rate mentions up to {max_rate}% in the agreement.",
                    explanation=(
                        f"An interest rate of {max_rate}% or above is very high and increases total repayment substantially."
                    ),
                ))
        except Exception:
            pass

    # Detect short-tenure/short repayment traps (e.g., very short loan tenures)
    months = [int(m) for m in re.findall(r"(\d{1,3})\s+months", normalized) if m]
    if months:
        try:
            min_m = min(months)
            if min_m <= 6:
                findings.append(RiskFinding(
                    category="Short Repayment Period",
                    severity="medium",
                    snippet=f"Loan tenure mentioned as {min_m} months which is short and may create high EMI burden.",
                    explanation=(
                        "Very short repayment terms can create unaffordable EMIs and repayment pressure on borrowers."
                    ),
                ))
        except Exception:
            pass

    # If miscellaneous/unusual charges were matched, add a focused explanation
    if any(f.category == "Unusual Charges" for f in findings):
        # Add an explanatory finding if no similar finding exists
        pass

    total_penalty = sum(PENALTY_MAP.get(f.severity, 1.0) for f in findings)
    score = max(0.0, min(10.0, round(10.0 - total_penalty, 1)))

    if score >= 7.0:
        category = "LOW"
    elif score >= 4.0:
        category = "MEDIUM"
    else:
        category = "HIGH"

    summary = _build_summary(score, category, findings)
    return RiskAnalysisResult(score=score, category=category, findings=findings, summary=summary)


def _build_summary(score: float, category: str, findings: list[RiskFinding]) -> str:
    """Plain-language summary shown below the score."""
    if not findings:
        return (
            f"Your Loan Safety Score is {score}/10 ({category} risk). "
            "No major risky clauses were detected. "
            "Still review the full agreement and confirm all amounts in writing."
        )

    labels = ", ".join(f.category for f in findings[:3])
    extra  = f" and {len(findings) - 3} more" if len(findings) > 3 else ""

    tone_map = {
        "HIGH":   "This agreement has several serious issues — do not sign without legal review.",
        "MEDIUM": "Some clauses need careful negotiation before you sign.",
        "LOW":    "A few minor issues found — generally manageable with review.",
    }
    tone = tone_map.get(category, "")

    return (
        f"Your Loan Safety Score is {score}/10 ({category} risk). {tone} "
        f"Flagged items: {labels}{extra}. "
        "Review each risk card below and compare with what you were told verbally."
    )