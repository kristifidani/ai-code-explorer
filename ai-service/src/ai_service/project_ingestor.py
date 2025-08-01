import os
import tempfile
import shutil
from typing import List, Dict

# For GitHub cloning
import subprocess

CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".java",
    ".go",
    ".rs",
    ".cpp",
    ".c",
    ".cs",
    ".rb",
    ".php",
    ".swift",
    ".kt",
    ".scala",
    ".sh",
    ".html",
    ".css",
    ".toml",
    ".md",
    ".yml",
}


def clone_github_repo(repo_url: str) -> str:
    """
    Clones a GitHub repo to a temporary directory.
    Returns the path to the cloned directory.
    """
    clone_to = tempfile.mkdtemp()
    subprocess.run(["git", "clone", repo_url, clone_to], check=True)
    return clone_to


def scan_code_files(root_dir: str) -> List[Dict]:
    """
    Scans the project directory for code files with given extensions.
    Returns a list of file paths.
    """
    code_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if any(file.endswith(ext) for ext in CODE_EXTENSIONS):
                code_files.append(os.path.join(root, file))
    return code_files


def cleanup_dir(path: str) -> None:
    """
    Removes a directory and all its contents.
    """
    shutil.rmtree(path, ignore_errors=True)
