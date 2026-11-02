import time
from pathlib import Path

from l2_meta_harness.evaluator import MetaHarness


def test_stress_meta_harness(tmp_path: Path):
    # Create 100 mock skills and 50 rules
    for i in range(100):
        skill_dir = tmp_path / f"skill_{i}"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(f"---\nname: skill_{i}\n---\n# Skill {i}\n" * 10)

    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    for j in range(50):
        (rules_dir / f"rule_{j}.md").write_text(f"# Rule {j}\nInvariant line\n" * 20)

    t0 = time.perf_counter()
    harness = MetaHarness(tmp_path)
    res = harness.evaluate()
    duration = time.perf_counter() - t0

    assert res["status"] == "PASS"
    assert res["oversized_skills_count"] == 0
    assert duration < 0.3, f"Harness eval took {duration}s (expected <0.3s)"
