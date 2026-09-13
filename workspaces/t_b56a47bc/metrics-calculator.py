#!/usr/bin/env python3
"""Engineering Metrics Calculator — DORA, Flow & Quality Metrics.

Generates simulated engineering data and computes key metrics:
- DORA: Deployment Frequency, Lead Time, Change Failure Rate, MTTR
- Flow: Cycle Time, WIP, Throughput
- Quality: Code Coverage, Defect Density

Usage:
    python metrics-calculator.py [--days N] [--team-size N] [--deploys-per-day N]
    python metrics-calculator.py --output report.md
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class Commit:
    sha: str
    author: str
    timestamp: datetime
    files_changed: int
    lines_added: int
    lines_deleted: int
    message: str


@dataclass
class Deployment:
    id: str
    timestamp: datetime
    status: str  # "success" | "failure"
    commit_sha: str
    environment: str  # "staging" | "production"
    duration_seconds: float


@dataclass
class Incident:
    id: str
    detected_at: datetime
    resolved_at: datetime | None
    severity: str  # "critical" | "high" | "medium" | "low"
    deployment_id: str | None
    description: str


@dataclass
class Issue:
    id: str
    title: str
    created_at: datetime
    resolved_at: datetime | None
    type: str  # "bug" | "feature" | "task" | "tech_debt"
    assignee: str
    sprint: int
    story_points: int


@dataclass
class PR:
    id: int
    title: str
    author: str
    created_at: datetime
    merged_at: datetime | None
    review_comment_at: datetime | None
    files_changed: int
    additions: int
    deletions: int


# ---------------------------------------------------------------------------
# Simulated data generators
# ---------------------------------------------------------------------------

TEAM_NAMES = ["alice", "bob", "charlie", "diana", "evan", "fiona", "george", "hana"]

COMMIT_MESSAGES = [
    "fix: resolve null pointer in user service",
    "feat: add dark mode toggle",
    "refactor: simplify auth middleware",
    "chore: update dependencies",
    "fix: handle edge case in payment flow",
    "feat: implement webhook retries",
    "docs: update API reference",
    "test: add integration tests for checkout",
    "perf: optimise database query",
    "ci: update GitHub Actions workflow",
]

DEPLOYMENT_ENVIRONMENTS = ["staging", "production"]

INCIDENT_DESCRIPTIONS = [
    "Memory leak in API gateway causing 500s",
    "Database connection pool exhaustion",
    "Cache invalidation bug leading to stale data",
    "Third-party API timeout under load",
    "Configuration drift in staging environment",
]


def generate_commits(
    start_date: datetime,
    days: int,
    team_size: int,
) -> list[Commit]:
    """Generate simulated git commits."""
    commits: list[Commit] = []
    end_date = start_date + timedelta(days=days)
    members = TEAM_NAMES[:team_size]
    rng = random.Random(42)

    current = start_date
    while current < end_date:
        # 3-8 commits per day
        num_commits = rng.randint(3, 8)
        for _ in range(num_commits):
            sha = format(rng.getrandbits(28), '07x')
            author = rng.choice(members)
            hour = rng.randint(8, 18)
            minute = rng.randint(0, 59)
            ts = current.replace(hour=hour, minute=minute, second=0)
            files = rng.randint(1, 5)
            adds = rng.randint(10, 500)
            dels = rng.randint(0, adds)
            msg = rng.choice(COMMIT_MESSAGES)
            commits.append(
                Commit(
                    sha=sha,
                    author=author,
                    timestamp=ts,
                    files_changed=files,
                    lines_added=adds,
                    lines_deleted=dels,
                    message=msg,
                )
            )
        current += timedelta(days=1)

    commits.sort(key=lambda c: c.timestamp)
    return commits


def generate_deployments(
    start_date: datetime,
    days: int,
    deploys_per_day: float,
) -> list[Deployment]:
    """Generate simulated CI/CD deployments."""
    deployments: list[Deployment] = []
    end_date = start_date + timedelta(days=days)
    rng = random.Random(123)
    deploy_id = 0

    current = start_date
    while current < end_date:
        # Poisson-ish: number of deploys today
        n = rng.poissonvariate(deploys_per_day) if hasattr(rng, "poissonvariate") else rng.randint(max(1, int(deploys_per_day) - 1), int(deploys_per_day) + 2)
        for _ in range(n):
            deploy_id += 1
            hour = rng.randint(9, 17)
            minute = rng.randint(0, 59)
            ts = current.replace(hour=hour, minute=minute, second=0)
            status = "failure" if rng.random() < 0.08 else "success"  # ~8% failure rate
            env = rng.choice(DEPLOYMENT_ENVIRONMENTS)
            duration = rng.uniform(30, 300)
            deployments.append(
                Deployment(
                    id=f"deploy-{deploy_id:04d}",
                    timestamp=ts,
                    status=status,
                    commit_sha=format(rng.getrandbits(28), '07x'),
                    environment=env,
                    duration_seconds=duration,
                )
            )
        current += timedelta(days=1)

    deployments.sort(key=lambda d: d.timestamp)
    return deployments


def generate_incidents(
    start_date: datetime,
    days: int,
    deployments: list[Deployment],
) -> list[Incident]:
    """Generate incidents correlated with failed deployments."""
    incidents: list[Incident] = []
    rng = random.Random(456)
    failed_deploys = [d for d in deployments if d.status == "failure"]
    end_date = start_date + timedelta(days=days)

    for dep in failed_deploys:
        # 60% of failures trigger an incident
        if rng.random() < 0.6:
            detected = dep.timestamp + timedelta(minutes=rng.randint(5, 120))
            resolve_minutes = rng.randint(15, 480)
            resolved = detected + timedelta(minutes=resolve_minutes)
            if resolved > end_date:
                resolved = end_date
            severity = rng.choice(["critical", "high", "medium", "low"])
            incidents.append(
                Incident(
                    id=f"inc-{len(incidents) + 1:04d}",
                    detected_at=detected,
                    resolved_at=resolved,
                    severity=severity,
                    deployment_id=dep.id,
                    description=rng.choice(INCIDENT_DESCRIPTIONS),
                )
            )
        else:
            # Silent rollback — no incident recorded
            pass

    # Add some random non-deployment incidents
    for _ in range(rng.randint(2, 5)):
        detected = start_date + timedelta(
            days=rng.randint(0, days - 1),
            hours=rng.randint(0, 23),
            minutes=rng.randint(0, 59),
        )
        resolved = detected + timedelta(minutes=rng.randint(30, 600))
        incidents.append(
            Incident(
                id=f"inc-{len(incidents) + 1:04d}",
                detected_at=detected,
                resolved_at=resolved,
                severity=rng.choice(["critical", "high", "medium", "low"]),
                deployment_id=None,
                description=rng.choice(INCIDENT_DESCRIPTIONS),
            )
        )

    incidents.sort(key=lambda i: i.detected_at)
    return incidents


def generate_issues(
    start_date: datetime,
    days: int,
    team_size: int,
) -> list[Issue]:
    """Generate simulated issue tracker entries."""
    issues: list[Issue] = []
    end_date = start_date + timedelta(days=days)
    members = TEAM_NAMES[:team_size]
    rng = random.Random(789)
    issue_id = 0
    sprint = 1

    current = start_date
    while current < end_date:
        # 5-15 issues created per week
        if current.weekday() == 0:  # Monday
            n = rng.randint(5, 15)
            for _ in range(n):
                issue_id += 1
                created = current + timedelta(
                    hours=rng.randint(8, 16), minutes=rng.randint(0, 59)
                )
                # Resolve within 1-10 days
                resolve_days = rng.randint(1, 10)
                resolved = created + timedelta(days=resolve_days)
                itype = rng.choices(
                    ["bug", "feature", "task", "tech_debt"],
                    weights=[0.2, 0.4, 0.25, 0.15],
                    k=1,
                )[0]
                points = {"bug": 3, "feature": 5, "task": 2, "tech_debt": 8}[itype]
                issues.append(
                    Issue(
                        id=f"ISS-{issue_id:04d}",
                        title=f"{itype.replace('_', ' ').title()}: {rng.choice(COMMIT_MESSAGES)}",
                        created_at=created,
                        resolved_at=resolved if resolved < end_date else None,
                        type=itype,
                        assignee=rng.choice(members),
                        sprint=sprint,
                        story_points=points,
                    )
                )
            sprint += 1
        current += timedelta(days=1)

    return issues


def generate_prs(
    commits: list[Commit],
    start_date: datetime,
    days: int,
) -> list[PR]:
    """Generate PRs correlated with commits."""
    prs: list[PR] = []
    rng = random.Random(999)
    members = list(set(c.author for c in commits))

    for i, commit in enumerate(commits):
        # ~70% of commits have a PR
        if rng.random() < 0.7:
            created = commit.timestamp - timedelta(hours=rng.randint(0, 48))
            if created < start_date:
                created = start_date
            # PR merged 1-5 days after creation
            merge_delay = rng.randint(1, 5)
            merged = created + timedelta(days=merge_delay)
            review_delay = rng.randint(0, 120)  # minutes to first review
            review_at = created + timedelta(minutes=review_delay) if rng.random() < 0.9 else None

            prs.append(
                PR(
                    id=i + 1,
                    title=commit.message,
                    author=commit.author,
                    created_at=created,
                    merged_at=merged if rng.random() < 0.85 else None,
                    review_comment_at=review_at,
                    files_changed=commit.files_changed,
                    additions=commit.lines_added,
                    deletions=commit.lines_deleted,
                )
            )

    prs.sort(key=lambda p: p.created_at)
    return prs


# ---------------------------------------------------------------------------
# Metric calculators
# ---------------------------------------------------------------------------


class DORACalculator:
    """Compute DORA metrics from deployments and incidents."""

    def __init__(self, deployments: list[Deployment], incidents: list[Incident], commits: list[Commit]) -> None:
        self.deployments = deployments
        self.incidents = incidents
        self.commits = commits

    def deployment_frequency(self) -> dict[str, Any]:
        """Deployments per week."""
        if not self.deployments:
            return {"value": 0, "unit": "deploys/week", "tier": "N/A"}

        per_week: dict[int, int] = {}
        for d in self.deployments:
            if d.environment != "production":
                continue
            week = d.timestamp.isocalendar()[1]
            per_week[week] = per_week.get(week, 0) + 1

        if not per_week:
            return {"value": 0, "unit": "deploys/week", "tier": "N/A"}

        median = statistics.median(per_week.values())
        # Tier classification
        if median >= 14:
            tier = "Elite"
        elif median >= 7:
            tier = "High"
        elif median >= 1:
            tier = "Medium"
        else:
            tier = "Low"

        return {"value": round(median, 1), "unit": "deploys/week", "tier": tier}

    def lead_time_for_changes(self) -> dict[str, Any]:
        """Median time from commit to production deployment (hours)."""
        prod_deploys = [d for d in self.deployments if d.environment == "production"]
        if not prod_deploys or not self.commits:
            return {"value": None, "unit": "hours", "tier": "N/A"}

        lead_times: list[float] = []
        deploy_shas = {d.commit_sha for d in prod_deploys}
        for commit in self.commits:
            if commit.sha in deploy_shas:
                for dep in prod_deploys:
                    if dep.commit_sha == commit.sha:
                        hours = (dep.timestamp - commit.timestamp).total_seconds() / 3600
                        if hours >= 0:
                            lead_times.append(hours)
                        break

        if not lead_times:
            return {"value": None, "unit": "hours", "tier": "N/A"}

        median = statistics.median(lead_times)
        if median < 1:
            tier = "Elite"
        elif median < 24:
            tier = "High"
        elif median < 168:  # 7 days
            tier = "Medium"
        else:
            tier = "Low"

        return {"value": round(median, 2), "unit": "hours", "tier": tier, "p95": round(sorted(lead_times)[int(len(lead_times) * 0.95)], 2)}

    def change_failure_rate(self) -> dict[str, Any]:
        """Percentage of production deployments that fail."""
        prod_deploys = [d for d in self.deployments if d.environment == "production"]
        if not prod_deploys:
            return {"value": 0, "unit": "%", "tier": "N/A"}

        failed = sum(1 for d in prod_deploys if d.status == "failure")
        rate = (failed / len(prod_deploys)) * 100

        if rate < 5:
            tier = "Elite"
        elif rate < 15:
            tier = "High"
        elif rate < 30:
            tier = "Medium"
        else:
            tier = "Low"

        return {"value": round(rate, 1), "unit": "%", "tier": tier, "failed": failed, "total": len(prod_deploys)}

    def mttr(self) -> dict[str, Any]:
        """Mean Time to Restore from incidents (minutes)."""
        resolved = [i for i in self.incidents if i.resolved_at is not None]
        if not resolved:
            return {"value": None, "unit": "minutes", "tier": "N/A"}

        restore_times = [(i.resolved_at - i.detected_at).total_seconds() / 60 for i in resolved]
        median = statistics.median(restore_times)

        if median < 60:
            tier = "Elite"
        elif median < 1440:  # 24 hours
            tier = "High"
        elif median < 10080:  # 7 days
            tier = "Medium"
        else:
            tier = "Low"

        return {"value": round(median, 1), "unit": "minutes", "tier": tier, "mean": round(statistics.mean(restore_times), 1)}

    def compute_all(self) -> dict[str, Any]:
        return {
            "deployment_frequency": self.deployment_frequency(),
            "lead_time_for_changes": self.lead_time_for_changes(),
            "change_failure_rate": self.change_failure_rate(),
            "mttr": self.mttr(),
        }


class FlowCalculator:
    """Compute flow metrics from PRs and issues."""

    def __init__(self, prs: list[PR], issues: list[Issue]) -> None:
        self.prs = prs
        self.issues = issues

    def cycle_time(self) -> dict[str, Any]:
        """Median time from PR creation to merge (hours)."""
        merged = [p for p in self.prs if p.merged_at is not None]
        if not merged:
            return {"value": None, "unit": "hours", "tier": "N/A"}

        times = [(p.merged_at - p.created_at).total_seconds() / 3600 for p in merged]
        median = statistics.median(times)

        if median < 24:
            tier = "Elite"
        elif median < 72:
            tier = "High"
        elif median < 168:
            tier = "Medium"
        else:
            tier = "Low"

        return {"value": round(median, 1), "unit": "hours", "tier": tier, "p95": round(sorted(times)[int(len(times) * 0.95)], 1)}

    def wip(self) -> dict[str, Any]:
        """Average WIP (open PRs at any point)."""
        if not self.prs:
            return {"value": 0, "unit": "PRs"}

        events = []
        for p in self.prs:
            events.append((p.created_at, 1))  # opened
            if p.merged_at:
                events.append((p.merged_at, -1))  # closed

        events.sort(key=lambda e: e[0])
        current = 0
        max_wip = 0
        for _, delta in events:
            current += delta
            max_wip = max(max_wip, current)

        return {"value": max_wip, "unit": "PRs", "peak": max_wip}

    def throughput(self) -> dict[str, Any]:
        """Merged PRs per week."""
        merged = [p for p in self.prs if p.merged_at is not None]
        if not merged:
            return {"value": 0, "unit": "PRs/week"}

        per_week: dict[int, int] = {}
        for p in merged:
            week = p.merged_at.isocalendar()[1]
            per_week[week] = per_week.get(week, 0) + 1

        median = statistics.median(per_week.values()) if per_week else 0
        return {"value": round(median, 1), "unit": "PRs/week", "total_merged": len(merged)}

    def compute_all(self) -> dict[str, Any]:
        return {
            "cycle_time": self.cycle_time(),
            "wip": self.wip(),
            "throughput": self.throughput(),
        }


class QualityCalculator:
    """Compute quality metrics from commits and issues."""

    def __init__(self, commits: list[Commit], issues: list[Issue], deployments: list[Deployment], prs: list[PR]) -> None:
        self.commits = commits
        self.issues = issues
        self.deployments = deployments
        self.prs = prs

    def code_coverage(self) -> dict[str, Any]:
        """Simulated code coverage (derived from test-related commits)."""
        test_commits = sum(1 for c in self.commits if "test" in c.message.lower())
        total = len(self.commits) if self.commits else 1
        coverage = min(95, (test_commits / total) * 200)  # rough simulation
        return {"value": round(coverage, 1), "unit": "%", "target": 80}

    def defect_density(self) -> dict[str, Any]:
        """Bugs per KLOC equivalent."""
        bugs = sum(1 for i in self.issues if i.type == "bug" and i.resolved_at is not None)
        # Simulated KLOC from commits
        kloc = sum(c.lines_added + c.lines_deleted for c in self.commits) / 1000
        if kloc == 0:
            return {"value": 0, "unit": "bugs/KLOC"}
        density = bugs / kloc
        return {"value": round(density, 2), "unit": "bugs/KLOC", "total_bugs": bugs, "kloc_equiv": round(kloc, 1)}

    def review_turnaround(self) -> dict[str, Any]:
        """Median time from PR creation to first review comment (hours)."""
        reviewed = [p for p in self.prs if p.review_comment_at is not None]
        if not reviewed:
            return {"value": None, "unit": "hours", "tier": "N/A"}

        times = [(p.review_comment_at - p.created_at).total_seconds() / 3600 for p in reviewed]
        median = statistics.median(times)

        return {"value": round(median, 1), "unit": "hours", "target": 4}

    def compute_all(self) -> dict[str, Any]:
        return {
            "code_coverage": self.code_coverage(),
            "defect_density": self.defect_density(),
            "review_turnaround": self.review_turnaround(),
        }


# ---------------------------------------------------------------------------
# Scorecard
# ---------------------------------------------------------------------------


class Scorecard:
    """Aggregates metrics into an actionable Markdown report."""

    def __init__(
        self,
        dora: dict[str, Any],
        flow: dict[str, Any],
        quality: dict[str, Any],
        start_date: datetime,
        days: int,
        team_size: int,
    ) -> None:
        self.dora = dora
        self.flow = flow
        self.quality = quality
        self.start_date = start_date
        self.days = days
        self.team_size = team_size

    def render(self) -> str:
        lines: list[str] = []
        lines.append("# Team Performance Scorecard")
        lines.append("")
        lines.append(f"**Period:** {self.start_date.strftime('%Y-%m-%d')} to {(self.start_date + timedelta(days=self.days)).strftime('%Y-%m-%d')}")
        lines.append(f"**Team size:** {self.team_size}")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

        # DORA section
        lines.append("## DORA Metrics")
        lines.append("")
        for name, label in [
            ("deployment_frequency", "Deployment Frequency"),
            ("lead_time_for_changes", "Lead Time for Changes"),
            ("change_failure_rate", "Change Failure Rate"),
            ("mttr", "Mean Time to Restore"),
        ]:
            m = self.dora[name]
            tier = m.get("tier", "N/A")
            val = m.get("value")
            unit = m.get("unit", "")
            if val is not None:
                lines.append(f"- **{label}:** {val} {unit}  *(Tier: {tier})*")
            else:
                lines.append(f"- **{label}:** N/A")
        lines.append("")

        # Flow section
        lines.append("## Flow Metrics")
        lines.append("")
        for name, label in [
            ("cycle_time", "Cycle Time"),
            ("wip", "Work in Progress"),
            ("throughput", "Throughput"),
        ]:
            m = self.flow[name]
            val = m.get("value")
            unit = m.get("unit", "")
            if val is not None:
                lines.append(f"- **{label}:** {val} {unit}")
            else:
                lines.append(f"- **{label}:** N/A")
        lines.append("")

        # Quality section
        lines.append("## Quality Metrics")
        lines.append("")
        for name, label in [
            ("code_coverage", "Code Coverage"),
            ("defect_density", "Defect Density"),
            ("review_turnaround", "Review Turnaround"),
        ]:
            m = self.quality[name]
            val = m.get("value")
            unit = m.get("unit", "")
            target = m.get("target")
            if val is not None:
                target_str = f" (target: {target})" if target else ""
                lines.append(f"- **{label}:** {val} {unit}{target_str}")
            else:
                lines.append(f"- **{label}:** N/A")
        lines.append("")

        # Summary & Recommendations
        lines.append("## Summary & Recommendations")
        lines.append("")

        # Determine overall health
        dora_tiers = [self.dora[k].get("tier", "N/A") for k in self.dora]
        elite_count = sum(1 for t in dora_tiers if t == "Elite")

        if elite_count >= 3:
            lines.append("Overall health: **Strong** \u2014 your team is performing at Elite/DORA benchmark levels.")
        elif elite_count >= 1:
            lines.append("Overall health: **Good** \u2014 solid performance with room for improvement.")
        else:
            lines.append("Overall health: **Needs Attention** \u2014 consider focused improvement initiatives.")

        lines.append("")
        lines.append("### Recommended Actions")
        lines.append("")

        # Actionable recommendations based on metrics
        if self.dora["change_failure_rate"]["value"] and self.dora["change_failure_rate"]["value"] > 15:
            lines.append("- **Reduce change failure rate:** Improve test coverage and add pre-merge checks.")
        if self.dora["mttr"]["value"] and self.dora["mttr"]["value"] > 60:
            lines.append("- **Improve MTTR:** Invest in better monitoring and rollback procedures.")
        if self.flow["cycle_time"]["value"] and self.flow["cycle_time"]["value"] > 72:
            lines.append("- **Reduce cycle time:** Streamline PR review process and reduce WIP limits.")
        if self.quality["review_turnaround"]["value"] and self.quality["review_turnaround"]["value"] > 4:
            lines.append("- **Faster reviews:** Set SLA for PR reviews (< 4 hours).")
        if self.quality["code_coverage"]["value"] and self.quality["code_coverage"]["value"] < 80:
            lines.append("- **Increase coverage:** Add unit tests for critical paths.")

        lines.append("- **Team health:** Run a retrospection to check for burnout signals.")
        lines.append("- **Share transparently:** Post this scorecard to the team channel.")
        lines.append("")
        lines.append("---")
        lines.append("*This scorecard is a team-level tool. Never use individual metrics for performance evaluations.*")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Engineering Metrics Calculator")
    parser.add_argument("--days", type=int, default=30, help="Simulation period in days (default: 30)")
    parser.add_argument("--team-size", type=int, default=5, help="Team size (default: 5)")
    parser.add_argument("--deploys-per-day", type=float, default=2.0, help="Average deployments per day (default: 2.0)")
    parser.add_argument("--output", type=str, default=None, help="Output file path (default: stdout)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()

    random.seed(args.seed)

    start_date = datetime(2026, 8, 1)

    print(f"Generating simulated data for {args.days} days, team size {args.team_size}...")
    commits = generate_commits(start_date, args.days, args.team_size)
    deployments = generate_deployments(start_date, args.days, args.deploys_per_day)
    incidents = generate_incidents(start_date, args.days, deployments)
    issues = generate_issues(start_date, args.days, args.team_size)
    prs = generate_prs(commits, start_date, args.days)

    print(f"  Commits: {len(commits)}")
    print(f"  Deployments: {len(deployments)}")
    print(f"  Incidents: {len(incidents)}")
    print(f"  Issues: {len(issues)}")
    print(f"  PRs: {len(prs)}")
    print()

    print("Computing metrics...")
    dora = DORACalculator(deployments, incidents, commits).compute_all()
    flow = FlowCalculator(prs, issues).compute_all()
    quality = QualityCalculator(commits, issues, deployments, prs).compute_all()

    scorecard = Scorecard(dora, flow, quality, start_date, args.days, args.team_size)
    report = scorecard.render()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Scorecard written to {args.output}")
    else:
        print(report)

    # Also write raw metrics as JSON for downstream consumption
    json_path = args.output.rsplit(".", 1)[0] + ".json" if args.output else "metrics.json"
    metrics_data = {
        "dora": {k: v for k, v in dora.items()},
        "flow": {k: v for k, v in flow.items()},
        "quality": {k: v for k, v in quality.items()},
        "meta": {"days": args.days, "team_size": args.team_size, "deploys_per_day": args.deploys_per_day},
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2, default=str)
    print(f"Raw metrics written to {json_path}")


if __name__ == "__main__":
    main()
