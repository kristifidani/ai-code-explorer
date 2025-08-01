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
    # Only allow URLs matching the GitHub repo pattern (HTTPS, SSH, and git protocols)
    github_repo_pattern = (
        r"^(?:"
        r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?/?"
        r"|git@github\.com:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\.git"
        r"|git://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\.git"
        r")$"
    )
    if not re.match(github_repo_pattern, repo_url):
        raise errors.InvalidParam.invalid_repo_url()
    clone_to = tempfile.mkdtemp()
    try:
        Repo.clone_from(repo_url, clone_to)
    except GitCommandError as e:
        shutil.rmtree(clone_to, ignore_errors=True)
        raise errors.GitCloneError.failed(e) from e
    else:
        return clone_to


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
