import logging
import os
import tempfile
import shutil

from ai_service import errors

from git import Repo, GitCommandError

logger = logging.getLogger(__name__)


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


def clone_github_repo(canonical_github_url: str) -> str:
    """
    Clones a GitHub repo to a temporary directory.
    Returns the path to the cloned directory.
    """
    clone_to = tempfile.mkdtemp()
    try:
        Repo.clone_from(canonical_github_url, clone_to)
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
    logger.info("Scanning project directory ...")
    code_files: list[str] = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if any(file.endswith(ext) for ext in CODE_EXTENSIONS):
                code_files.append(os.path.join(root, file))
    return code_files


def cleanup_dir(path: str) -> None:
    """
    Removes a directory and all its contents.
    """
    logger.info("Cleaning up project directory ...")
    shutil.rmtree(path, ignore_errors=True)
