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
        timestamp = datetime.now().strftime("%Y-%m-%d at %H:%M:%S")
        
        content = f"""<div align="center">

# 🎓 Junior Developer Guide
## {feature_name}

![Status](https://img.shields.io/badge/Status-Active-success)
![Generated](https://img.shields.io/badge/Generated-{timestamp.replace(' ', '%20')}-blue)
![Confidence](https://img.shields.io/badge/AI%20Powered-Triage%20Agent-purple)

</div>

---

## 📋 What's Inside This Guide?

Welcome, junior developer! 👋 This guide was automatically generated to help you navigate the codebase for **{feature_name}**.

### 🎯 You'll Find:
- ✅ **Top {len(relevant_files)} most relevant files** for this feature
- ✅ **Mission statements** explaining what each directory does
- ✅ **Code previews** to get you started quickly
- ✅ **Relevance scores** showing how confident we are about each file
- ✅ **Pro tips** from experienced developers

### 🚀 How to Use This Guide:
1. Start with the **highest relevance file** (marked 🟢)
2. Read the **mission statement** to understand the context
3. Review the **code preview** to see what's inside
4. Follow the **navigation tips** at the bottom

---

## 🎯 Key Files to Explore

<details open>
<summary><b>Click to expand/collapse all files</b></summary>

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
            
            # Confidence emoji and badge
            confidence_emoji = {
                'high': '🟢',
                'medium': '🟡',
                'low': '🔴'
            }.get(confidence, '⚪')
            
            confidence_badge = {
                'high': '![High](https://img.shields.io/badge/Confidence-High-success)',
                'medium': '![Medium](https://img.shields.io/badge/Confidence-Medium-yellow)',
                'low': '![Low](https://img.shields.io/badge/Confidence-Low-red)'
            }.get(confidence, '![Unknown](https://img.shields.io/badge/Confidence-Unknown-lightgrey)')
            
            # Priority indicator
            priority = "🔥 START HERE!" if i == 1 else "⭐ High Priority" if i == 2 else "📌 Worth Checking"
            
            content += f"""
### {confidence_emoji} File #{i}: `{file_path}`

<table>
<tr>
<td><b>Relevance Score</b></td>
<td>{relevance:.1%}</td>
<td>{confidence_badge}</td>
</tr>
<tr>
<td><b>Priority</b></td>
<td colspan="2">{priority}</td>
</tr>
</table>

#### 📍 Directory Mission
> {mission}

#### 💡 Why This File Matters
This file scored **{relevance:.1%}** relevance to "{feature_name}". {
    "This is your best starting point! The high relevance score indicates this file is central to the feature." if confidence == 'high'
    else "This file has good relevance and is worth exploring after high-confidence files." if confidence == 'medium'
    else "This file may have tangential relevance. Check it if the other files don't provide enough context."
}

#### 📝 Code Preview
<details>
<summary><b>Click to view code snippet</b></summary>

```{lang}
{snippet}
```

</details>

#### 🎯 What to Look For
- **Function/Class names** - They often describe the purpose
- **Import statements** - Shows dependencies and related modules
- **Comments and docstrings** - Previous developers left helpful hints
- **Variable names** - Follow the data flow through the code

---

"""
        
        # Close the details section
        content += """
</details>

---

## 🗺️ Step-by-Step Navigation Guide

<table>
<tr>
<td width="50px" align="center">1️⃣</td>
<td><b>Start with the Highest Relevance File</b><br/>
Begin with the file marked 🟢 (highest confidence). This is your best entry point into the feature.</td>
</tr>
<tr>
<td width="50px" align="center">2️⃣</td>
<td><b>Read the Directory Mission</b><br/>
Understand the purpose of the directory before diving into code. Context is everything!</td>
</tr>
<tr>
<td width="50px" align="center">3️⃣</td>
<td><b>Scan the Code Preview</b><br/>
Look at imports, function names, and class definitions. Get a feel for what the file does.</td>
</tr>
<tr>
<td width="50px" align="center">4️⃣</td>
<td><b>Follow the Data Flow</b><br/>
Trace how data moves through functions. Look for input → processing → output patterns.</td>
</tr>
<tr>
<td width="50px" align="center">5️⃣</td>
<td><b>Explore Related Files</b><br/>
Check imports and files in the same directory. They often work together.</td>
</tr>
</table>

---

## 🎓 Pro Tips for Junior Developers

### 🔍 Understanding Relevance Scores

| Score | Indicator | What It Means | Action |
|-------|-----------|---------------|--------|
| >70% | 🟢 High | Very likely related to your feature | **Start here!** This is your primary focus |
| 40-70% | 🟡 Medium | Good relevance, worth exploring | Check after high-confidence files |
| <40% | 🔴 Low | Tangential relevance | Explore only if needed for context |

### 📖 Reading Code Like a Pro

<details>
<summary><b>🎯 Click for expert code reading strategies</b></summary>

#### 1. **Top-Down Approach**
```
Start with: File name → Class names → Function names → Implementation
Why: Gives you the big picture before diving into details
```

#### 2. **Follow the Imports**
```python
from auth.login import authenticate_user  # This tells you dependencies!
```
- Imports show you what this file depends on
- They're like a roadmap to related functionality

#### 3. **Read Docstrings First**
```python
def process_payment(amount: float) -> bool:
    \"\"\"
    Process a payment transaction.
    
    Args:
        amount: Payment amount in USD
    
    Returns:
        True if successful, False otherwise
    \"\"\"
```
- Docstrings explain WHAT the code does
- Implementation shows HOW it does it

#### 4. **Trace Variable Transformations**
```python
raw_data → cleaned_data → processed_data → result
```
- Follow how data changes through the code
- Each transformation tells part of the story

</details>

### 🛠️ Essential IDE Shortcuts

<details>
<summary><b>⌨️ Click for productivity shortcuts</b></summary>

| Action | VS Code | PyCharm | What It Does |
|--------|---------|---------|--------------|
| Go to Definition | `F12` | `Ctrl+B` | Jump to where something is defined |
| Find References | `Shift+F12` | `Alt+F7` | See everywhere it's used |
| Search in Files | `Ctrl+Shift+F` | `Ctrl+Shift+F` | Find text across the project |
| Rename Symbol | `F2` | `Shift+F6` | Safely rename variables/functions |
| Show Documentation | `Ctrl+K Ctrl+I` | `Ctrl+Q` | View docstrings inline |

</details>

### 🚨 When You're Stuck

<details>
<summary><b>🆘 Click for troubleshooting strategies</b></summary>

#### Strategy 1: Find the Tests
```bash
# Tests often show how code is meant to be used
find . -name "*test*.py" | grep <feature_name>
```

#### Strategy 2: Search for Keywords
```bash
# Use grep or IDE search to find relevant code
grep -r "authentication" --include="*.py"
```

#### Strategy 3: Check Git History
```bash
# See who worked on this recently
git log --follow <filename>
git blame <filename>  # See who wrote each line
```

#### Strategy 4: Draw a Diagram
```
[User Input] → [Validation] → [Processing] → [Database] → [Response]
```
- Visual representations help understanding
- Map out the data flow on paper

#### Strategy 5: Ask Smart Questions
❌ Bad: "This code doesn't work"
✅ Good: "In `auth/login.py` line 45, the `authenticate_user` function returns None. Based on the docstring, it should return a User object. What am I missing?"

</details>

### 🎯 Quick Wins for Understanding Code

1. **🔖 Add Comments as You Learn**
   ```python
   # I learned: This function validates user input before saving
   def validate_input(data):
       ...
   ```

2. **🧪 Run the Tests**
   ```bash
   pytest tests/test_auth.py -v  # See what's expected to work
   ```

3. **🐛 Use Print Debugging**
   ```python
   print(f"DEBUG: user_id = {user_id}, type = {type(user_id)}")
   ```

4. **📝 Keep a Learning Log**
   ```markdown
   ## What I Learned Today
   - `authenticate_user()` checks password hash, not plain text
   - Session tokens expire after 24 hours
   - User roles are stored in the `roles` table
   ```

---

## 📚 Additional Resources

### 🔧 Tools to Help You

| Tool | Purpose | Command |
|------|---------|---------|
| **Repo Mapper** | See full project structure | `triage-agent map` |
| **Issue Triage** | Find files for specific issues | `triage-agent issue <number>` |
| **Guide Generator** | Create guides like this one | `triage-agent guide "<feature>"` |

### 📖 Learning Resources

- 📘 **Project README**: Start with the main README.md
- 📗 **API Docs**: Check `docs/` directory if it exists
- 📙 **Architecture Docs**: Look for ARCHITECTURE.md or similar
- 📕 **Contributing Guide**: CONTRIBUTING.md has setup instructions

---

## 🚀 Your Action Plan

### Today (30 minutes)
- [ ] Open the #1 file in your IDE
- [ ] Read through the code preview above
- [ ] Identify the main functions/classes
- [ ] Note any questions you have

### This Week
- [ ] Explore all files listed in this guide
- [ ] Run the related tests
- [ ] Make a small, safe change to understand the flow
- [ ] Document what you learned

### Remember
> **"Every expert was once a beginner. The only difference is they didn't give up."**

You've got this! 💪 Start with file #1 and take it one step at a time.

---

<div align="center">

### 🎉 Happy Coding!

*Generated by [Developer Triage Agent](https://github.com/mpagi-shafiq/Project-Atlas)*
*Helping junior developers navigate complex codebases with confidence*

![Made with Love](https://img.shields.io/badge/Made%20with-❤️-red)
![For Juniors](https://img.shields.io/badge/For-Junior%20Developers-blue)
![AI Powered](https://img.shields.io/badge/AI-Powered-purple)

</div>
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
