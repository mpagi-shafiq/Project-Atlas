"""
Developer Triage Agent - A tool to help junior developers navigate complex repositories.

This package provides three core capabilities:
1. Repo Mapping: Automatically scan project structure and generate mission statements
2. Contextual Triage: Map GitHub issues to relevant files
3. Onboarding Guide: Generate documentation explaining data flow
"""

__version__ = "0.1.0"
__author__ = "mpagi-shafiq"

from .repo_mapper import RepoMapper
from .triage_logic import TriageEngine
from .cli import cli

__all__ = ["RepoMapper", "TriageEngine", "cli"]

# Made with Bob
