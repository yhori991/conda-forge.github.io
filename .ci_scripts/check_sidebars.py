import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parents[1]
DOCS_DIR = REPO_ROOT / "docs"
COMMUNITY_DIR = REPO_ROOT / "community"


def get_all_documents(docs_dir):
    files = []
    for ext in (".md", ".mdx", ".jsx", ".md.tmpl"):
        for f in docs_dir.rglob(f"*{ext}"):
            if f.stem.startswith("_"):
                continue
            path = str(f.relative_to(docs_dir))[: -len(ext)]
            if path.startswith("minutes/"):
                continue
            if path.startswith("funding/"):
                continue
            files.append(path)
    return files


def get_sidebar_files(items):
    files = []
    for item in items:
        if isinstance(item, str):
            if item.startswith(("http://", "https://", "mailto:")):
                continue
            files.append(item)
        elif isinstance(item, dict):
            if item.get("type") == "autogenerated":
                continue
            if item.get("type") == "doc":
                doc_id = item.get("id")
                if doc_id:
                    files.append(doc_id)  # same as a str-type item
            if "items" in item:
                files.extend(get_sidebar_files(item["items"]))
            if item.get("link", {}).get("type") == "doc":
                doc_id = item.get("link", {}).get("id")
                if doc_id:
                    files.append(doc_id)
            # shorthand syntax for categories is {"Category Name": ["file1", "file2"]}
            for value in item.values():
                if isinstance(value, list):
                    files.extend(get_sidebar_files(value))
    return files


def main():
    exit_code = 0
    for dirname in ("docs", "community"):
        print("Checking", dirname, "sidebar...")
        directory = REPO_ROOT / dirname
        docs_files = set(get_all_documents(directory))
        initial_items = json.loads((directory / "_sidebar.json").read_text())
        sidebar_files = set(get_sidebar_files(initial_items))
        missing_files_from_sidebar = docs_files - sidebar_files
        if missing_files_from_sidebar:
            print(f"The following files are missing from the {dirname}/ sidebar:")
            for f in sorted(missing_files_from_sidebar):
                print(f"  - {f}")
            print(f"Please add them to {dirname}/_sidebar.json")
            exit_code = 1
        non_existing_files_in_sidebar = sidebar_files - docs_files
        if non_existing_files_in_sidebar:
            print("The following files included in sidebar do not exist:")
            for f in sorted(non_existing_files_in_sidebar):
                print(f"  - {f}")
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())