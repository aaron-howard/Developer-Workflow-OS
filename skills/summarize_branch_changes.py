import argparse
import json
import sys
from pathlib import Path

# Add repo root to sys.path so we can import from app.server
repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from app.server.branch_summary import summarize_branch

def run(repo_path: str, base_branch: str, target_branch: str, output_path: str | None = None) -> dict:
    """
    Skill to summarize changes between two branches.
    Writes a JSON output containing the changed files, summary, and risk areas.
    """
    result = summarize_branch(repo_path, base_branch, target_branch)
    
    if output_path:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
            
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize branch changes")
    parser.add_argument("--repo-path", default=".", help="Path to repository")
    parser.add_argument("--base-branch", required=True, help="Base branch (e.g. main)")
    parser.add_argument("--target-branch", required=True, help="Target branch to summarize")
    parser.add_argument("--output", help="Path to write JSON output")
    
    args = parser.parse_args()
    
    res = run(args.repo_path, args.base_branch, args.target_branch, args.output)
    if not args.output:
        print(json.dumps(res, indent=2))
