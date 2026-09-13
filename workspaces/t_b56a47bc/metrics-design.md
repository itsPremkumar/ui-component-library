# Engineering Metrics System — Design Document

## Purpose

A practical engineering metrics system for Technical Leads and Engineering
Managers to measure, track, and improve team performance. This design covers
DORA metrics, flow metrics, quality metrics, team health indicators, and
guidance on presenting metrics without gamification or harmful incentives.

---

## 1. DORA Metrics (Core)

DORA (DevOps Research and Assessment) identifies four key metrics that
strongly correlate with organizational performance.

### 1.1 Deployment Frequency (DF)

- **Definition:** How often code is deployed to production.
- **Measurement:** Count of deployments to production per unit time (day/week).
- **Benchmark tiers:**
  - Elite: multiple deploys/day
  - High: once/day
  - Medium: once/week
  - Low: once/month or less
- **Data sources:** CI/CD pipeline logs, deployment manifests, release notes.

### 1.2 Lead Time for Changes (LT)

- **Definition:** Time from commit to production deployment.
- **Measurement:** Median time (in hours/days) from `git commit` to successful
  production deployment.
- **Benchmark tiers:**
  - Elite: < 1 hour
  - High: < 1 day
  - Medium: < 1 week
  - Low: > 1 month
- **Data sources:** Git timestamps, CI/CD pipeline start/end times.

### 1.3 Change Failure Rate (CFR)

- **Definition:** Percentage of deployments causing a failure in production
  requiring remediation (rollback, hotfix).
- **Measurement:** Failed deployments / total deployments * 100.
- **Benchmark tiers:**
  - Elite: < 5%
  - High: 5–15%
  - Medium: 15–30%
  - Low: > 30%
- **Data sources:** Incident reports, rollback logs, CI/CD status.

### 1.4 Mean Time to Restore (MTTR)

- **Definition:** Time to restore service after a production failure.
- **Measurement:** Median time (in minutes/hours) from detection to restored
  service.
- **Benchmark tiers:**
  - Elite: < 1 hour
  - High: < 1 day
  - Medium: < 1 week
  - Low: > 1 week
- **Data sources:** Incident management systems, CI/CD rollback timestamps.

---

## 2. Flow Metrics (Lean / Flow Framework)

### 2.1 Cycle Time

- **Definition:** Time from work start to completion (commit to merge/deploy).
- **Measurement:** Median cycle time per team, per sprint.
- **Use:** Identifies bottlenecks in the delivery pipeline.

### 2.2 Work in Progress (WIP)

- **Definition:** Number of items actively being worked on at any given time.
- **Measurement:** Count of open PRs, in-progress tickets.
- **Use:** High WIP signals context-switching overhead and reduced throughput.

### 2.3 Throughput

- **Definition:** Number of items completed per unit time.
- **Measurement:** Closed tickets / merged PRs per sprint or week.
- **Use:** Tracks team capacity and predicts delivery dates.

---

## 3. Quality Metrics

### 3.1 Code Coverage

- Unit test coverage percentage (target: > 80%).
- Measured via `pytest-cov`, `nyc`, `jacoco`.

### 3.2 Defect Density

- Bugs per KLOC (thousand lines of code) per release.
- Tracked from issue tracker labels (`bug`, `regression`).

### 3.3 Escalation Rate

- Percentage of issues requiring L2/L3 support or management escalation.
- Signals quality gaps in earlier stages.

### 3.4 Review Turnaround

- Median time from PR open to first review comment.
- Target: < 4 hours.

---

## 4. Team Health Indicators

### 4.1 Sprint Goal Achievement Rate

- % of sprints where all committed goals were met.
- Sustained > 70% is healthy; < 50% signals overcommitment.

### 4.2 Burnout Signals

- PR review latency spikes (reviewer is slow).
- Increased context-switching (many small PRs, frequent reassignments).
- Weekend commits (indirect signal — review sensitively).

### 4.3 Collaboration Index

- Cross-team PR reviews / total PRs.
- Knowledge sharing via PR comments and documentation updates.

### 4.4 Satisfaction & Engagement

- Anonymous quarterly survey (eNPS, psychological safety).
- NOT tracked per individual — aggregated only.

---

## 5. Anti-Gamification & Healthy Incentives

### Principles

1. **Measure systems, not individuals.** Metrics describe the process, not
   the person. Never tie individual performance reviews to DORA metrics.
2. **Avoid velocity tracking.** Story points per developer invites gaming.
3. **No code-volume targets.** Lines of code (LOC) incentivise bloat.
4. **Publish transparently.** Dashboards are for the team, not for
   management surveillance.
5. **Context over targets.** A spike in cycle time needs investigation,
   not blame. Ask "what blocked us?" not "who was slow?"
6. **Review the metrics themselves.** If a metric isn't driving improvement,
   drop it.

### Presentation Guidelines

- Show trends over time, not single snapshots.
- Always include the benchmark range for comparison.
- Pair every metric with a narrative: "What does this mean for us?"
- Celebrate improvements, investigate regressions — never punish.

---

## 6. Data Sources & Collection

| Metric              | Source                          | Tool / Method                         |
| ------------------- | ------------------------------- | ------------------------------------- |
| Deployment Frequency| CI/CD pipeline logs             | GitHub Actions, GitLab CI, Jenkins    |
| Lead Time           | Git + CI timestamps             | GitHub API, custom scripts            |
| Change Failure Rate | Incident + deployment logs      | PagerDuty, incident reports           |
| MTTR                | Incident management system      | Incident timeline analysis            |
| Cycle Time          | Issue tracker + PR events       | Jira, Linear, GitHub Issues           |
| WIP / Throughput    | Issue tracker                   | Jira board state, API queries         |
| Code Coverage       | Test runner output              | pytest-cov, codecov                   |
| Defect Density        | Issue tracker                   | Label filtering                       |
| Review Turnaround   | PR events                       | GitHub PR API                         |
| Team Health         | Surveys + observational         | Anonymous forms, 1:1 retros           |

---

## 7. Dashboard Layout

```
┌──────────────────────────────────────────────────────┐
│  Engineering Metrics Dashboard                        │
├──────────────┬──────────────┬────────────────────────┤
│  DORA        │  Flow        │  Quality               │
│  ─ DF        │  ─ Cycle Time│  ─ Code Coverage       │
│  ─ LT        │  ─ WIP       │  ─ Defect Density      │
│  ─ CFR       │  ─ Throughput│  ─ Review Turnaround   │
│  ─ MTTR      │              │                        │
├──────────────┴──────────────┴────────────────────────┤
│  Team Health                                          │
│  ─ Sprint Goal Achievement │ ─ Collaboration Index   │
│  ─ Burnout Signals         │ ─ eNPS (aggregated)     │
└──────────────────────────────────────────────────────┘
```

---

## 8. Python Calculator Architecture

The `metrics-calculator.py` script provides:

1. **Simulated data generation** — realistic git commits, CI/CD logs,
   issue tracker entries.
2. **Metric computation** — all DORA, flow, quality metrics with
   statistical summaries (median, p95, trends).
3. **Scorecard output** — aggregated report in Markdown.

### Script Structure

```
metrics-calculator.py
├── DataGenerators
│   ├── GitCommitGenerator      — simulated commits with timestamps
│   ├── CICDPipelineGenerator    — deployment logs with success/failure
│   └── IssueTrackerGenerator    — tickets with creation/resolve times
├── MetricCalculators
│   ├── DORACalculator           — DF, LT, CFR, MTTR
│   ├── FlowCalculator           — cycle time, WIP, throughput
│   └── QualityCalculator        — coverage, defect density
├── Scorecard                    — aggregates into Markdown report
└── main()                       — orchestrates generation → calculation → report
```

---

## 9. Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run with defaults (30-day simulated dataset)
python metrics-calculator.py

# Customise simulation parameters
python metrics-calculator.py --days 90 --team-size 5 --deploys-per-day 3

# Output to specific file
python metrics-calculator.py --output report.md
```

---

## 10. Version History

| Date       | Version | Changes                        |
| ---------- | ------- | ------------------------------ |
| 2026-09-13 | 1.0.0   | Initial design document        |
