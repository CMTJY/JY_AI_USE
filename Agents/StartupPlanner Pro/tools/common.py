from pathlib import Path
import re

import yaml


def load_yaml(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def parse_frontmatter(path):
    text = Path(path).read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not match:
        raise ValueError(f"missing frontmatter: {path}")
    return yaml.safe_load(match.group(1)), text[match.end():].lstrip()


def write_yaml(path, value):
    Path(path).write_text(
        yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
        newline="\n",
    )


def role_files(root):
    for path in (Path(root) / "agents").rglob("*.md"):
        if "skills" not in path.parts and "templates" not in path.parts:
            yield path

