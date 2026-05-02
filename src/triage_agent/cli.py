"""
CLI Module - Command-line interface for the Developer Triage Agent.

Provides commands for:
- Mapping repository structure
- Triaging GitHub issues
- Generating onboarding guides
"""

import os
import sys
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich import print as rprint
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .repo_mapper import RepoMapper
from .triage_logic import TriageEngine


console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    Developer Triage Agent - Help junior developers navigate complex repositories.
    
    This tool provides three core capabilities:
    
    1. Repo Mapping: Scan and analyze repository structure
    
    2. Contextual Triage: Map GitHub issues to relevant files
    
    3. Onboarding Guide: Generate documentation for data flows
    """
    pass


@cli.command()
@click.option('--path', '-p', default='.', help='Repository path to scan')
@click.option('--output', '-o', default='repo_map.json', help='Output file path')
@click.option('--max-depth', '-d', default=5, help='Maximum directory depth to scan')
def map(path: str, output: str, max_depth: int):
    """
    Scan repository structure and generate mission statements.
    
    Example:
        triage-agent map --path /path/to/repo --output repo_structure.json
    """
    console.print(Panel.fit(
        "[bold cyan]Repository Mapper[/bold cyan]\n"
        f"Scanning: {path}",
        border_style="cyan"
    ))
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Scanning repository...", total=None)
            
            mapper = RepoMapper(path)
            result = mapper.scan_repository()
            
            progress.update(task, description="Saving results...")
            mapper.save_to_file(output)
            
            progress.update(task, description="Complete!", completed=True)
        
        # Display summary
        summary = result['summary']
        missions = result['missions']
        
        console.print(f"\n[green]✓[/green] Scan complete!")
        console.print(f"[dim]Total directories analyzed:[/dim] {summary['total_directories']}")
        console.print(f"[dim]Output saved to:[/dim] {output}\n")
        
        # Display sample missions
        if missions:
            table = Table(title="Sample Mission Statements", show_header=True, header_style="bold magenta")
            table.add_column("Directory", style="cyan", no_wrap=True)
            table.add_column("Mission Statement", style="white")
            
            for path, mission in list(missions.items())[:5]:
                table.add_row(path or ".", mission)
            
            console.print(table)
            
            if len(missions) > 5:
                console.print(f"\n[dim]... and {len(missions) - 5} more directories[/dim]")
    
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}", style="bold red")
        sys.exit(1)


@cli.command()
@click.argument('issue_number', type=int)
@click.option('--repo', '-r', required=True, help='GitHub repository (owner/repo)')
@click.option('--token', '-t', envvar='GITHUB_TOKEN', help='GitHub personal access token')
@click.option('--path', '-p', default='.', help='Local repository path')
@click.option('--max-files', '-m', default=3, help='Maximum number of files to return')
def issue(issue_number: int, repo: str, token: str, path: str, max_files: int):
    """
    Analyze a GitHub issue and find relevant files.
    
    Example:
        triage-agent issue 123 --repo mpagi-shafiq/Project-Atlas --token YOUR_TOKEN
    
    Or set GITHUB_TOKEN environment variable:
        export GITHUB_TOKEN=your_token
        triage-agent issue 123 --repo mpagi-shafiq/Project-Atlas
    """
    if not token:
        console.print("[red]✗ Error:[/red] GitHub token required. Set GITHUB_TOKEN environment variable or use --token", style="bold red")
        sys.exit(1)
    
    console.print(Panel.fit(
        "[bold cyan]Issue Triage[/bold cyan]\n"
        f"Repository: {repo}\n"
        f"Issue: #{issue_number}",
        border_style="cyan"
    ))
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Fetching issue from GitHub...", total=None)
            
            engine = TriageEngine(path, token)
            
            progress.update(task, description="Analyzing issue...")
            result = engine.triage_issue_by_number(repo, issue_number, max_files)
            
            progress.update(task, description="Complete!", completed=True)
        
        # Display results
        console.print(f"\n[green]✓[/green] Analysis complete!\n")
        
        console.print(f"[bold]Issue:[/bold] #{result['issue_number']} - {result['issue_title']}")
        console.print(f"[dim]Keywords extracted:[/dim] {', '.join(result['keywords'][:5])}\n")
        
        # Display relevant files
        if result['relevant_files']:
            table = Table(title="Top Relevant Files", show_header=True, header_style="bold magenta")
            table.add_column("Rank", style="cyan", width=6)
            table.add_column("File Path", style="white")
            table.add_column("Relevance", style="green", justify="right")
            table.add_column("Confidence", style="yellow")
            
            for i, file_info in enumerate(result['relevant_files'], 1):
                confidence_color = {
                    'high': 'green',
                    'medium': 'yellow',
                    'low': 'red'
                }.get(file_info['confidence'], 'white')
                
                table.add_row(
                    f"#{i}",
                    file_info['path'],
                    f"{file_info['relevance_score']:.1%}",
                    f"[{confidence_color}]{file_info['confidence']}[/{confidence_color}]"
                )
            
            console.print(table)
        else:
            console.print("[yellow]⚠[/yellow] No relevant files found. Try a different issue or check the repository path.")
    
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}", style="bold red")
        sys.exit(1)


@cli.command()
@click.argument('feature_name')
@click.option('--path', '-p', default='.', help='Repository path')
@click.option('--output', '-o', default='JUNIOR_GUIDE.md', help='Output file path')
def guide(feature_name: str, path: str, output: str):
    """
    Generate an onboarding guide for a specific feature.
    
    Example:
        triage-agent guide "API request flow" --path /path/to/repo
    """
    console.print(Panel.fit(
        "[bold cyan]Guide Generator[/bold cyan]\n"
        f"Feature: {feature_name}",
        border_style="cyan"
    ))
    
    console.print("\n[yellow]⚠[/yellow] Guide generation is coming in the next release!")
    console.print("[dim]This feature will trace data flow and generate JUNIOR_GUIDE.md[/dim]\n")
    
    # Placeholder for future implementation
    console.print("[dim]Planned features:[/dim]")
    console.print("  • Trace data flow through the codebase")
    console.print("  • Identify key components and their interactions")
    console.print("  • Generate markdown documentation with diagrams")
    console.print("  • Include code examples and explanations\n")


@cli.command()
def init():
    """
    Initialize configuration for the triage agent.
    
    Creates a config file with default settings.
    """
    console.print(Panel.fit(
        "[bold cyan]Initialize Configuration[/bold cyan]",
        border_style="cyan"
    ))
    
    config_content = """# Developer Triage Agent Configuration

# GitHub Settings
github:
  token: ${GITHUB_TOKEN}  # Set via environment variable
  default_repo: owner/repo

# Repo Mapper Settings
repo_mapper:
  ignore_patterns:
    - .venv
    - __pycache__
    - node_modules
    - .git
  max_depth: 5

# Issue Triage Settings
issue_triage:
  max_files: 3
  relevance_threshold: 0.4
  file_extensions:
    - .py
    - .js
    - .ts
    - .java

# Guide Generator Settings
guide_generator:
  output_file: JUNIOR_GUIDE.md
  template: default
"""
    
    config_path = Path('triage_config.yaml')
    
    if config_path.exists():
        if not click.confirm(f"{config_path} already exists. Overwrite?"):
            console.print("[yellow]Configuration not changed.[/yellow]")
            return
    
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    console.print(f"\n[green]✓[/green] Configuration file created: {config_path}")
    console.print("[dim]Edit this file to customize settings[/dim]\n")


@cli.command()
def interactive():
    """
    Start interactive mode for exploring the repository.
    """
    console.print(Panel.fit(
        "[bold cyan]Interactive Mode[/bold cyan]\n"
        "Coming soon!",
        border_style="cyan"
    ))
    
    console.print("\n[yellow]⚠[/yellow] Interactive mode is coming in the next release!")
    console.print("[dim]This will provide an interactive shell for exploring repositories[/dim]\n")


if __name__ == '__main__':
    cli()

# Made with Bob
