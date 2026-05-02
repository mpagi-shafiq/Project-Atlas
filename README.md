# Developer Triage Agent 🔍

A Python-based tool designed to help junior developers navigate complex repositories with confidence. The Developer Triage Agent provides intelligent analysis and guidance for understanding codebases, triaging issues, and onboarding new team members.

## 🎯 Core Features

### 1. **Repo Mapping** 🗺️
Automatically scan your project structure and generate human-readable "mission statements" for each directory, helping developers understand the purpose and organization of the codebase at a glance.

### 2. **Contextual Triage** 🎯
Input a GitHub issue description, and the agent identifies the top 3 most relevant files using intelligent keyword extraction and relevance ranking. Perfect for quickly locating where to start working on a bug or feature.

### 3. **Onboarding Guide** 📚
Generate a `JUNIOR_GUIDE.md` that explains data flow for specific features (e.g., "How a request moves from API to DB"), making it easier for new developers to understand system architecture.

## 🚀 Installation

This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable Python package management.

### Prerequisites
- Python 3.12 or higher
- uv package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/mpagi-shafiq/Project-Atlas.git
cd Project-Atlas

# Install dependencies with uv
uv sync

# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

## 📖 Usage

### Map Repository Structure

Scan your repository and generate mission statements for each directory:

```bash
python -m triage_agent.cli map --path /path/to/repo --output repo_map.json
```

**Example Output:**
```
✓ Scan complete!
Total directories analyzed: 15

Sample Mission Statements:
┌─────────────┬──────────────────────────────────────────┐
│ Directory   │ Mission Statement                        │
├─────────────┼──────────────────────────────────────────┤
│ src         │ Contains the main source code            │
│ tests       │ Contains unit tests and test fixtures    │
│ docs        │ Contains project documentation           │
└─────────────┴──────────────────────────────────────────┘
```

### Triage GitHub Issues

Analyze a GitHub issue and find the most relevant files:

```bash
# Set your GitHub token
export GITHUB_TOKEN=your_github_token

# Analyze an issue
python -m triage_agent.cli issue 123 --repo mpagi-shafiq/Project-Atlas
```

**Example Output:**
```
✓ Analysis complete!

Issue: #123 - Fix authentication bug in login flow
Keywords extracted: authentication, login, bug, user, session

Top Relevant Files:
┌──────┬─────────────────────────┬───────────┬────────────┐
│ Rank │ File Path               │ Relevance │ Confidence │
├──────┼─────────────────────────┼───────────┼────────────┤
│ #1   │ src/auth/login.py       │ 87.5%     │ high       │
│ #2   │ src/auth/session.py     │ 72.3%     │ high       │
│ #3   │ tests/test_auth.py      │ 65.1%     │ medium     │
└──────┴─────────────────────────┴───────────┴────────────┘
```

### Generate Onboarding Guide

Create documentation explaining data flow for a specific feature:

```bash
python -m triage_agent.cli guide "API request flow" --output JUNIOR_GUIDE.md
```

*Note: Guide generation is coming in the next release!*

### Initialize Configuration

Create a configuration file with default settings:

```bash
python -m triage_agent.cli init
```

This creates `triage_config.yaml` where you can customize:
- Ignore patterns for repo scanning
- Maximum directory depth
- Relevance thresholds
- File extensions to analyze

## 🛠️ Development

### Project Structure

```
my-bob-project/
├── src/
│   └── triage_agent/
│       ├── __init__.py          # Package initialization
│       ├── cli.py               # Command-line interface
│       ├── repo_mapper.py       # Repository scanning logic
│       └── triage_logic.py      # Issue triage and file matching
├── tests/                       # Unit tests (coming soon)
├── .gitignore                   # Git ignore patterns
├── pyproject.toml               # Project dependencies
├── README.md                    # This file
└── IMPLEMENTATION_PLAN.md       # Detailed architecture docs
```

### Running Tests

```bash
# Install test dependencies
uv add --dev pytest pytest-cov

# Run tests
uv run pytest
```

### Code Quality

```bash
# Format code
uv run black src/

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/
```

## 🔧 Configuration

### Environment Variables

- `GITHUB_TOKEN`: Your GitHub personal access token (required for issue triage)

### Configuration File

Create `triage_config.yaml` to customize behavior:

```yaml
github:
  token: ${GITHUB_TOKEN}
  default_repo: owner/repo

repo_mapper:
  ignore_patterns:
    - .venv
    - __pycache__
    - node_modules
  max_depth: 5

issue_triage:
  max_files: 3
  relevance_threshold: 0.4
```

## 📊 How It Works

### Repo Mapping Algorithm

1. **Directory Traversal**: Recursively walks the repository structure
2. **Pattern Analysis**: Examines folder names, file types, and contents
3. **Mission Generation**: Infers purpose based on naming conventions and file patterns
4. **Output**: Generates JSON with structure and mission statements

### Issue Triage Algorithm

1. **Keyword Extraction**: Parses issue title and body for relevant terms
2. **File Scanning**: Searches repository files for keyword matches
3. **Relevance Scoring**: Calculates scores based on:
   - Keyword frequency in file content
   - Filename matches
   - File location relevance
4. **Ranking**: Returns top N files sorted by relevance score

## 🗺️ Roadmap

### Phase 1: Foundation ✅
- [x] Project setup with uv
- [x] Basic CLI interface
- [x] Repo mapping functionality
- [x] Issue triage logic

### Phase 2: Enhancement (In Progress)
- [ ] Guide generator implementation
- [ ] Interactive mode
- [ ] Configuration file support
- [ ] Comprehensive test suite

### Phase 3: Advanced Features
- [ ] AI-powered code analysis
- [ ] Dependency graph visualization
- [ ] Multi-language support
- [ ] VS Code extension

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Mpagi Shafiq**
- GitHub: [@mpagi-shafiq](https://github.com/mpagi-shafiq)
- Repository: [Project-Atlas](https://github.com/mpagi-shafiq/Project-Atlas)

## 🙏 Acknowledgments

- Built with [uv](https://github.com/astral-sh/uv) for fast Python package management
- CLI powered by [Click](https://click.palletsprojects.com/)
- Beautiful terminal output with [Rich](https://rich.readthedocs.io/)
- GitHub integration via [PyGithub](https://pygithub.readthedocs.io/)

## 📞 Support

If you encounter any issues or have questions:
1. Check the [documentation](IMPLEMENTATION_PLAN.md)
2. Search existing [GitHub issues](https://github.com/mpagi-shafiq/Project-Atlas/issues)
3. Create a new issue with detailed information

---

**Status**: Early Development Phase 🚧

This tool is actively being developed. Features and APIs may change. Feedback and contributions are highly appreciated!