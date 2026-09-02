import argparse
import sys
from pathlib import Path

# Add repo root to sys.path so we can import from app.server
repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from app.server.implementation_checklist import generate_implementation_checklist

def run(repo_path: str, feature_name: str, output_path: str | None = None) -> str:
    """
    Skill to generate an implementation checklist for a given feature.
    Writes a markdown output.
    """
    result = generate_implementation_checklist(repo_path, feature_name)
    
    if output_path:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(result)
            
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate feature implementation checklist")
    parser.add_argument("--repo-path", default=".", help="Path to repository")
    parser.add_argument("--feature-name", required=True, help="Name of the feature")
    parser.add_argument("--output", help="Path to write Markdown output")
    
    args = parser.parse_args()
    
    res = run(args.repo_path, args.feature_name, args.output)
    if not args.output:
        print(res)
