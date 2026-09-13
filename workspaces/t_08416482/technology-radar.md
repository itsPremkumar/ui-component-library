# Technology Radar

A conceptual technology radar for a typical software company, categorizing tools and techniques into four quadrants. Review cadence: monthly for Trial/Assess, quarterly full refresh with the Architecture Review Board.

---

## Quadrant Legend

| Quadrant | Description | Example Tools |
|----------|-------------|---------------|
| **Adopt** | Proven, widely adopted, low risk | PostgreSQL, Kubernetes, React, Terraform |
| **Trial** | Promising but needs validation | WebAssembly, Tailwind CSS, Bun, Turso |
| **Assess** | Emerging, potential but unproven at scale | Dapr, Tetragon, eBPF-based networking |
| **Hold** | Legacy or problematic; avoid for new work | AngularJS, SOAP-based services, Oracle DB |

---

## Languages

| Technology | Ring | Movement | Rationale |
|------------|------|----------|-----------|
| TypeScript | Adopt | → | Standard for frontend and backend; strong typing; massive ecosystem |
| Python | Adopt | → | Data/ML, scripting, automation; dominant in AI/ML space |
| Go | Adopt | → | Cloud-native services, CLI tools; excellent concurrency model |
| Rust | Trial | ↑ | Systems programming; memory safety without GC; growing adoption |
| Kotlin | Trial | ↑ | JVM alternative; first-class Android; coroutines for async |
| Scala | Hold | ↓ | Declining community; complex type system; limited hiring pool |

---

## Frameworks & Platforms

| Technology | Ring | Movement | Rationale |
|------------|------|----------|-----------|
| React / Next.js | Adopt | → | Dominant frontend framework; SSR/SSG; huge ecosystem |
| Kubernetes | Adopt | → | Industry-standard orchestration; extensive tooling |
| PostgreSQL | Adopt | → | Most capable open-source relational DB; JSON support |
| Terraform | Adopt | → | IaC standard; multi-cloud; state management |
| Spring Boot | Adopt | → | Mature Java ecosystem; strong enterprise adoption |
| Tailwind CSS | Trial | ↑ | Utility-first CSS; rapid UI development; growing adoption |
| Bun | Trial | ↑ | Fast JS runtime; bundler/test runner; early stage |
| Turso | Trial | ↑ | Edge SQLite; libSQL; interesting for distributed edge apps |
| Dapr | Assess | ↑ | Distributed app runtime; portable sidecar pattern |
| Tetragon | Assess | ↑ | Runtime security observability; eBPF-based |
| eBPF networking | Assess | ↑ | Kernel-level networking/observability; steep learning curve |

---

## Data & Storage

| Technology | Ring | Movement | Rationale |
|------------|------|----------|-----------|
| PostgreSQL | Adopt | → | Relational; JSON; extensions; proven at scale |
| Redis | Adopt | → | Caching, sessions, pub/sub; mature ecosystem |
| Elasticsearch | Adopt | → | Full-text search; log analytics; well-understood |
| MongoDB | Trial | ↑ | Document model; flexible schema; good for prototyping |
| ClickHouse | Assess | ↑ | Columnar OLAP; fast analytics queries |
| Oracle DB | Hold | ↓ | Expensive licensing; declining new adoption |

---

## DevOps & Infrastructure

| Technology | Ring | Movement | Rationale |
|------------|------|----------|-----------|
| Docker | Adopt | → | Container standard; universal tooling |
| GitHub Actions | Adopt | → | CI/CD integration; marketplace; generous free tier |
| ArgoCD | Adopt | → | GitOps standard; Kubernetes-native |
| Grafana | Adopt | → | Observability dashboards; rich plugin ecosystem |
| Vault | Adopt | → | Secrets management; PKI; dynamic secrets |
| PagerDuty | Adopt | → | Alert routing; incident management |
| Loki | Trial | ↑ | Log aggregation; Grafana-native; cost-effective |
| Jaeger | Trial | ↑ | Distributed tracing; CNCF project; OpenTelemetry |
| eBPF-based monitoring | Assess | ↑ | Kernel-level observability; low overhead |

---

## Security

| Technology | Ring | Movement | Rationale |
|------------|------|----------|-----------|
| OAuth2 / OIDC | Adopt | → | Standard auth protocol; broad library support |
| HashiCorp Vault | Adopt | → | Secrets management; encryption-as-a-service |
| Let's Encrypt | Adopt | → | Free TLS certificates; automated renewal |
| OWASP ZAP | Trial | ↑ | Security scanning; DAST; CI integration |
| Tetragon | Assess | ↑ | Runtime security; syscall monitoring |
| SOAP-based services | Hold | ↓ | Legacy protocol; XML overhead; limited modern tooling |

---

## Testing

| Technology | Ring | Movement | Rationale |
|------------|------|----------|-----------|
| Jest | Adopt | → | JS/TS testing standard; fast; snapshot support |
| pytest | Adopt | → | Python testing; rich plugin ecosystem |
| Go testing | Adopt | → | Built-in; fast; table-driven tests idiomatic |
| Playwright | Trial | ↑ | E2E testing; cross-browser; reliable selectors |
| k6 | Trial | ↑ | Load testing; scripting in JS; cloud execution |
| Tox | Assess | ↑ | Python env management for tests; multi-version matrix |

---

## Ring Movement Key

- **→** Stable — no significant change
- **↑** Advancing — gaining traction, moving toward Adopt
- **↓** Declining — losing favor, moving toward Hold
- **⚠️** New — recently added, needs evaluation

---

## Update Cadence

| Frequency | Activity |
|-----------|----------|
| **Monthly** | Review Trial and Assess items; add/remove based on team feedback |
| **Quarterly** | Full radar refresh with Architecture Review Board |
| **Ad-hoc** | Emergency review for critical new technology or security concern |

---

## Governance

- All radar entries include: rationale, risks, and a "Try This" first step
- Hold items require written justification and exit criteria
- Trial items must have a 6-week evaluation plan with clear success metrics
- Annual external review of radar against industry benchmarks