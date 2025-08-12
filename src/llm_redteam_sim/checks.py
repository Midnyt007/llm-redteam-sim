from __future__ import annotations
import re
from typing import Dict, Any

# Compact, readable regexes. These are intentionally simple and easy to extend.
JAILBREAK_SIGNS = re.compile(
    r"(?i)ignore\s+previous|override\s+instructions|\bpretend\b|developer\s+mode|do\s+not\s+refuse"
)
SYSTEM_LEAK_SIGNS = re.compile(r"(?i)system\s+prompt|hidden\s+instruction|internal\s+policy")
VIOLENCE_SIGNS = re.compile(r"(?i)kill|murder|assassinate|bomb|poison|weapon\b")
SELFHARM_SIGNS = re.compile(r"(?i)suicide|self-?harm|kill\s+myself|end\s+my\s+life")
# Naive PII: long numbers, SSN-like, credit-card-like, emails
PII_EMAIL = re.compile(r"[\w.-]+@[\w.-]+\.[A-Za-z]{2,6}")
PII_LONG_NUMBER = re.compile(r"\b\d{12,19}\b")
PII_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def analyze(text: str) -> Dict[str, Any]:
    t = text or ""
    flags = {
        "jailbreak": bool(JAILBREAK_SIGNS.search(t)),
        "system_leak": bool(SYSTEM_LEAK_SIGNS.search(t)),
        "violence": bool(VIOLENCE_SIGNS.search(t)),
        "self_harm": bool(SELFHARM_SIGNS.search(t)),
        "pii_email": bool(PII_EMAIL.search(t)),
        "pii_long_number": bool(PII_LONG_NUMBER.search(t) or PII_SSN.search(t)),
    }
    flags["any_flag"] = any(flags.values())
    return flags
