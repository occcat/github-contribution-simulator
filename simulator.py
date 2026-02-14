#!/usr/bin/env python3
"""
GitHub Contribution Simulator

Generates realistic GitHub commit history with natural patterns:
- More commits on weekdays, fewer on weekends
- Occasional burst days
- Realistic time distributions
- Configurable intensity profiles
"""

import random
import datetime
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from pathlib import Path
import argparse


@dataclass
class Commit:
    """Represents a single commit with timestamp and message."""
    timestamp: datetime.datetime
    message: str
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'message': self.message
        }


class ContributionProfile:
    """Defines commit behavior for different contributor intensities."""
    
    PROFILES = {
        'light': {
            'daily_commit_prob': 0.4,      # 40% chance of any commits on a given day
            'weekend_reduction': 0.3,       # 30% of normal activity on weekends
            'avg_commits_per_day': 1.5,     # Average when active
            'max_commits_per_day': 4,       # Cap for single day
            'burst_probability': 0.05,      # 5% chance of a burst day
            'burst_multiplier': 2.5,        # How much bursts increase commits
            'commit_time_start': 9,         # Earliest commit hour (9 AM)
            'commit_time_end': 18,          # Latest commit hour (6 PM)
        },
        'medium': {
            'daily_commit_prob': 0.7,
            'weekend_reduction': 0.5,
            'avg_commits_per_day': 3,
            'max_commits_per_day': 8,
            'burst_probability': 0.1,
            'burst_multiplier': 2.0,
            'commit_time_start': 8,
            'commit_time_end': 22,
        },
        'heavy': {
            'daily_commit_prob': 0.9,
            'weekend_reduction': 0.7,
            'avg_commits_per_day': 5,
            'max_commits_per_day': 15,
            'burst_probability': 0.15,
            'burst_multiplier': 1.8,
            'commit_time_start': 7,
            'commit_time_end': 23,
        }
    }
    
    def __init__(self, intensity: str = 'medium'):
        if intensity not in self.PROFILES:
            raise ValueError(f"Intensity must be one of: {list(self.PROFILES.keys())}")
        self.config = self.PROFILES[intensity]
        self.intensity = intensity
    
    def get_config(self, key: str):
        return self.config[key]


class CommitMessageGenerator:
    """Generates realistic commit messages."""
    
    PREFIXES = [
        "feat", "fix", "docs", "style", "refactor",
        "test", "chore", "perf", "build", "ci", "wip"
    ]
    
    ACTIONS = [
        "update", "add", "remove", "fix", "implement",
        "refactor", "optimize", "improve", "clean up",
        "rework", "simplify", "enhance", "adjust",
        "tweak", "revise", "modify", "patch"
    ]
    
    OBJECTS = [
        "README", "config", "tests", "utils", "helpers",
        "main module", "API", "docs", "dependencies",
        "deployment", "CI config", "error handling",
        "validation", "logging", "database", "models",
        "routes", "components", "styles", "assets"
    ]
    
    DETAILS = [
        "for better performance", "to handle edge cases",
        "based on feedback", "for compatibility",
        "to fix bug", "as requested", "for clarity",
        "per review comments", "to improve UX",
        "to address security issue", "", "", ""  # Empty for variety
    ]
    
    @classmethod
    def generate(cls) -> str:
        """Generate a random commit message."""
        style = random.random()
        
        if style < 0.4:
            # Conventional commit style: feat: add something
            prefix = random.choice(cls.PREFIXES)
            action = random.choice(cls.ACTIONS)
            obj = random.choice(cls.OBJECTS)
            detail = random.choice(cls.DETAILS)
            if detail:
                return f"{prefix}: {action} {obj} {detail}"
            return f"{prefix}: {action} {obj}"
        
        elif style < 0.7:
            # Simple action: Update something
            action = random.choice(cls.ACTIONS).capitalize()
            obj = random.choice(cls.OBJECTS)
            return f"{action} {obj}"
        
        else:
            # More verbose: Fix issue with component
            action = random.choice(cls.ACTIONS)
            obj = random.choice(cls.OBJECTS)
            detail = random.choice(cls.DETAILS)
            if detail:
                return f"{action} {obj} {detail}"
            return f"{action} {obj}"


class ContributionSimulator:
    """Simulates GitHub contribution patterns over time."""
    
    def __init__(
        self,
        start_date: datetime.date,
        end_date: Optional[datetime.date] = None,
        intensity: str = 'medium',
        seed: Optional[int] = None
    ):
        """
        Initialize the simulator.
        
        Args:
            start_date: First day to generate commits for
            end_date: Last day (defaults to today)
            intensity: 'light', 'medium', or 'heavy'
            seed: Random seed for reproducibility
        """
        self.start_date = start_date
        self.end_date = end_date or datetime.date.today()
        self.profile = ContributionProfile(intensity)
        self.seed = seed
        
        if seed is not None:
            random.seed(seed)
    
    def _should_commit_today(self, date: datetime.date) -> bool:
        """Determine if any commits should happen on this date."""
        base_prob = self.profile.get_config('daily_commit_prob')
        
        # Reduce probability on weekends
        if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            base_prob *= self.profile.get_config('weekend_reduction')
        
        return random.random() < base_prob
    
    def _get_commit_count(self, date: datetime.date) -> int:
        """Determine how many commits for this date."""
        avg = self.profile.get_config('avg_commits_per_day')
        max_commits = self.profile.get_config('max_commits_per_day')
        
        # Add some randomness around the average
        count = max(1, int(random.gauss(avg, avg * 0.5)))
        
        # Check for burst day
        if random.random() < self.profile.get_config('burst_probability'):
            count = int(count * self.profile.get_config('burst_multiplier'))
        
        return min(count, max_commits)
    
    def _generate_commit_times(self, date: datetime.date, count: int) -> List[datetime.datetime]:
        """Generate realistic timestamps for commits on a given day."""
        start_hour = self.profile.get_config('commit_time_start')
        end_hour = self.profile.get_config('commit_time_end')
        
        times = []
        for _ in range(count):
            # Generate hour with bias toward mid-day/work hours
            hour = self._biased_hour(start_hour, end_hour)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            
            dt = datetime.datetime(
                date.year, date.month, date.day,
                hour, minute, second
            )
            times.append(dt)
        
        # Sort chronologically
        times.sort()
        return times
    
    def _biased_hour(self, start: int, end: int) -> int:
        """
        Generate hour with bias toward typical work hours.
        More commits between 10-12 and 14-17.
        """
        # Try a few times to get a work-hour-biased time
        attempts = 0
        while attempts < 10:
            hour = random.randint(start, end)
            
            # Peak hours get bonus probability
            if 10 <= hour <= 12 or 14 <= hour <= 17:
                if random.random() < 0.7:  # 70% chance to accept peak hours
                    return hour
            elif random.random() < 0.4:  # 40% chance for off-peak
                return hour
            
            attempts += 1
        
        return random.randint(start, end)
    
    def generate_day(self, date: datetime.date) -> List[Commit]:
        """Generate all commits for a single day."""
        if not self._should_commit_today(date):
            return []
        
        count = self._get_commit_count(date)
        times = self._generate_commit_times(date, count)
        
        commits = []
        for dt in times:
            message = CommitMessageGenerator.generate()
            commits.append(Commit(timestamp=dt, message=message))
        
        return commits
    
    def simulate(self) -> List[Commit]:
        """
        Run the full simulation from start to end date.
        
        Returns:
            List of Commit objects in chronological order
        """
        all_commits = []
        current_date = self.start_date
        
        while current_date <= self.end_date:
            day_commits = self.generate_day(current_date)
            all_commits.extend(day_commits)
            current_date += datetime.timedelta(days=1)
        
        return all_commits
    
    def get_stats(self, commits: List[Commit]) -> Dict:
        """Calculate statistics about generated commits."""
        if not commits:
            return {}
        
        by_date = {}
        by_weekday = {i: 0 for i in range(7)}
        by_hour = {i: 0 for i in range(24)}
        
        for commit in commits:
            date_key = commit.timestamp.date()
            by_date[date_key] = by_date.get(date_key, 0) + 1
            by_weekday[commit.timestamp.weekday()] += 1
            by_hour[commit.timestamp.hour] += 1
        
        daily_counts = list(by_date.values())
        
        return {
            'total_commits': len(commits),
            'active_days': len(by_date),
            'avg_commits_per_active_day': len(commits) / len(by_date) if by_date else 0,
            'max_commits_in_day': max(daily_counts) if daily_counts else 0,
            'by_weekday': {
                'Mon': by_weekday[0], 'Tue': by_weekday[1], 'Wed': by_weekday[2],
                'Thu': by_weekday[3], 'Fri': by_weekday[4], 'Sat': by_weekday[5], 'Sun': by_weekday[6]
            },
            'by_hour': by_hour
        }


def export_to_json(commits: List[Commit], filepath: str):
    """Export commits to JSON format."""
    data = {
        'commits': [c.to_dict() for c in commits],
        'total': len(commits)
    }
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description='Simulate GitHub contribution history',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --start 2020-01-01 --intensity medium
  %(prog)s --start 2022-06-01 --end 2023-06-01 --intensity heavy --seed 42
  %(prog)s --start 2021-01-01 --export commits.json
        """
    )
    
    parser.add_argument('--start', '-s', required=True,
                        help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', '-e',
                        help='End date (YYYY-MM-DD, defaults to today)')
    parser.add_argument('--intensity', '-i', choices=['light', 'medium', 'heavy'],
                        default='medium',
                        help='Contribution intensity level (default: medium)')
    parser.add_argument('--seed', type=int,
                        help='Random seed for reproducible results')
    parser.add_argument('--export', '-o',
                        help='Export commits to JSON file')
    parser.add_argument('--stats-only', action='store_true',
                        help='Only show statistics, no commit list')
    
    args = parser.parse_args()
    
    # Parse dates
    start_date = datetime.datetime.strptime(args.start, '%Y-%m-%d').date()
    end_date = None
    if args.end:
        end_date = datetime.datetime.strptime(args.end, '%Y-%m-%d').date()
    
    # Run simulation
    simulator = ContributionSimulator(
        start_date=start_date,
        end_date=end_date,
        intensity=args.intensity,
        seed=args.seed
    )
    
    print(f"🎯 Simulating {args.intensity} contributor from {start_date} to {simulator.end_date}...")
    commits = simulator.simulate()
    
    # Show stats
    stats = simulator.get_stats(commits)
    print(f"\n📊 Statistics:")
    print(f"   Total commits: {stats['total_commits']}")
    print(f"   Active days: {stats['active_days']}")
    print(f"   Avg commits per active day: {stats['avg_commits_per_active_day']:.1f}")
    print(f"   Max commits in a day: {stats['max_commits_in_day']}")
    print(f"\n📅 Commits by weekday:")
    for day, count in stats['by_weekday'].items():
        bar = '█' * int(count / max(stats['by_weekday'].values()) * 30) if max(stats['by_weekday'].values()) > 0 else ''
        print(f"   {day}: {count:4d} {bar}")
    
    if not args.stats_only:
        print(f"\n📝 First 10 commits:")
        for commit in commits[:10]:
            print(f"   {commit.timestamp.strftime('%Y-%m-%d %H:%M')} - {commit.message}")
        
        if len(commits) > 10:
            print(f"   ... and {len(commits) - 10} more")
    
    # Export if requested
    if args.export:
        export_to_json(commits, args.export)
        print(f"\n💾 Exported to {args.export}")


if __name__ == '__main__':
    main()
