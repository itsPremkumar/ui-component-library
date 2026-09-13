# AI Governance Self-Assessment Checklist

> **Purpose:** Actionable checklist for engineering teams to self-assess AI system governance readiness before deployment.
> **Usage:** Complete this checklist during model development and before production deployment. Score each item and track remediation.

---

## Pre-Deployment Governance Checklist

### 1. Model Documentation (Score: /20)

| # | Item | Required | Status | Notes |
|---|---|---|---|---|
| 1.1 | Model card created with purpose, architecture, training data summary | Yes | [ ] | |
| 1.2 | Data sheet completed for all training datasets | Yes | [ ] | |
| 1.3 | Model version documented (version, commit hash, build ID) | Yes | [ ] | |
| 1.4 | Training data provenance documented (source, collection date, size) | Yes | [ ] | |
| 1.5 | Known limitations and edge cases documented | Yes | [ ] | |
| 1.6 | Intended use cases and out-of-scope uses clearly stated | Yes | [ ] | |
| 1.7 | Model performance metrics documented (accuracy, precision, recall, F1, AUC) | Yes | [ ] | |
| 1.8 | Fairness metrics documented across protected groups | Yes | [ ] | |
| 1.9 | Model explainability method selected and documented | Yes | [ ] | SHAP, LIME, attention, etc. |
| 1.10 | Model card reviewed and signed off by AI Owner | Yes | [ ] | |

### 2. Data Governance (Score: /20)

| # | Item | Required | Status | Notes |
|---|---|---|---|---|
| 2.1 | Data collection consent verified for all training data | Yes | [ ] | |
| 2.2 | PII/PHI scan completed — no unauthorized personal data | Yes | [ ] | |
| 2.3 | Data retention policy applied to training data | Yes | [ ] | |
| 2.4 | Data bias analysis completed and documented | Yes | [ ] | |
| 2.5 | Train/validation/test split documented and reproducible | Yes | [ ] | |
| 2.6 | Data augmentation techniques documented (if any) | Yes | [ ] | |
| 2.7 | Data versioning in place (DVC, LakeFS, or equivalent) | Yes | [ ] | |
| 2.8 | Data access controls enforced (role-based, encryption) | Yes | [ ] | |
| 2.9 | Data lineage tracked from source to model input | Yes | [ ] | |
| 2.10 | Privacy Impact Assessment (PIA) completed if PII involved | Yes | [ ] | |

### 3. Fairness & Bias (Score: /20)

| # | Item | Required | Status | Notes |
|---|---|---|---|---|
| 3.1 | Protected attribute inventory completed | Yes | [ ] | |
| 3.2 | Disparate impact ratio calculated (>0.8 threshold) | Yes | [ ] | |
| 3.3 | Equalized odds test passed across groups | Yes | [ ] | |
| 3.4 | Calibration test passed across groups | Yes | [ ] | |
| 3.5 | Bias mitigation strategy applied (pre/in/post-processing) | Yes | [ ] | |
| 3.6 | Counterfactual fairness tests completed | Yes | [ ] | |
| 3.7 | Fairness metrics tracked in monitoring dashboard | Yes | [ ] | |
| 3.8 | Fairness thresholds defined and documented | Yes | [ ] | |
| 3.9 | Bias audit report reviewed by AI Review Board | Yes | [ ] | |
| 3.10 | Remediation plan in place if any fairness threshold failed | Yes | [ ] | |

### 4. Model Performance & Robustness (Score: /15)

| # | Item | Required | Status | Notes |
|---|---|---|---|---|
| 4.1 | Model evaluated on holdout test set with documented metrics | Yes | [ ] | |
| 4.2 | Cross-validation results documented | Yes | [ ] | |
| 4.3 | Adversarial robustness testing completed | Yes | [ ] | |
| 4.4 | Out-of-distribution detection mechanism in place | Yes | [ ] | |
| 4.5 | Confidence calibration evaluated (ECE score) | Yes | [ ] | |
| 4.6 | Ablation studies documented for key features | Yes | [ ] | |
| 4.7 | Model latency and throughput benchmarks documented | Yes | [ ] | |
| 4.8 | Model size and resource requirements documented | Yes | [ ] | |
| 4.9 | Error analysis completed — failure modes documented | Yes | [ ] | |
| 4.10 | Model passes all unit, integration, and e2e tests | Yes | [ ] | |

### 5. Deployment & Operations (Score: /15)

| # | Item | Required | Status | Notes |
|---|---|---|---|---|
| 5.1 | Deployment plan documented (blue-green, canary, rolling) | Yes | [ ] | |
| 5.2 | Rollback plan documented and tested | Yes | [ ] | |
| 5.3 | CI/CD pipeline includes model validation gates | Yes | [ ] | |
| 5.4 | Monitoring and alerting configured for data drift | Yes | [ ] | |
| 5.5 | Monitoring and alerting configured for concept drift | Yes | [ ] | |
| 5.6 | Monitoring and alerting configured for performance drift | Yes | [ ] | |
| 5.7 | Prediction logging enabled (input, output, timestamp, request ID) | Yes | [ ] | |
| 5.8 | Model serving endpoint secured (auth, rate limiting, TLS) | Yes | [ ] | |
| 5.9 | Shadow deployment completed for new model versions | Yes | [ ] | |
| 5.10 | Load testing completed under expected traffic patterns | Yes | [ ] | |

### 6. Compliance & Audit (Score: /10)

| # | Item | Required | Status | Notes |
|---|---|---|---|---|
| 6.1 | Risk assessment completed using risk-matrix.md template | Yes | [ ] | |
| 6.2 | Regulatory requirements identified for use case/jurisdiction | Yes | [ ] | |
| 6.3 | AI system risk classification assigned (Minimal/Limited/High/Unacceptable) | Yes | [ ] | |
| 6.4 | Conformity assessment documentation prepared | Yes | [ ] | |
| 6.5 | Audit trail logging enabled for all model events | Yes | [ ] | |
| 6.6 | Access controls configured for model and data | Yes | [ ] | |
| 6.7 | Third-party model licenses and attributions verified | Yes | [ ] | |
| 6.8 | Incident response playbook reviewed and updated | Yes | [ ] | |
| 6.9 | AI Review Board approval obtained for high-risk models | Yes | [ ] | |
| 6.10 | Compliance sign-off obtained before deployment | Yes | [ ] | |

### 7. Incident Response & Communication (Score: /10)

| # | Item | Required | Status | Notes |
|---|---|---|---|---|
| 7.1 | Incident response contact list current | Yes | [ ] | |
| 7.2 | Model monitoring dashboard accessible to AI Owner | Yes | [ ] | |
| 7.3 | Alert channels configured (PagerDuty, Slack, email) | Yes | [ ] | |
| 7.4 | Rollback procedure tested in staging environment | Yes | [ ] | |
| 7.5 | Communication plan for model incidents drafted | Yes | [ ] | |
| 7.6 | User notification template prepared for automated decisions | Yes | [ ] | |
| 7.7 | Data breach response plan includes AI-specific procedures | Yes | [ ] | |
| 7.8 | Post-incident review process defined | Yes | [ ] | |
| 7.9 | Stakeholder communication plan documented | Yes | [ ] | |
| 7.10 | External regulatory notification contacts identified | Conditional | [ ] | Required for high-risk systems |

---

## Scoring Summary

| Section | Max Score | Your Score | % |
|---|---|---|---|
| 1. Model Documentation | 20 | /20 | |
| 2. Data Governance | 20 | /20 | |
| 3. Fairness & Bias | 20 | /20 | |
| 4. Model Performance | 15 | /15 | |
| 5. Deployment & Operations | 15 | /15 | |
| 6. Compliance & Audit | 10 | /10 | |
| 7. Incident Response | 10 | /10 | |
| **TOTAL** | **110** | **/110** | |

### Deployment Readiness

| Score Range | Status | Action Required |
|---|---|---|
| 100-110 | **Ready for Deployment** | AI Review Board sign-off |
| 85-99 | **Conditional** | Remediate flagged items before deployment |
| 70-84 | **Not Ready** | Significant gaps — remediate and re-assess |
| < 70 | **Not Ready** | Fundamental gaps — do not deploy |

---

## Sign-Off

| Role | Name | Signature | Date |
|---|---|---|---|
| AI Owner | | | |
| ML Engineer | | | |
| AI Review Board | | | |
| Compliance Officer | | | |
| Security Engineer | | | |

---

*This checklist must be completed and signed off before any high-risk AI system is deployed to production. Completed checklists must be retained for audit purposes (minimum 3 years).*
