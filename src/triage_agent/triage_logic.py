"""
Triage Logic Module - Maps GitHub issues to relevant files.

This module provides functionality to:
- Fetch GitHub issues via API
- Extract keywords from issue descriptions
- Rank files by relevance to the issue
- Identify the top 3 most relevant files
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import Counter
from github import Github, GithubException
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class TriageEngine:
    """Maps GitHub issues to relevant files in the repository."""
    
    def __init__(self, repo_path: str, github_token: Optional[str] = None):
        """
        Initialize the TriageEngine.
        
        Args:
            repo_path: Path to the repository
            github_token: GitHub personal access token (optional, will use GITHUB_TOKEN from .env if not provided)
        """
        self.repo_path = Path(repo_path)
        # Use provided token or fall back to environment variable
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.github_client = None
        
        if github_token:
            self.github_client = Github(github_token)
    
    def fetch_github_issue(self, repo_name: str, issue_number: int) -> Dict:
        """
        Fetch issue details from GitHub.
        
        Args:
            repo_name: Repository name in format 'owner/repo'
            issue_number: Issue number
            
        Returns:
            Dictionary containing issue details
        """
        if not self.github_client:
            raise ValueError("GitHub token required to fetch issues")
        
        try:
            repo = self.github_client.get_repo(repo_name)
            issue = repo.get_issue(issue_number)
            
            return {
                'number': issue.number,
                'title': issue.title,
                'body': issue.body or '',
                'labels': [label.name for label in issue.labels],
                'state': issue.state,
                'created_at': issue.created_at.isoformat(),
                'url': issue.html_url
            }
        except GithubException as e:
            raise Exception(f"Failed to fetch issue: {e}")
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract relevant keywords from text.
        
        Args:
            text: Text to extract keywords from
            
        Returns:
            List of keywords
        """
        # Convert to lowercase and remove special characters
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Split into words
        words = text.split()
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'what', 'which', 'who', 'when', 'where', 'why', 'how'
        }
        
        # Filter out stop words and short words
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Return unique keywords, prioritizing by frequency
        word_counts = Counter(keywords)
        return [word for word, _ in word_counts.most_common()]
    
    def get_file_content(self, file_path: Path) -> str:
        """
        Read file content safely.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content as string, or empty string if unable to read
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except (UnicodeDecodeError, PermissionError, FileNotFoundError):
            return ''
    
    def calculate_relevance_score(self, file_path: Path, keywords: List[str]) -> float:
        """
        Calculate relevance score for a file based on keywords.
        
        Args:
            file_path: Path to the file
            keywords: List of keywords to search for
            
        Returns:
            Relevance score (0.0 to 1.0)
        """
        if not file_path.exists() or not file_path.is_file():
            return 0.0
        
        # Get file content
        content = self.get_file_content(file_path).lower()
        if not content:
            return 0.0
        
        # Calculate score based on keyword matches
        score = 0.0
        total_keywords = len(keywords)
        
        if total_keywords == 0:
            return 0.0
        
        for i, keyword in enumerate(keywords):
            # Weight earlier keywords more heavily
            weight = 1.0 - (i / total_keywords) * 0.5
            
            # Count occurrences
            occurrences = content.count(keyword)
            
            if occurrences > 0:
                # Bonus for filename match
                if keyword in file_path.name.lower():
                    score += weight * 2.0
                
                # Score based on occurrences (with diminishing returns)
                score += weight * min(occurrences, 5) / 5.0
        
        # Normalize score
        max_possible_score = sum(1.0 - (i / total_keywords) * 0.5 for i in range(total_keywords)) * 2.0
        normalized_score = min(score / max_possible_score, 1.0) if max_possible_score > 0 else 0.0
        
        return normalized_score
    
    def find_relevant_files(self, keywords: List[str], max_files: int = 3, 
                          file_extensions: Optional[List[str]] = None) -> List[Tuple[str, float]]:
        """
        Find the most relevant files based on keywords.
        
        Args:
            keywords: List of keywords to search for
            max_files: Maximum number of files to return
            file_extensions: List of file extensions to consider (e.g., ['.py', '.js'])
            
        Returns:
            List of tuples (file_path, relevance_score) sorted by relevance
        """
        if file_extensions is None:
            file_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rb', '.php']
        
        file_scores = []
        
        # Walk through repository
        for file_path in self.repo_path.rglob('*'):
            # Skip directories and non-matching extensions
            if not file_path.is_file():
                continue
            
            if file_path.suffix not in file_extensions:
                continue
            
            # Skip ignored directories
            if any(part.startswith('.') or part in ['__pycache__', 'node_modules', 'venv', '.venv'] 
                   for part in file_path.parts):
                continue
            
            # Calculate relevance score
            score = self.calculate_relevance_score(file_path, keywords)
            
            if score > 0:
                relative_path = str(file_path.relative_to(self.repo_path))
                file_scores.append((relative_path, score))
        
        # Sort by score (descending) and return top N
        file_scores.sort(key=lambda x: x[1], reverse=True)
        return file_scores[:max_files]
    
    def analyze_issue(self, issue_data: Dict, max_files: int = 3) -> Dict:
        """
        Analyze a GitHub issue and find relevant files.
        
        Args:
            issue_data: Dictionary containing issue details
            max_files: Maximum number of files to return
            
        Returns:
            Dictionary containing analysis results
        """
        # Extract keywords from title and body
        title_keywords = self.extract_keywords(issue_data.get('title', ''))
        body_keywords = self.extract_keywords(issue_data.get('body', ''))
        
        # Combine keywords, prioritizing title
        all_keywords = title_keywords + body_keywords
        
        # Find relevant files
        relevant_files = self.find_relevant_files(all_keywords, max_files)
        
        return {
            'issue_number': issue_data.get('number'),
            'issue_title': issue_data.get('title'),
            'keywords': all_keywords[:10],  # Top 10 keywords
            'relevant_files': [
                {
                    'path': path,
                    'relevance_score': round(score, 3),
                    'confidence': 'high' if score > 0.7 else 'medium' if score > 0.4 else 'low'
                }
                for path, score in relevant_files
            ],
            'total_files_analyzed': len(list(self.repo_path.rglob('*.py')))
        }
    
    def triage_issue_by_number(self, repo_name: str, issue_number: int, max_files: int = 3) -> Dict:
        """
        Fetch and analyze a GitHub issue by number.
        
        Args:
            repo_name: Repository name in format 'owner/repo'
            issue_number: Issue number
            max_files: Maximum number of files to return
            
        Returns:
            Dictionary containing triage results
        """
        issue_data = self.fetch_github_issue(repo_name, issue_number)
        return self.analyze_issue(issue_data, max_files)

# Made with Bob
