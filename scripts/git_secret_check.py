#!/usr/bin/env python3
"""
CrowdWisdom AI Studio — Pre-Commit & CI Secret Scanner
Inspects staged files or the entire repository for accidentally exposed credentials,
API keys, access tokens, and database passwords.

Exits with code 1 if any unmasked secret is detected, aborting the commit.
"""
import os
import re
import sys
import subprocess
from pathlib import Path

# Sensitive Key Patterns (Real Production Formats)
SECRET_REGEXES = {
    "Google Gemini API Key": re.compile(r"AIzaSy[A-Za-z0-9_-]{33}"),
    "Google Gemini Alt Key": re.compile(r"AQ\.[A-Za-z0-9_-]{40,}"),
    "OpenAI API Key": re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    "OpenAI Project Key": re.compile(r"sk-proj-[A-Za-z0-9_-]{30,}"),
    "OpenRouter API Key": re.compile(r"sk-or-v1-[A-Za-z0-9_-]{30,}"),
    "Anthropic API Key": re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"),
    "NVIDIA NIM API Key": re.compile(r"nvapi-[A-Za-z0-9_-]{20,}"),
    "Apify API Token": re.compile(r"apify_api_[A-Za-z0-9_-]{20,}"),
    "Tavily API Key": re.compile(r"tvly-[A-Za-z0-9_-]{20,}"),
    "Resend API Key": re.compile(r"re_[A-Za-z0-9_-]{20,}"),
    "MongoDB URI with Credentials": re.compile(r"mongodb(?:\+srv)?://([^:]+):([^@]+)@"),
    "Generic Private Key": re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
}

# Directories to exclude from scanning
IGNORED_DIRS = {
    ".git",
    "node_modules",
    ".pytest_cache",
    "__pycache__",
    ".storage_quarantine",
    "dist",
    "build",
    "vendor",
}

# Files that are allowed to define placeholder names
ALLOWED_FILES = {
    ".env.example",
    ".gitignore",
    "scripts/git_secret_check.py",
}

SAFE_PLACEHOLDERS = [
    "your_",
    "replace_with",
    "placeholder",
    "example",
    "dummy",
    "mock",
    "test_",
    "change-this",
    "[REDACTED]",
    "****",
    "...",
    "<",
    ">",
]


def mask(val: str) -> str:
    if len(val) <= 8:
        return "*" * len(val)
    return val[:4] + "****" + val[-4:]


def is_placeholder(val: str) -> bool:
    v = val.lower()
    return any(p in v for p in SAFE_PLACEHOLDERS)


def scan_file_content(file_path: Path, content: str) -> list:
    findings = []
    lines = content.splitlines()
    for line_idx, line in enumerate(lines, 1):
        for name, pattern in SECRET_REGEXES.items():
            for match in pattern.finditer(line):
                matched = match.group(0)
                if is_placeholder(matched):
                    continue
                # Skip if line is clearly a mock or test marker
                if "unit-test" in line.lower() or "looks-real-but-must-not-be-used" in line:
                    continue
                findings.append({
                    "file": str(file_path),
                    "line": line_idx,
                    "type": name,
                    "masked": mask(matched),
                    "snippet": line.strip()[:100],
                })
    return findings


def get_staged_files() -> list:
    try:
        out = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            text=True,
            errors="ignore",
        )
        return [f.strip() for f in out.splitlines() if f.strip()]
    except Exception:
        return []


def main():
    mode = "--all" if "--all" in sys.argv else "--staged"
    repo_root = Path(__file__).resolve().parent.parent

    print("=" * 70)
    print(f"CrowdWisdom AI Studio — Secret Protection Scanner ({mode})")
    print("=" * 70)

    files_to_scan = []
    if mode == "--staged":
        staged = get_staged_files()
        for s in staged:
            p = repo_root / s
            if p.is_file():
                files_to_scan.append(p)
    else:
        for root, dirs, files in os.walk(repo_root):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            for f in files:
                p = Path(root) / f
                if p.suffix.lower() in [".png", ".jpg", ".jpeg", ".mp4", ".webm", ".ico", ".svg", ".pyc"]:
                    continue
                files_to_scan.append(p)

    total_findings = []
    for fp in files_to_scan:
        rel = fp.relative_to(repo_root).as_posix()
        if rel in ALLOWED_FILES:
            continue
        try:
            content = fp.read_text(encoding="utf-8", errors="ignore")
            findings = scan_file_content(rel, content)
            total_findings.extend(findings)
        except Exception:
            pass

    if total_findings:
        print(f"\n[BLOCKED] Found {len(total_findings)} potential unmasked secret(s)!")
        for f in total_findings:
            print(f"  - {f['file']}:{f['line']} [{f['type']}] -> {f['masked']}")
            print(f"    Line: {f['snippet']}")
        print("\nCommit rejected! Remove credentials before committing.")
        sys.exit(1)
    else:
        print(f"\n[PASS] No secrets detected in {len(files_to_scan)} scanned file(s).")
        sys.exit(0)


if __name__ == "__main__":
    main()
