"""Approval gate helpers.

Every skill that publishes to YouTube MUST present a draft to the user and wait
for explicit approval before calling Publora. This file is a thin conventions
layer, not runtime enforcement. Skills call `render_approval_card` to format the
draft consistently and then stop until the user says go.
"""
from __future__ import annotations
from typing import Optional


def render_approval_card(
    *,
    kind: str,  # "video" | "short" | "community" | "title" | "thumbnail"
    preview_text: str,
    target_url: Optional[str] = None,
    title_chars: Optional[int] = None,
    desc_chars: Optional[int] = None,
    extra_context: Optional[dict] = None,
) -> str:
    """Format a standardized approval card for the user to review.

    The card MUST contain:
    - What the action is (video / short / community / title / thumbnail)
    - The full preview text (title + description, script, or post)
    - Title char count (cap 100) and description char count (cap 5,000) where they apply
    - Target URL if applicable (YouTube Studio upload, or the Community tab)
    - A clear prompt: "reply publish / yes, or suggest edits"
    """
    lines = [f"## Draft ready for approval - {kind}", ""]
    if target_url:
        lines.append(f"**Target:** {target_url}")
    if title_chars is not None:
        flag = " (OVER 100)" if title_chars > 100 else ""
        lines.append(f"**Title chars:** {title_chars}/100{flag}")
    if desc_chars is not None:
        flag = " (OVER 5000)" if desc_chars > 5000 else ""
        lines.append(f"**Description chars:** {desc_chars}/5000{flag}")
    lines.append("")
    lines.append("**Preview:**")
    lines.append("")
    for pl in preview_text.splitlines() or [""]:
        lines.append(f"> {pl}")
    lines.append("")
    if extra_context:
        lines.append("**Context:**")
        for k, v in extra_context.items():
            lines.append(f"- **{k}**: {v}")
        lines.append("")
    lines.append("Reply **publish** / **yes** to proceed, or suggest edits.")
    return "\n".join(lines)
