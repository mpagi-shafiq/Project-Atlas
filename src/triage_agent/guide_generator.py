"""
Guide Generator Module - Creates onboarding documentation for junior developers.

This module provides functionality to:
- Generate JUNIOR_GUIDE.md with mission statements
- Explain data flow for specific features
- Create professional markdown documentation
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class GuideGenerator:
    """Generates onboarding guides for junior developers."""
    
    def __init__(self, repo_path: str = '.'):
        """
        Initialize the GuideGenerator.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = Path(repo_path)
    
    def load_repo_map(self, repo_map_path: str = 'repo_map.json') -> Dict:
        """
        Load repository map from JSON file.
        
        Args:
            repo_map_path: Path to the repo_map.json file
            
        Returns:
            Dictionary containing repository structure and missions
        """
        map_file = Path(repo_map_path)
        if not map_file.exists():
            raise FileNotFoundError(
                f"Repository map not found at {repo_map_path}. "
                "Run 'triage-agent map' first to generate it."
            )
        
        with open(map_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_file_mission(self, file_path: str, repo_map: Dict) -> Optional[str]:
        """
        Get the mission statement for a file's directory.
        
        Args:
            file_path: Path to the file
            repo_map: Repository map data
            
        Returns:
            Mission statement or None if not found
        """
        missions = repo_map.get('missions', {})
        
        # Try to find mission for the file's directory
        file_path_obj = Path(file_path)
        
        # Check parent directories from most specific to least specific
        for parent in [file_path_obj.parent] + list(file_path_obj.parents):
            parent_str = str(parent).replace('\\', '/')
            if parent_str == '.':
                parent_str = ''
            
            if parent_str in missions:
                return missions[parent_str]
        
        return None
    
    def read_file_snippet(self, file_path: str, max_lines: int = 20) -> str:
        """
        Read a snippet from a file for documentation.
        
        Args:
            file_path: Path to the file
            max_lines: Maximum number of lines to read
            
        Returns:
            File content snippet
        """
        full_path = self.repo_path / file_path
        
        if not full_path.exists():
            return "File not found"
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:max_lines]
                content = ''.join(lines)
                
                if len(lines) == max_lines:
                    content += "\n... (truncated)"
                
                return content
        except (UnicodeDecodeError, PermissionError):
            return "Unable to read file content"
    
    def generate_guide_from_triage(
        self,
        feature_name: str,
        relevant_files: List[Dict],
        repo_map: Optional[Dict] = None,
        output_path: str = 'JUNIOR_GUIDE.md'
    ) -> str:
        """
        Generate a junior developer guide based on triage results.
        
        Args:
            feature_name: Name of the feature being documented
            relevant_files: List of relevant files from triage (with path and relevance_score)
            repo_map: Repository map data (will load if not provided)
            output_path: Path to save the guide
            
        Returns:
            Path to the generated guide
        """
        if repo_map is None:
            try:
                repo_map = self.load_repo_map()
            except FileNotFoundError:
                repo_map = {'missions': {}}
        
        # Generate the markdown content
        guide_content = self._create_guide_content(feature_name, relevant_files, repo_map)
        
        # Write to file
        output_file = Path(output_path)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        return str(output_file)
    
    def _create_guide_content(
        self,
        feature_name: str,
        relevant_files: List[Dict],
        repo_map: Dict
    ) -> str:
        """
        Create the markdown content for the guide.
        
        Args:
            feature_name: Name of the feature
            relevant_files: List of relevant files
            repo_map: Repository map data
            
        Returns:
            Markdown content as string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = f"""# Junior Developer Guide: {feature_name}

> **Generated:** {timestamp}  
> **Purpose:** Help junior developers understand the codebase structure and navigate relevant files

---

## 📋 Overview

This guide provides an overview of the key files related to **{feature_name}**. Each section includes:
- File location and purpose
- Mission statement (what this part of the codebase does)
- Relevance score (how closely it matches your feature)
- Code preview

---

## 🎯 Key Files to Explore

"""
        
        # Add each relevant file
        for i, file_info in enumerate(relevant_files, 1):
            file_path = file_info.get('path', 'Unknown')
            relevance = file_info.get('relevance_score', 0)
            confidence = file_info.get('confidence', 'unknown')
            
            # Get mission statement
            mission = self.get_file_mission(file_path, repo_map)
            if not mission:
                mission = "No mission statement available. This file may be part of a specialized module."
            
            # Get file extension for syntax highlighting
            file_ext = Path(file_path).suffix.lstrip('.')
            if file_ext in ['py', 'js', 'ts', 'java', 'cpp', 'c', 'go', 'rb', 'php']:
                lang = file_ext
            else:
                lang = 'text'
            
            # Read file snippet
            snippet = self.read_file_snippet(file_path)
            
            # Confidence emoji
            confidence_emoji = {
                'high': '🟢',
                'medium': '🟡',
                'low': '🔴'
            }.get(confidence, '⚪')
            
            content += f"""### {i}. `{file_path}` {confidence_emoji}

**Relevance Score:** {relevance:.1%} ({confidence} confidence)

**Directory Mission:**
> {mission}

**Why This File Matters:**
This file scored {relevance:.1%} relevance to "{feature_name}". It's located in a directory that {mission.lower()}

**Code Preview:**
```{lang}
{snippet}
```

---

"""
        
        # Add navigation guide
        content += """## 🗺️ How to Navigate

### Step 1: Start with the Highest Relevance File
Begin by exploring the file with the highest relevance score (marked with 🟢). This is most likely where the core logic for your feature resides.

### Step 2: Understand the Directory Structure
Pay attention to the "Directory Mission" for each file. This tells you the purpose of that section of the codebase.

### Step 3: Follow the Data Flow
Look for:
- **Function calls** - Where does data come from and where does it go?
- **Imports** - What other modules does this file depend on?
- **Class definitions** - What objects are being created and manipulated?

### Step 4: Check Related Files
Files in the same directory often work together. If you see imports from nearby files, explore those next.

---

## 💡 Tips for Junior Developers

### Understanding Relevance Scores
- **🟢 High (>70%)**: This file is very likely related to your feature. Start here!
- **🟡 Medium (40-70%)**: This file has some relevance. Check it after high-confidence files.
- **🔴 Low (<40%)**: This file might have tangential relevance. Explore if needed.

### Reading Code Effectively
1. **Start with function/class names** - They often describe what the code does
2. **Read comments and docstrings** - Previous developers left clues!
3. **Trace variable names** - Follow how data transforms through the code
4. **Use your IDE** - Jump to definitions and find references

### When You're Stuck
- Look for test files (usually in `tests/` or `test_*.py`)
- Check for README files in subdirectories
- Search for the feature name in comments
- Ask senior developers about the "Directory Mission" concepts

---

## 📚 Additional Resources

### Repository Structure
Run `triage-agent map` to see the full repository structure with mission statements for all directories.

### Issue Triage
Use `triage-agent issue <number>` to find relevant files for specific GitHub issues.

### Documentation
Check the main README.md and any docs/ directory for additional context.

---

## 🚀 Next Steps

1. **Open the top file** in your IDE
2. **Set breakpoints** or add print statements to understand the flow
3. **Run the tests** related to this feature
4. **Make small changes** and observe the effects
5. **Ask questions** - No question is too basic!

---

*Generated by Developer Triage Agent - Helping junior developers navigate complex codebases*
"""
        
        return content
    
    def generate_simple_guide(
        self,
        feature_name: str,
        output_path: str = 'JUNIOR_GUIDE.md'
    ) -> str:
        """
        Generate a simple guide without triage data.
        
        Args:
            feature_name: Name of the feature
            output_path: Path to save the guide
            
        Returns:
            Path to the generated guide
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = f"""# Junior Developer Guide: {feature_name}

> **Generated:** {timestamp}  
> **Status:** Basic guide (no triage data available)

---

## 📋 Overview

This is a basic guide for understanding **{feature_name}** in the codebase.

To generate a more detailed guide with specific file recommendations:
1. First, run the issue triage: `triage-agent issue <number> --repo owner/repo`
2. Then generate the guide with the triage results

---

## 🗺️ General Navigation Tips

### Understanding the Codebase
1. **Start with the README** - Get an overview of the project
2. **Explore the directory structure** - Run `triage-agent map` to see mission statements
3. **Look for entry points** - Find main.py, app.py, or index files
4. **Check the tests** - Tests often show how code is meant to be used

### Finding Relevant Code
- Use your IDE's search function (Ctrl+Shift+F or Cmd+Shift+F)
- Search for the feature name in comments and docstrings
- Look for related class or function names
- Check git history for recent changes

---

## 💡 Next Steps

Run the triage agent to get specific file recommendations:

```bash
# Analyze a GitHub issue
triage-agent issue 123 --repo owner/repo

# Generate a detailed guide
triage-agent guide "{feature_name}" --with-triage
```

---

*Generated by Developer Triage Agent*
"""
        
        output_file = Path(output_path)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(output_file)

# Made with Bob
