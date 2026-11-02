"""l2_meta_harness — Level-2 Recursive Meta-Harness Evaluator."""

from __future__ import annotations

from pathlib import Path
from typing import Any

MAX_SKILL_BYTES = 24_576  # 24KB agent skills cap
MAX_RULES_TOKENS = 20_000
MAX_RULE_FILE_BYTES = 500_000  # 500KB cap to prevent OOM / resource exhaustion


class MetaHarness:
    """Evaluates agent instructions, skills, and rule budgets for drift with bounded memory safety."""

    def __init__(self, root_dir: Path | str = ".") -> None:
        self.root_dir = Path(root_dir).resolve()

    def evaluate(self) -> dict[str, Any]:
        if not self.root_dir.is_dir():
            return {
                "status": "PASS",
                "rules_tokens_approx": 0,
                "rules_budget_max": MAX_RULES_TOKENS,
                "oversized_skills_count": 0,
                "oversized_skills": [],
                "findings": ["Directory does not exist; empty evaluation."],
            }

        oversized_skills: list[dict[str, Any]] = []
        rules_tokens = 0
        findings: list[str] = []

        # Check skills
        for skill_file in self.root_dir.rglob("SKILL.md"):
            try:
                size = skill_file.stat().st_size
                if size > MAX_SKILL_BYTES:
                    oversized_skills.append(
                        {
                            "path": str(skill_file.relative_to(self.root_dir)),
                            "size_bytes": size,
                            "limit_bytes": MAX_SKILL_BYTES,
                        }
                    )
                    findings.append(
                        f"Oversized skill: {skill_file.name} ({size} > {MAX_SKILL_BYTES})"
                    )
            except OSError:
                continue

        # Check rules with bounded file read
        for rule_file in self.root_dir.rglob("*.md"):
            if "rules" in rule_file.parts or rule_file.name in ("AGENTS.md", "GEMINI.md"):
                try:
                    size = rule_file.stat().st_size
                    if size > MAX_RULE_FILE_BYTES:
                        findings.append(
                            f"Rule file {rule_file.name} exceeds safe memory limit ({size} bytes)"
                        )
                        approx_tokens = size // 4
                    else:
                        content = rule_file.read_text(encoding="utf-8", errors="ignore")
                        approx_tokens = len(content) // 4
                    rules_tokens += approx_tokens
                except OSError:
                    continue

        budget_status = "PASS" if rules_tokens <= MAX_RULES_TOKENS else "OVERBUDGET"
        if budget_status == "OVERBUDGET":
            findings.append(f"Rules tokens {rules_tokens} exceed budget {MAX_RULES_TOKENS}")

        status = "PASS" if not findings else "DRIFT"

        return {
            "status": status,
            "rules_tokens_approx": rules_tokens,
            "rules_budget_max": MAX_RULES_TOKENS,
            "oversized_skills_count": len(oversized_skills),
            "oversized_skills": oversized_skills,
            "findings": findings,
        }
