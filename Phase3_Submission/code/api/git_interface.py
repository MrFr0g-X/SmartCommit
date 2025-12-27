"""
Git Interface - Handles repository interactions and diff extraction
Uses GitPython for repository operations
"""

import os
import logging
from typing import Optional, List, Dict
from git import Repo, GitCommandError
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitInterface:
    """Interface for Git repository operations"""

    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize Git interface

        Args:
            repo_path: Path to git repository. If None, uses current directory
        """
        self.repo_path = repo_path or os.getcwd()

        try:
            self.repo = Repo(self.repo_path)
            logger.info(f"Initialized Git interface for: {self.repo_path}")
        except Exception as e:
            logger.warning(f"Not a git repository: {e}")
            self.repo = None

    def get_diff(self, commit_id: Optional[str] = None) -> str:
        """
        Get diff for a specific commit or current working directory

        Args:
            commit_id: SHA of commit. If None, gets diff of working directory

        Returns:
            Diff string
        """
        if not self.repo:
            raise ValueError("No git repository initialized")

        try:
            if commit_id:
                # Get diff for specific commit
                commit = self.repo.commit(commit_id)
                if commit.parents:
                    parent = commit.parents[0]
                    diff = self.repo.git.diff(parent.hexsha, commit.hexsha)
                else:
                    # First commit, compare with empty tree
                    diff = commit.diff(None, create_patch=True)
                    diff = '\n'.join([d.diff.decode('utf-8') for d in diff])
            else:
                # Get diff of working directory
                diff = self.repo.git.diff('HEAD')

            return diff

        except GitCommandError as e:
            logger.error(f"Error getting diff: {e}")
            return ""

    def get_commit_history(self, max_count: int = 100) -> List[Dict]:
        """
        Get commit history with messages and diffs

        Args:
            max_count: Maximum number of commits to retrieve

        Returns:
            List of commit dictionaries
        """
        if not self.repo:
            raise ValueError("No git repository initialized")

        commits = []
        try:
            for commit in self.repo.iter_commits(max_count=max_count):
                # Get diff
                if commit.parents:
                    parent = commit.parents[0]
                    diff = self.repo.git.diff(parent.hexsha, commit.hexsha)
                else:
                    diff = ""

                commit_data = {
                    'sha': commit.hexsha,
                    'message': commit.message.strip(),
                    'author': commit.author.name,
                    'date': datetime.fromtimestamp(commit.committed_date).isoformat(),
                    'diff': diff
                }
                commits.append(commit_data)

            logger.info(f"Retrieved {len(commits)} commits")
            return commits

        except Exception as e:
            logger.error(f"Error getting commit history: {e}")
            return []

    def get_changed_files(self, commit_id: Optional[str] = None) -> List[str]:
        """Get list of changed files"""
        if not self.repo:
            raise ValueError("No git repository initialized")

        try:
            if commit_id:
                commit = self.repo.commit(commit_id)
                if commit.parents:
                    parent = commit.parents[0]
                    diff = parent.diff(commit)
                else:
                    diff = commit.diff(None)
            else:
                diff = self.repo.index.diff('HEAD')

            files = [item.a_path for item in diff]
            return files

        except Exception as e:
            logger.error(f"Error getting changed files: {e}")
            return []

    def stage_and_commit(self, message: str, files: Optional[List[str]] = None):
        """
        Stage files and create commit (for automated workflows)

        Args:
            message: Commit message
            files: List of files to stage. If None, stages all changes
        """
        if not self.repo:
            raise ValueError("No git repository initialized")

        try:
            # Stage files
            if files:
                self.repo.index.add(files)
            else:
                self.repo.git.add(A=True)

            # Commit
            self.repo.index.commit(message)
            logger.info(f"Created commit: {message[:50]}...")

        except Exception as e:
            logger.error(f"Error creating commit: {e}")
            raise

    @staticmethod
    def parse_diff_stats(diff: str) -> Dict:
        """
        Parse diff to extract statistics

        Args:
            diff: Diff string

        Returns:
            Dictionary with diff statistics
        """
        lines = diff.split('\n')

        stats = {
            'files_changed': 0,
            'insertions': 0,
            'deletions': 0,
            'total_changes': 0
        }

        current_file = None
        for line in lines:
            # Count file changes
            if line.startswith('diff --git'):
                stats['files_changed'] += 1
                current_file = line.split()[-1] if line.split() else None

            # Count insertions and deletions
            elif line.startswith('+') and not line.startswith('+++'):
                stats['insertions'] += 1
                stats['total_changes'] += 1
            elif line.startswith('-') and not line.startswith('---'):
                stats['deletions'] += 1
                stats['total_changes'] += 1

        return stats


# For testing
if __name__ == "__main__":
    # Test with current repository
    git = GitInterface()

    if git.repo:
        # Get latest commit
        commits = git.get_commit_history(max_count=1)
        if commits:
            print(f"Latest commit: {commits[0]['message']}")
            print(f"Files changed: {git.get_changed_files(commits[0]['sha'])}")

            # Get diff stats
            stats = GitInterface.parse_diff_stats(commits[0]['diff'])
            print(f"Stats: {stats}")
    else:
        print("No git repository found")
