# Team Performance Scorecard Template

> **Usage:** Fill in the metrics from your dashboard each sprint or month.
> This template is designed for team-level reflection \u2014 never for
> individual performance evaluations.

---

## Header

| Field              | Value                    |
| ------------------ | ------------------------ |
| Team               | _[team name]_            |
| Period Start       | _YYYY-MM-DD_             |
| Period End         | _YYYY-MM-DD_             |
| Team Size          | _N_                      |
| Sprint Count       | _N_                      |
| Generated          | _YYYY-MM-DD HH:MM_       |

---

## DORA Metrics

| Metric | Value | Unit | Tier | Trend |
| ------ | ----- | ---- | ---- | ----- |
| Deployment Frequency | _/_ | deploys/week | Elite/High/Medium/Low | \u2191/\u2193/\u2192 |
| Lead Time for Changes | _/_ | hours | Elite/High/Medium/Low | \u2191/\u2193/\u2192 |
| Change Failure Rate | _/_ | % | Elite/High/Medium/Low | \u2191/\u2193/\u2192 |
| MTTR | _/_ | minutes | Elite/High/Medium/Low | \u2191/\u2193/\u2192 |

---

## Flow Metrics

| Metric | Value | Unit | Trend |
| ------ | ----- | ---- | ----- |
| Cycle Time (median) | _/_ | hours | \u2191/\u2193/\u2192 |
| Peak WIP | _/_ | PRs | \u2191/\u2193/\u2192 |
| Throughput | _/_ | PRs/week | \u2191/\u2193/\u2192 |

---

## Quality Metrics

| Metric | Value | Target | Status |
| ------ | ----- | ------ | ------ |
| Code Coverage | _/% | >80% | \u2705/\u26a0\ufe0f/\u274c |
| Defect Density | _/KLOC | <1.0 | \u2705/\u26a0\ufe0f/\u274c |
| Review Turnaround | _/hours | <4h | \u2705/\u26a0\ufe0f/\u274c |

---

## Team Health Indicators

| Indicator | Signal | Action Needed? |
| --------- | ------ | -------------- |
| Sprint Goal Achievement | _%_ | Yes/No |
| Burnout Signals | None/Mild/Moderate/Severe | Yes/No |
| Collaboration Index | _X%_ cross-team PRs | Yes/No |
| Survey eNPS | _/_ (aggregated) | Yes/No |

---

## Sprint Narrative

_What went well this period?_

_What was challenging?_

_What will we change next period?_

---

## Action Items

| # | Action | Owner | Due | Status |
| - | ------ | ----- | --- | ------ |
| 1 | _e.g. Add integration tests for payment flow_ | _[name]_ | _YYYY-MM-DD_ | _Open_ |
| 2 | _e.g. Reduce WIP limit from 5 to 3_ | _[name]_ | _YYYY-MM-DD_ | _Open_ |
| 3 | | | | |

---

## Anti-Gamification Checklist

- [ ] Metrics are team-level, never individual
- [ ] No velocity or story-point-per-person targets
- [ ] No LOC-based productivity targets
- [ ] Dashboard is team-visible, not management surveillance
- [ ] Trends shown over snapshots
- [ ] Every metric has a narrative explanation
- [ ] Team agreed on what to measure and why

---

## Review Cycle

| Checkpoint | Frequency | Owner |
| ---------- | --------- | ----- |
| Dashboard review | Weekly | Tech Lead |
| Scorecard retrospective | Monthly | Engineering Manager |
| Metric relevance audit | Quarterly | Tech Lead + EM |
| Survey & health check | Quarterly | EM + HR |

---

*Template version 1.0 \u2014 Adapt this to your team's context. Drop metrics that don't drive improvement.*
