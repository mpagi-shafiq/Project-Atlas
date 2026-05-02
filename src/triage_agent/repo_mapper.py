"""
Repo Mapper Module - Scans repository structure and generates mission statements.

This module provides functionality to:
- Walk through directory trees
- Analyze folder purposes based on contents
- Generate human-readable mission statements for each directory
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
import json


class RepoMapper:
    """Scans repository structure and generates mission statements for directories."""
    
    def __init__(self, root_path: str, ignore_patterns: Optional[List[str]] = None):
        """
        Initialize the RepoMapper.
        
        Args:
            root_path: Root directory to scan
            ignore_patterns: List of patterns to ignore (e.g., ['.venv', '__pycache__'])
        """
        self.root_path = Path(root_path)
        self.ignore_patterns = ignore_patterns or [
            '.venv', 'venv', '__pycache__', '.git', 
            'node_modules', '.pytest_cache', '.mypy_cache',
            'dist', 'build', '*.egg-info'
        ]
        self.repo_structure: Dict = {}
    
    def should_ignore(self, path: Path) -> bool:
        """
        Check if a path should be ignored based on ignore patterns.
        
        Args:
            path: Path to check
            
        Returns:
            True if path should be ignored, False otherwise
        """
        path_str = str(path)
        for pattern in self.ignore_patterns:
            if pattern in path_str or path.name.startswith('.'):
                return True
        return False
    
    def scan_directory(self, path: Optional[Path] = None, max_depth: int = 5, current_depth: int = 0) -> Dict:
        """
        Recursively scan directory structure.
        
        Args:
            path: Directory path to scan (defaults to root_path)
            max_depth: Maximum depth to scan
            current_depth: Current recursion depth
            
        Returns:
            Dictionary containing directory structure
        """
        if path is None:
            path = self.root_path
        
        if current_depth >= max_depth or self.should_ignore(path):
            return {}
        
        structure = {
            'name': path.name,
            'path': str(path.relative_to(self.root_path)),
            'type': 'directory',
            'children': [],
            'files': []
        }
        
        try:
            for item in sorted(path.iterdir()):
                if self.should_ignore(item):
                    continue
                
                if item.is_dir():
                    child_structure = self.scan_directory(item, max_depth, current_depth + 1)
                    if child_structure:
                        structure['children'].append(child_structure)
                else:
                    structure['files'].append({
                        'name': item.name,
                        'extension': item.suffix,
                        'size': item.stat().st_size
                    })
        except PermissionError:
            pass
        
        return structure
    
    def analyze_folder_purpose(self, folder_data: Dict) -> str:
        """
        Analyze folder contents and infer its purpose.
        
        Args:
            folder_data: Dictionary containing folder information
            
        Returns:
            Inferred purpose/mission statement
        """
        folder_name = folder_data.get('name', '').lower()
        files = folder_data.get('files', [])
        children = folder_data.get('children', [])
        
        # Analyze based on folder name
        name_purposes = {
            'src': 'Contains the main source code for the application',
            'tests': 'Contains unit tests and test fixtures',
            'docs': 'Contains project documentation',
            'config': 'Contains configuration files',
            'utils': 'Contains utility functions and helper modules',
            'models': 'Contains data models and database schemas',
            'views': 'Contains view templates and UI components',
            'controllers': 'Contains application controllers and business logic',
            'api': 'Contains API endpoints and routes',
            'services': 'Contains service layer and business logic',
            'static': 'Contains static assets (CSS, JS, images)',
            'templates': 'Contains HTML templates',
            'migrations': 'Contains database migration scripts',
            'scripts': 'Contains utility scripts and automation tools',
        }
        
        if folder_name in name_purposes:
            return name_purposes[folder_name]
        
        # Analyze based on file extensions
        extensions = [f.get('extension', '') for f in files]
        
        if '.py' in extensions:
            if any('test' in f.get('name', '').lower() for f in files):
                return 'Contains Python test files'
            return 'Contains Python source code'
        elif '.js' in extensions or '.ts' in extensions:
            return 'Contains JavaScript/TypeScript code'
        elif '.html' in extensions:
            return 'Contains HTML templates'
        elif '.css' in extensions or '.scss' in extensions:
            return 'Contains stylesheets'
        elif '.md' in extensions:
            return 'Contains markdown documentation'
        elif '.json' in extensions or '.yaml' in extensions or '.yml' in extensions:
            return 'Contains configuration files'
        
        # Default based on structure
        if children and not files:
            return 'Organizational directory containing subdirectories'
        elif files and not children:
            return f'Contains {len(files)} files'
        else:
            return 'Mixed content directory'
    
    def generate_mission_statements(self, structure: Optional[Dict] = None) -> Dict:
        """
        Generate mission statements for all directories in the structure.
        
        Args:
            structure: Directory structure (uses cached structure if None)
            
        Returns:
            Dictionary mapping paths to mission statements
        """
        if structure is None:
            structure = self.repo_structure
        
        missions = {}
        
        def process_directory(dir_data: Dict):
            path = dir_data.get('path', '')
            mission = self.analyze_folder_purpose(dir_data)
            missions[path] = mission
            
            for child in dir_data.get('children', []):
                process_directory(child)
        
        process_directory(structure)
        return missions
    
    def scan_repository(self) -> Dict:
        """
        Scan the entire repository and generate mission statements.
        
        Returns:
            Dictionary containing structure and mission statements
        """
        self.repo_structure = self.scan_directory()
        missions = self.generate_mission_statements()
        
        return {
            'structure': self.repo_structure,
            'missions': missions,
            'summary': {
                'total_directories': len(missions),
                'root_path': str(self.root_path)
            }
        }
    
    def save_to_file(self, output_path: str = 'repo_map.json'):
        """
        Save the repository map to a JSON file.
        
        Args:
            output_path: Path to save the JSON file
        """
        result = self.scan_repository()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        return output_path

# Made with Bob
