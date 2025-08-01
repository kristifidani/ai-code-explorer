import os
import tempfile
import shutil
import re

from ai_service import errors

from git import Repo, GitCommandError

CODE_EXTENSIONS = {
    # Programming languages
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
    ".jsx",
    ".tsx",
    ".vue",
    ".dart",
    ".r",
    ".m",
    # Web technologies
    ".html",
    ".css",
    ".scss",
    ".sass",
    ".less",
    # Configuration and documentation
    ".toml",
    ".md",
    ".yml",
    ".yaml",
    ".json",
    ".xml",
    ".ini",
    ".cfg",
    ".conf",
}


def clone_github_repo(repo_url: str) -> str:
    """
    Clones a GitHub repo to a temporary directory.
    Returns the path to the cloned directory.
    Validates the repo_url to prevent command injection.
    """
    # Only allow URLs matching the GitHub repo pattern
    github_repo_pattern = r"^https://github\.com/[\w\-\.]+/[\w\-\.]+(\.git)?/?$"
    if not re.match(github_repo_pattern, repo_url):
        raise errors.InvalidParam.invalid_repo_url()
    clone_to = tempfile.mkdtemp()
    try:
        Repo.clone_from(repo_url, clone_to)
        return clone_to
    except GitCommandError as e:
        raise errors.GitCloneError.failed(e) from e


def scan_code_files(root_dir: str) -> list[str]:
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
