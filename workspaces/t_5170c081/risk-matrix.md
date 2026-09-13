# AI/ML Risk Assessment Matrix Template

> **Purpose:** Structured risk assessment matrix for evaluating AI/ML system categories by likelihood and impact.
> **Usage:** Complete for each AI system during development and before deployment. Update quarterly or after incidents.
> **Scale:** Likelihood 1 (Rare) to 5 (Almost Certain); Impact 1 (Negligible) to 5 (Severe).

---

## 1. Risk Matrix Legend

### Likelihood Scale

| Score | Label | Probability | Description |
|---|---|---|---|
| 1 | Rare | < 5% | Unlikely to occur in normal operations |
| 2 | Unlikely | 5-20% | Could occur but not expected |
| 3 | Possible | 20-50% | May occur under certain conditions |
| 4 | Likely | 50-80% | Expected to occur in most scenarios |
| 5 | Almost Certain | > 80% | Expected to occur frequently |

### Impact Scale

| Score | Label | Severity | Description |
|---|---|---|---|
| 1 | Negligible | Minimal harm | No user harm, minor operational disruption, no regulatory impact |
| 2 | Minor | Limited harm | Small user impact, localized service disruption, minor compliance gap |
| 3 | Moderate | Significant harm | Measurable user harm, regional service degradation, regulatory scrutiny |
| 4 | Major | Severe harm | Significant user harm, widespread outage, regulatory violation, financial loss |
| 5 | Severe | Critical harm | Life/safety impact, systemic failure, major regulatory penalty, reputational crisis |

### Risk Score Matrix

| Likelihood \ Impact | 1 Negligible | 2 Minor | 3 Moderate | 4 Major | 5 Severe |
|---|---|---|---|---|---|
| **5 Almost Certain** | 5 Low | 10 Medium | 15 High | 20 Critical | 25 Critical |
| **4 Likely** | 4 Low | 8 Medium | 12 High | 16 Critical | 20 Critical |
| **3 Possible** | 3 Low | 6 Medium | 9 Medium | 12 High | 15 High |
| **2 Unlikely** | 2 Low | 4 Low | 6 Medium | 8 Medium | 10 Medium |
| **1 Rare** | 1 Low | 2 Low | 3 Low | 4 Low | 5 Low |

### Risk Response Levels

| Score | Level | Required Action | Review Frequency |
|---|---|---|---|
| 1-4 | Low | Accept, monitor | Annually |
| 5-9 | Medium | Mitigate, document | Quarterly |
| 10-16 | High | Mitigate urgently, escalate | Monthly |
| 17-25 | Critical | Do not deploy until mitigated | Weekly / Board |

---

## 2. AI/ML System Category Risk Assessment

Complete the following table for each AI/ML system in production.

### 2.1 System Information

| Field | Value |
|---|---|
| System Name | _[e.g., Credit Scoring v2.3]_ |
| System ID | _[e.g., AI-SYS-001]_ |
| Model Type | _[Classification / Regression / NLP / Computer Vision / Reinforcement Learning / Generative]_ |
| Deployment Environment | _[Production / Staging / Development]_ |
| Data Sensitivity | _[Public / Internal / Confidential / Restricted / Highly Restricted]_ |
| Affected Users | _[Employees / Customers / Public / Vulnerable Populations]_ |
| Jurisdiction(s) | _[EU / US / APAC / Multi-region]_ |
| AI Owner | _[Name + email]_ |
| Last Assessment Date | _[YYYY-MM-DD]_ |
| Next Review Date | _[YYYY-MM-DD]_ |

### 2.2 Risk Register

| Risk ID | Risk Description | Category | Likelihood (1-5) | Impact (1-5) | Score | Mitigation | Residual Score | Owner |
|---|---|---|---|---|---|---|---|---|
| R-001 | Training data contains historical bias | Data Risk | | | | | | |
| R-002 | Model produces discriminatory outcomes | Fairness Risk | | | | | | |
| R-003 | Input data drifts from training distribution | Technical Risk | | | | | | |
| R-004 | Model accuracy degrades over time | Technical Risk | | | | | | |
| R-005 | Adversarial attack manipulates model output | Security Risk | | | | | | |
| R-006 | Training data contains PII/privacy violations | Data Risk | | | | | | |
| R-007 | Model fails silently (no confidence flag) | Operational Risk | | | | | | |
| R-008 | Dependency vulnerability in ML pipeline | Security Risk | | | | | | |
| R-009 | Model update breaks backward compatibility | Operational Risk | | | | | | |
| R-010 | Regulatory non-compliance (AI Act/GDPR) | Compliance Risk | | | | | | |
| R-011 | Model explanation not available for high-stakes decisions | Transparency Risk | | | | | | |
| R-012 | Data pipeline corruption affects model input | Operational Risk | | | | | | |
| R-013 | Model performance insufficient for business needs | Technical Risk | | | | | | |
| R-014 | Unauthorized access to model or training data | Security Risk | | | | | | |
| R-015 | Model used for unintended purpose (scope creep) | Governance Risk | | | | | | |

### 2.3 Top Risks Summary

| Priority | Risk ID | Risk Description | Score | Mitigation Status |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

---

## 3. Risk Assessment by AI System Category

### 3.1 Risk Profiles by Category

| AI Category | Typical Likelihood | Typical Impact | Typical Score | Risk Level | Example Use Cases |
|---|---|---|---|---|---|
| **Content Recommendation** | 3 | 2 | 6 | Medium | News feed, product recs, video suggestions |
| **Credit & Lending** | 3 | 5 | 15 | High | Credit scoring, loan approval, interest rates |
| **Hiring & HR** | 3 | 4 | 12 | High | Resume screening, candidate ranking, performance eval |
| **Medical Diagnosis** | 2 | 5 | 10 | High | Disease detection, treatment recommendation |
| **Autonomous Vehicles** | 3 | 5 | 15 | High | Self-driving, collision avoidance, routing |
| **Law Enforcement** | 3 | 5 | 15 | High | Predictive policing, facial recognition, risk assessment |
| **Generative AI (Chat)** | 4 | 3 | 12 | High | Chatbots, content generation, code assistants |
| **Generative AI (Creative)** | 3 | 2 | 6 | Medium | Image generation, text synthesis, media creation |
| **Fraud Detection** | 3 | 4 | 12 | High | Transaction monitoring, anomaly detection |
| **Predictive Maintenance** | 2 | 3 | 6 | Medium | Equipment failure prediction, scheduling |
| **Customer Sentiment** | 2 | 2 | 4 | Low | NPS prediction, churn modeling, satisfaction |
| **Internal Analytics** | 2 | 2 | 4 | Low | Employee analytics, process optimization |
| **Advertising & Targeting** | 3 | 3 | 9 | Medium | Ad placement, audience segmentation |
| **Financial Trading** | 3 | 5 | 15 | High | Algorithmic trading, portfolio optimization |
| **Education & Assessment** | 2 | 3 | 6 | Medium | Grading, adaptive learning, proctoring |
| **Social Media Moderation** | 3 | 3 | 9 | Medium | Content flagging, toxicity detection |

---

## 4. Mitigation Strategies by Risk Category

### 4.1 Technical Risk Mitigations

| Risk | Mitigation | Verification |
|---|---|---|
| Data drift | Monitor PSI daily, automated retraining pipeline | PSI < 0.25 sustained |
| Concept drift | Track prediction distribution, shadow deployment | Accuracy drop < 5% |
| Model degradation | Regular holdout evaluation, A/B testing | Performance within 2% of baseline |
| Adversarial vulnerability | Adversarial training, robustness testing | Adversarial accuracy > baseline - 5% |
| OOD detection | Confidence thresholding, outlier detection | OOD detection rate > 90% |
| Model coupling | Dependency scanning, container isolation | No critical CVEs |

### 4.2 Data Risk Mitigations

| Risk | Mitigation | Verification |
|---|---|---|
| Training bias | Bias audit, fairness metrics, diverse data | Disparate impact > 0.8 |
| PII leakage | Data anonymization, PII scanning | Zero PII in training data |
| Data quality | Data validation pipelines, schema enforcement | Data quality score > 95% |
| Data staleness | Data freshness monitoring, expiration policies | Data age < retention period |
| Data leakage | Proper train/test split, temporal validation | No leakage in evaluation |

### 4.3 Operational Risk Mitigations

| Risk | Mitigation | Verification |
|---|---|---|
| Pipeline failure | CI/CD with canary deployment, rollback automation | MTTR < 30 min |
| Monitoring gaps | Comprehensive monitoring, alerting on all SLOs | 100% SLO coverage |
| Rollback failure | Regular rollback drills, blue-green deployment | Rollback < 5 min |
| Capacity overload | Load testing, auto-scaling | Handles 2x peak traffic |
| Configuration error | Infrastructure as code, config validation | Zero config drift |

### 4.4 Compliance Risk Mitigations

| Risk | Mitigation | Verification |
|---|---|---|
| Regulatory violation | Regulatory mapping, compliance checklist | All applicable regs covered |
| Audit failure | Immutable audit logs, access controls | Audit trail complete |
| Consent violation | Consent management, opt-out mechanism | 100% consent compliance |
| Documentation gap | Model cards, data sheets, system docs | All artifacts current |
| Cross-border transfer | Data residency controls, transfer impact assessment | Compliant with local laws |

---

## 5. Risk Assessment Workflow

### 5.1 Assessment Process

```
Step 1: IDENTIFY
  → List all risks for the AI system (use risk register template)
  → Include technical, data, operational, compliance, security, reputational risks
  → Engage cross-functional team (ML, security, compliance, domain experts)

Step 2: ANALYZE
  → Score each risk on likelihood (1-5) and impact (1-5)
  → Calculate risk score (likelihood x impact)
  → Use historical incident data and domain expertise for scoring

Step 3: EVALUATE
  → Classify risk level (Low / Medium / High / Critical)
  → Prioritize risks by score
  → Compare against acceptable risk thresholds

Step 4: MITIGATE
  → Define mitigation strategy for each risk
  → Assign owner and deadline for each mitigation
  → Implement technical and procedural controls

Step 5: RESIDUAL ASSESSMENT
  → Re-score risks after mitigation
  → Accept residual risks with AI Review Board approval
  → Document accepted risks with justification

Step 6: MONITOR & REVIEW
  → Track risk indicators continuously
  → Quarterly formal risk review
  → Update assessment after incidents or significant changes
```

### 5.2 Risk Review Triggers

Conduct a risk review when:
- New AI system proposed for deployment
- Model architecture or training data changes significantly
- Deployment environment changes (new region, new user group)
- Incident or near-miss occurs
- Regulatory requirements change
- Quarterly review cycle (every 3 months)
- AI Review Board requests reassessment

---

## 6. Risk Acceptance Criteria

### 6.1 Acceptance Rules

| Risk Level | Acceptance Authority | Conditions |
|---|---|---|
| Low (1-4) | AI Owner | Documented, monitored |
| Medium (5-9) | AI Owner + Engineering Manager | Mitigation plan, quarterly review |
| High (10-16) | AI Review Board | Mitigation in progress, monthly review |
| Critical (17-25) | AI Review Board + CISO + Legal | Do not deploy until mitigated |

### 6.2 Risk Acceptance Template

```
Risk Acceptance Record
======================
Risk ID:           R-XXX
Risk Description:  [description]
Original Score:    [likelihood x impact = score]
Residual Score:    [after mitigation]
Acceptance Authority: [role + name]
Acceptance Date:   [YYYY-MM-DD]
Review Date:       [YYYY-MM-DD]
Justification:     [why residual risk is acceptable]
Monitoring Plan:   [how risk will be tracked]
Escalation Trigger: [conditions that trigger re-assessment]
Signatures:
  - AI Owner: _______________ Date: ___________
  - AI Review Board: ________ Date: ___________
  - Compliance: ___________ Date: ___________
```

---

## 7. Appendix: Risk Scoring Worksheet

### 7.1 Quick Assessment Template

For rapid assessment during sprint planning or design reviews:

| System | Data Sensitivity | User Impact | Regulatory Exposure | Fairness Sensitivity | Overall Score | Risk Level |
|---|---|---|---|---|---|---|
| System A | [1-5] | [1-5] | [1-5] | [1-5] | [sum] | [level] |
| System B | [1-5] | [1-5] | [1-5] | [1-5] | [sum] | [level] |

**Scoring Guide:**
- Data Sensitivity: 1=Public, 2=Internal, 3=Confidential, 4=Restricted, 5=Highly Restricted (PII/PHI)
- User Impact: 1=No impact, 2=Minor inconvenience, 3=Financial/reputational, 4=Significant harm, 5=Life/safety
- Regulatory Exposure: 1=None, 2=Minor, 3=GDPR/HIPAA, 4=Strict regulation, 5=Prohibited use
- Fairness Sensitivity: 1=No protected groups, 2=Low sensitivity, 3=Some groups, 4=High sensitivity, 5=Vulnerable populations

### 7.2 Historical Incident Reference

| Date | System | Incident | Root Cause | Score | Lessons |
|---|---|---|---|---|---|
| | | | | | |

*Maintain this table to calibrate future risk assessments with actual incident data.*

---

*This risk matrix template should be customized for each AI system and reviewed by the AI Review Board. All risk assessments must be documented and retained for audit purposes.*
