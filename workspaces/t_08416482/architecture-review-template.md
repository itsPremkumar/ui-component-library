# Architecture Review Template

A reusable, structured template for conducting technical architecture reviews in an engineering organization. Adapt the checklist to the context — this is a framework, not a rigid form.

---

## Review Metadata

| Field | Value |
|-------|-------|
| **Review ID** | AR-YYYY-NNN |
| **Date** | |
| **Author / Proposer** | |
| **Reviewer(s)** | |
| **System / Service** | |
| **Review Type** | New Design / Major Refactor / Security Change / Cross-Team Dependency |
| **Decision Required** | Approve / Conditional / Reject / Defer |

---

## 1. System Overview

- [ ] System context diagram included (C4 Level 1-2)
- [ ] Scope and boundaries clearly defined
- [ ] Non-functional requirements documented (latency, throughput, availability)
- [ ] User stories / use cases driving the design

## 2. Data Architecture

- [ ] Data flow diagram provided
- [ ] Storage strategy justified (SQL / NoSQL / Polyglot)
- [ ] Data retention and GDPR/privacy compliance addressed
- [ ] Backup and recovery plan in place (RPO / RTO defined)
- [ ] Data migration strategy (if applicable)

## 3. API Design

- [ ] API contracts defined (OpenAPI / GraphQL schema / gRPC proto)
- [ ] Versioning strategy documented
- [ ] Error handling and retry logic specified
- [ ] Rate limiting and auth model defined
- [ ] Backward compatibility plan for changes

## 4. Security

- [ ] Threat model completed (STRIDE or PASTA)
- [ ] Authentication / authorization design (OAuth2 / OIDC / API keys)
- [ ] Data encryption at rest and in transit
- [ ] Secrets management approach
- [ ] Input validation and injection attack mitigation

## 5. Scalability & Performance

- [ ] Load estimates provided (peak / average)
- [ ] Horizontal scaling strategy documented
- [ ] Caching strategy (what, where, TTL, invalidation)
- [ ] Performance benchmarks / targets defined
- [ ] Database indexing and query optimization plan

## 6. Observability

- [ ] Logging format and aggregation plan (structured logging, correlation IDs)
- [ ] Metrics and alerting thresholds defined
- [ ] Distributed tracing strategy
- [ ] Runbook for on-call (common failure scenarios)
- [ ] Error budget and SLA/SLO targets

## 7. Operational Readiness

- [ ] Deployment strategy (blue/green / canary / rolling)
- [ ] Rollback plan documented and tested
- [ ] Configuration management (env vars / config files / secrets)
- [ ] Disaster recovery test scheduled
- [ ] Cost estimate (infra + licensing + operational)

## 8. Team & Process

- [ ] On-call rotation defined
- [ ] Documentation plan (runbooks, architecture docs)
- [ ] Test strategy (unit / integration / e2e / chaos)
- [ ] CI/CD pipeline coverage
- [ ] Knowledge transfer plan for critical components

---

## Review Outcome

| Outcome | Action |
|---------|--------|
| **Approved** | Proceed to implementation |
| **Conditional** | Address feedback within 1 sprint; re-review required |
| **Rejected** | Document rationale; reconsider in 3 months with updated info |
| **Deferred** | Schedule follow-up review with specific criteria |

### Feedback Summary

| # | Area | Feedback | Owner | Due |
|---|------|----------|-------|-----|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

### Sign-Off

| Role | Name | Decision | Date |
|------|------|----------|------|
| Author | | | |
| Reviewer | | | |
| ARB Chair | | | |

---

## Notes

*Add any additional context, open questions, or follow-up items here.*