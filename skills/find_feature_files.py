import argparse
import json
import sys
from pathlib import Path

# Add repo root to sys.path so we can import from app.server
repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from app.server.repo_memory import build_feature_context

def run(repo_path: str, feature_name: str, output_path: str | None = None) -> dict:
    """
    Skill to find and collate feature context files.
    Writes a JSON output containing the related context and files for a feature.
    """
    result = build_feature_context(repo_path, feature_name)
    
    if output_path:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
            
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find feature context files")
    parser.add_argument("--repo-path", default=".", help="Path to repository")
    parser.add_argument("--feature-name", required=True, help="Name of the feature to find context for")
    parser.add_argument("--output", help="Path to write JSON output")
    
    args = parser.parse_args()
    
    res = run(args.repo_path, args.feature_name, args.output)
    if not args.output:
        print(json.dumps(res, indent=2))
