import argparse
import sys
from pathlib import Path

# Add repo root to sys.path so we can import from app.server
repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from app.server.release_notes import generate_release_notes

def run(repo_path: str, start_ref: str, end_ref: str, output_path: str | None = None) -> str:
    """
    Skill to generate draft release notes between two Git references.
    Writes a markdown output.
    """
    result = generate_release_notes(repo_path, start_ref, end_ref)
    
    if output_path:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(result)
            
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Draft release notes")
    parser.add_argument("--repo-path", default=".", help="Path to repository")
    parser.add_argument("--start-ref", required=True, help="Start git ref (e.g. previous tag)")
    parser.add_argument("--end-ref", default="HEAD", help="End git ref")
    parser.add_argument("--output", help="Path to write Markdown output")
    
    args = parser.parse_args()
    
    res = run(args.repo_path, args.start_ref, args.end_ref, args.output)
    if not args.output:
        print(res)
