"""CLI interface for l2-meta-harness."""

import argparse
import json
import sys

from l2_meta_harness.eval import MetaHarness


def main() -> None:
    parser = argparse.ArgumentParser(
        description="meta-harness: Level-2 Recursive Meta-Harness & Drift Evaluator"
    )
    parser.add_argument("path", nargs="?", default=".", help="Directory to evaluate")
    parser.add_argument("--json", action="store_true", help="Output JSON receipt")

    args = parser.parse_args()
    harness = MetaHarness(args.path)
    res = harness.evaluate()

    if args.json:
        print(json.dumps(res, indent=2))
        sys.exit(0 if res["status"] == "PASS" else 1)

    print(f"\n⚖️ Level-2 Meta-Harness Evaluation for '{args.path}':")
    print(f"  • Status: {res['status']}")
    print(f"  • Estimated Rules Tokens: {res['rules_tokens_approx']} / {res['rules_budget_max']}")
    print(f"  • Oversized Skills (>24KB): {res['oversized_skills_count']}")

    if res["findings"]:
        print("\n⚠️ Detected Drift Findings:")
        for f in res["findings"]:
            print(f"    - {f}")

    print(
        f"\n[RECEIPT] status={res['status']} sensor=meta_harness tokens={res['rules_tokens_approx']}"
    )
    sys.exit(0 if res["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
