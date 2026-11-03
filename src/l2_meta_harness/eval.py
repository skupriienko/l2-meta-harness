"""l2_meta_harness — Level-2 Recursive Meta-Harness Evaluator."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

MAX_SKILL_BYTES = 24_576  # 24KB agent skills cap
MAX_RULES_TOKENS = 20_000
MAX_RULE_FILE_BYTES = 500_000  # 500KB cap to prevent OOM / resource exhaustion


@dataclass(frozen=True)
class OversizedSkill:
    """Records an agent skill exceeding the 24KB cap."""

    path: str
    size_bytes: int
    limit_bytes: int = MAX_SKILL_BYTES

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "size_bytes": self.size_bytes,
            "limit_bytes": self.limit_bytes,
        }


@dataclass(frozen=True)
class EvalResult:
    """Structured result of Level-2 meta-harness audit."""

    status: str
    rules_tokens_approx: int
    rules_budget_max: int
    oversized_skills_count: int
    oversized_skills: list[OversizedSkill] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "rules_tokens_approx": self.rules_tokens_approx,
            "rules_budget_max": self.rules_budget_max,
            "oversized_skills_count": self.oversized_skills_count,
            "oversized_skills": [s.to_dict() for s in self.oversized_skills],
            "findings": self.findings,
        }


class MetaHarness:
    """Evaluates agent instructions, skills, and rule budgets for drift with bounded memory safety."""

    def __init__(self, root_dir: Path | str = ".") -> None:
        self.root_dir = Path(root_dir).resolve()

    def eval(self) -> EvalResult:
        """Evaluates framework rules and skills returning typed EvalResult."""
        if not self.root_dir.is_dir():
            return EvalResult(
                status="PASS",
                rules_tokens_approx=0,
                rules_budget_max=MAX_RULES_TOKENS,
                oversized_skills_count=0,
                oversized_skills=[],
                findings=["Directory does not exist; empty evaluation."],
            )

        oversized_skills: list[OversizedSkill] = []
        rules_tokens = 0
        findings: list[str] = []

        # Check skills
        for skill_file in self.root_dir.rglob("SKILL.md"):
            try:
                size = skill_file.stat().st_size
                if size > MAX_SKILL_BYTES:
                    oversized_skills.append(
                        OversizedSkill(
                            path=str(skill_file.relative_to(self.root_dir)),
                            size_bytes=size,
                        )
                    )
                    findings.append(
                        f"Oversized skill: {skill_file.name} ({size} > {MAX_SKILL_BYTES})"
                    )
            except OSError:
                continue

        # Check rules with bounded file read
        for rule_file in self.root_dir.rglob("*.md"):
            if "rules" in rule_file.parts or rule_file.name in (
                "AGENTS.md",
                "GEMINI.md",
            ):
                try:
                    size = rule_file.stat().st_size
                    if size > MAX_RULE_FILE_BYTES:
                        findings.append(
                            f"Rule file {rule_file.name} exceeds safe memory limit ({size} bytes)"
                        )
                        continue
                    text = rule_file.read_text(encoding="utf-8", errors="ignore")
                    rules_tokens += len(text) // 4
                except OSError:
                    continue

        if rules_tokens > MAX_RULES_TOKENS:
            findings.append(
                f"Rules tokens (~{rules_tokens}) exceeded budget ceiling of {MAX_RULES_TOKENS}"
            )

        status = "DRIFT" if findings else "PASS"

        return EvalResult(
            status=status,
            rules_tokens_approx=rules_tokens,
            rules_budget_max=MAX_RULES_TOKENS,
            oversized_skills_count=len(oversized_skills),
            oversized_skills=oversized_skills,
            findings=findings,
        )

    def evaluate(self) -> dict[str, Any]:
        """Backward-compatible dictionary evaluate method."""
        return self.eval().to_dict()
