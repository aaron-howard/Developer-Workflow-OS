import argparse
import sys
from pathlib import Path

# Add repo root to sys.path so we can import from app.server
repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from app.server.sprint_recap import generate_sprint_recap

def run(repo_path: str, output_path: str | None = None) -> str:
    """
    Skill to generate a weekly sprint summary.
    Writes a markdown output.
    """
    result = generate_sprint_recap(repo_path)
    
    if output_path:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(result)
            
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate weekly sprint summary")
    parser.add_argument("--repo-path", default=".", help="Path to repository")
    parser.add_argument("--output", help="Path to write Markdown output")
    
    args = parser.parse_args()
    
    res = run(args.repo_path, args.output)
    if not args.output:
        print(res)
