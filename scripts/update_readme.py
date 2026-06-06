import os
import re

# Config
PROBLEMS_DIR   = "problems"
README_PATH    = "README.md"
TOTAL_PROBLEMS = 280
BAR_LENGTH     = 25

# Collect solved problems
# Each problem is either:
#   - a subdirectory containing index.md  (e.g. problems/dna-counting/index.md)
#   - a standalone .md file directly in problems/
def collect_problems(directory: str) -> list[tuple[str, str]]:
    if not os.path.isdir(directory):
        return []

    found = []
    for entry in os.scandir(directory):
        if entry.name == ".gitkeep":
            continue
        if entry.is_dir():
            index_path = os.path.join(entry.path, "index.md")
            if os.path.isfile(index_path):
                name = entry.name.replace("-", " ").title()
                link = f"./problems/{entry.name}/"
                found.append((name, link))
        elif entry.is_file() and entry.name.endswith(".md"):
            name = entry.name[:-3].replace("-", " ").title()
            link = f"./problems/{entry.name}"
            found.append((name, link))

    return sorted(found, key=lambda x: x[0])

# Build the markdown block
def build_progress_block(problems: list[tuple[str, str]]) -> tuple[str, int, float]:
    count = len(problems)
    pct   = (count / TOTAL_PROBLEMS) * 100

    filled = round((count / TOTAL_PROBLEMS) * BAR_LENGTH)
    bar    = "█" * filled + "░" * (BAR_LENGTH - filled)

    if count == 0:
        table = "| - | *No problems solved yet.* |"
    else:
        rows = []
        for i, (name, link) in enumerate(problems, start=1):
            rows.append(f"| {i} | [{name}]({link}) |")
        table = "\n".join(rows)

    block = (
        f"**Progress: {count} / {TOTAL_PROBLEMS} ({pct:.1f}%)**\n\n"
        f"`{bar}` {pct:.1f}%\n\n"
        f"| # | Post |\n"
        f"|---|------|\n"
        f"{table}"
    )
    return block, count, pct

# Inject into README
def update_readme(readme_path: str, new_block: str) -> None:
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern     = r"(<!-- PROGRESS_START -->).*?(<!-- PROGRESS_END -->)"
    replacement = rf"\1\n{new_block}\n\2"

    new_content, num_subs = re.subn(pattern, replacement, content, flags=re.DOTALL)

    if num_subs == 0:
        raise ValueError(
            "Could not find <!-- PROGRESS_START --> / <!-- PROGRESS_END --> "
            "markers in README.md. Make sure both markers are present."
        )

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)

# Entry point
if __name__ == "__main__":
    problems          = collect_problems(PROBLEMS_DIR)
    block, count, pct = build_progress_block(problems)
    update_readme(README_PATH, block)
    print(f"README updated: {count} / {TOTAL_PROBLEMS} problems solved ({pct:.1f}%)")
