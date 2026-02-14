#!/usr/bin/env python3
"""
GitHub Contribution Simulator - Commit Generator

This script generates actual Git commits with backdated timestamps
to create a realistic GitHub contribution graph.

Usage:
    python generate_commits.py --start 2020-01-01 --repo ./my-project
    python generate_commits.py --start 2020-01-01 --intensity heavy --auto-push
"""

import os
import sys
import json
import argparse
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta


# Import from simulator module
from simulator import ContributionSimulator, CommitMessageGenerator


def run_git_command(repo_path: str, *args, check: bool = True) -> subprocess.CompletedProcess:
    """Run a git command in the specified repository."""
    env = os.environ.copy()
    env['GIT_AUTHOR_DATE'] = ''
    env['GIT_COMMITTER_DATE'] = ''
    
    result = subprocess.run(
        ['git'] + list(args),
        cwd=repo_path,
        capture_output=True,
        text=True,
        env=env
    )
    
    if check and result.returncode != 0:
        raise RuntimeError(f"Git command failed: {' '.join(args)}\n{result.stderr}")
    
    return result


def setup_repository(repo_path: str, remote_url: str = None) -> str:
    """
    Setup or verify a git repository.
    
    Args:
        repo_path: Path to repository (will be created if doesn't exist)
        remote_url: Optional remote URL to set
        
    Returns:
        Path to the repository
    """
    repo = Path(repo_path)
    
    if not repo.exists():
        print(f"📁 Creating new directory: {repo}")
        repo.mkdir(parents=True)
    
    git_dir = repo / '.git'
    
    if not git_dir.exists():
        print(f"🔧 Initializing git repository...")
        run_git_command(str(repo), 'init')
        run_git_command(str(repo), 'config', 'user.name', 'GitHub Simulator')
        run_git_command(str(repo), 'config', 'user.email', 'simulator@example.com')
        
        # Create initial commit
        readme = repo / 'README.md'
        readme.write_text('# GitHub Contribution Simulator\n\nGenerated with github-contribution-simulator\n')
        run_git_command(str(repo), 'add', 'README.md')
        run_git_command(str(repo), 'commit', '-m', 'Initial commit')
        print(f"✅ Repository initialized")
    else:
        print(f"📦 Using existing repository: {repo}")
    
    if remote_url:
        # Check if remote exists
        result = run_git_command(str(repo), 'remote', 'get-url', 'origin', check=False)
        if result.returncode != 0:
            print(f"🔗 Adding remote: {remote_url}")
            run_git_command(str(repo), 'remote', 'add', 'origin', remote_url)
        else:
            print(f"🔗 Remote already configured: {result.stdout.strip()}")
    
    return str(repo)


def generate_content_file(repo_path: str, commit_num: int) -> str:
    """Generate a content file for a commit."""
    content_dir = Path(repo_path) / 'content'
    content_dir.mkdir(exist_ok=True)
    
    filename = f"contribution_{commit_num:05d}.txt"
    filepath = content_dir / filename
    
    # Generate meaningful-looking content
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    content = f"""Contribution Entry #{commit_num}
Generated: {timestamp}
Message: Auto-generated contribution file

This file is part of the contribution simulation.
"""
    
    filepath.write_text(content)
    
    # Return path relative to repo root
    return str(filepath.relative_to(repo_path))


def create_commit(repo_path: str, timestamp: datetime, message: str, commit_num: int):
    """
    Create a single git commit with a specific timestamp.
    
    Args:
        repo_path: Path to git repository
        timestamp: Commit timestamp (author and committer date)
        message: Commit message
        commit_num: Commit number for content generation
    """
    # Generate a file to commit (returns relative path)
    rel_filepath = generate_content_file(repo_path, commit_num)
    
    # Format the date for git
    date_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    
    # Set environment variables for backdating
    env = os.environ.copy()
    env['GIT_AUTHOR_DATE'] = date_str
    env['GIT_COMMITTER_DATE'] = date_str
    
    # Add and commit
    subprocess.run(
        ['git', 'add', rel_filepath],
        cwd=repo_path,
        check=True
    )
    
    subprocess.run(
        ['git', 'commit', '-m', message],
        cwd=repo_path,
        env=env,
        check=True,
        capture_output=True
    )


def generate_contributions(
    repo_path: str,
    start_date: datetime,
    end_date: datetime = None,
    intensity: str = 'medium',
    seed: int = None,
    dry_run: bool = False
) -> int:
    """
    Generate git commits for the specified date range.
    
    Args:
        repo_path: Path to git repository
        start_date: Start date for commits
        end_date: End date (defaults to today)
        intensity: 'light', 'medium', or 'heavy'
        seed: Random seed for reproducibility
        dry_run: If True, only simulate without creating commits
        
    Returns:
        Number of commits created
    """
    from datetime import date as date_type
    
    start = start_date.date() if isinstance(start_date, datetime) else start_date
    end = end_date.date() if isinstance(end_date, datetime) else end_date or date_type.today()
    
    print(f"🎯 Configuration:")
    print(f"   Repository: {repo_path}")
    print(f"   Date range: {start} to {end}")
    print(f"   Intensity: {intensity}")
    print(f"   Mode: {'DRY RUN (no commits will be made)' if dry_run else 'LIVE'}")
    print()
    
    # Generate commit schedule
    simulator = ContributionSimulator(
        start_date=start,
        end_date=end,
        intensity=intensity,
        seed=seed
    )
    
    print("📊 Simulating contribution pattern...")
    commits = simulator.simulate()
    
    stats = simulator.get_stats(commits)
    print(f"   Total commits to generate: {stats['total_commits']}")
    print(f"   Active days: {stats['active_days']}")
    print(f"   Average per active day: {stats['avg_commits_per_active_day']:.1f}")
    print()
    
    if dry_run:
        print("📝 Sample commits (dry run):")
        for commit in commits[:5]:
            print(f"   {commit.timestamp.strftime('%Y-%m-%d %H:%M')} - {commit.message}")
        if len(commits) > 5:
            print(f"   ... and {len(commits) - 5} more")
        return len(commits)
    
    # Create actual commits
    print("🔨 Creating commits...")
    
    for i, commit in enumerate(commits, 1):
        try:
            create_commit(repo_path, commit.timestamp, commit.message, i)
            
            # Progress indicator
            if i % 50 == 0 or i == len(commits):
                print(f"   Progress: {i}/{len(commits)} commits created")
                
        except Exception as e:
            print(f"   ⚠️  Error on commit {i}: {e}")
            continue
    
    print()
    print(f"✅ Complete! Created {len(commits)} commits.")
    
    return len(commits)


def main():
    parser = argparse.ArgumentParser(
        description='Generate git commits with backdated timestamps',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create new repo and fill with commits from 2020
  %(prog)s --start 2020-01-01 --repo ./my-project
  
  # Use existing repo with heavy intensity
  %(prog)s --start 2021-06-01 --repo ./existing-project --intensity heavy
  
  # Dry run to see what would be created
  %(prog)s --start 2022-01-01 --end 2022-12-31 --dry-run
  
  # With remote and auto-push
  %(prog)s --start 2020-01-01 --repo ./project --remote https://github.com/user/repo.git --push
        """
    )
    
    parser.add_argument('--start', '-s', required=True,
                        help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', '-e',
                        help='End date (YYYY-MM-DD, defaults to today)')
    parser.add_argument('--repo', '-r', default='./contribution-repo',
                        help='Repository path (default: ./contribution-repo)')
    parser.add_argument('--remote', '-R',
                        help='Remote URL to add (e.g., https://github.com/user/repo.git)')
    parser.add_argument('--intensity', '-i', choices=['light', 'medium', 'heavy'],
                        default='medium',
                        help='Contribution intensity (default: medium)')
    parser.add_argument('--seed', type=int,
                        help='Random seed for reproducible results')
    parser.add_argument('--dry-run', '-n', action='store_true',
                        help='Simulate without creating commits')
    parser.add_argument('--push', '-p', action='store_true',
                        help='Push to remote after creating commits')
    parser.add_argument('--force', '-f', action='store_true',
                        help='Force push (use with caution!)')
    
    args = parser.parse_args()
    
    # Parse dates
    start_date = datetime.strptime(args.start, '%Y-%m-%d')
    end_date = None
    if args.end:
        end_date = datetime.strptime(args.end, '%Y-%m-%d')
    
    # Setup repository
    if not args.dry_run:
        repo_path = setup_repository(args.repo, args.remote)
    else:
        repo_path = args.repo
    
    # Generate commits
    count = generate_contributions(
        repo_path=repo_path,
        start_date=start_date,
        end_date=end_date,
        intensity=args.intensity,
        seed=args.seed,
        dry_run=args.dry_run
    )
    
    # Push if requested
    if args.push and not args.dry_run:
        print()
        print("📤 Pushing to remote...")
        try:
            branch = run_git_command(repo_path, 'branch', '--show-current').stdout.strip()
            push_args = ['push', '-u', 'origin', branch]
            if args.force:
                push_args.insert(1, '--force')
            
            result = run_git_command(repo_path, *push_args, check=False)
            if result.returncode == 0:
                print("✅ Pushed successfully!")
            else:
                print(f"⚠️  Push failed: {result.stderr}")
                print("   You may need to push manually:")
                print(f"   cd {repo_path} && git push -u origin {branch}")
        except Exception as e:
            print(f"⚠️  Push error: {e}")


if __name__ == '__main__':
    main()
