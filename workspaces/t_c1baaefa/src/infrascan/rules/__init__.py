"""Extensible rule engine for security, compliance, and cost checks."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Optional

import yaml

from infrascan.schemas import Finding, Resource, Severity


class Rule(ABC):
    """Base class for all rules."""

    def __init__(
        self,
        rule_id: str,
        title: str,
        description: str,
        severity: Severity,
        category: str = "security",
        remediation: str = "",
        references: Optional[list[str]] = None,
        enabled: bool = True,
    ):
        self.rule_id = rule_id
        self.title = title
        self.description = description
        self.severity = severity
        self.category = category
        self.remediation = remediation
        self.references = references or []
        self.enabled = enabled

    @abstractmethod
    def check(self, resource: Resource) -> Optional[Finding]:
        """Check a resource against this rule. Returns Finding if violated."""
        ...

    def applies_to(self, resource: Resource) -> bool:
        """Check if this rule applies to the given resource type."""
        return True


class PropertyRule(Rule):
    """Rule that checks resource properties."""

    def __init__(
        self,
        rule_id: str,
        title: str,
        description: str,
        severity: Severity,
        resource_types: list[str],
        property_name: str,
        expected_value: Any = None,
        forbidden_value: Any = None,
        required: bool = False,
        check_func: Optional[Callable[[Any], bool]] = None,
        category: str = "security",
        remediation: str = "",
        references: Optional[list[str]] = None,
    ):
        super().__init__(rule_id, title, description, severity, category, remediation, references)
        self.resource_types = resource_types
        self.property_name = property_name
        self.expected_value = expected_value
        self.forbidden_value = forbidden_value
        self.required = required
        self.check_func = check_func

    def applies_to(self, resource: Resource) -> bool:
        return any(rt in resource.resource_type for rt in self.resource_types)

    def check(self, resource: Resource) -> Optional[Finding]:
        if not self.applies_to(resource):
            return None

        props = resource.properties
        value = props.get(self.property_name)

        if self.required and value is None:
            return self._make_finding(resource, f"Required property '{self.property_name}' is missing")

        if value is None:
            return None

        if self.forbidden_value is not None and value == self.forbidden_value:
            return self._make_finding(
                resource,
                f"Property '{self.property_name}' has forbidden value: {value}"
            )

        if self.expected_value is not None and value != self.expected_value:
            return self._make_finding(
                resource,
                f"Property '{self.property_name}' expected '{self.expected_value}' but got '{value}'"
            )

        if self.check_func is not None and not self.check_func(value):
            return self._make_finding(
                resource,
                f"Property '{self.property_name}' failed validation check"
            )

        return None

    def _make_finding(self, resource: Resource, detail: str) -> Finding:
        return Finding(
            rule_id=self.rule_id,
            title=self.title,
            description=f"{self.description}\nDetail: {detail}",
            severity=self.severity,
            resource=resource,
            file_path=resource.source_file,
            line_number=resource.line_start,
            remediation=self.remediation,
            references=self.references,
            category=self.category,
        )


class TagRule(Rule):
    """Rule that checks for required tags on resources."""

    def __init__(
        self,
        rule_id: str,
        title: str,
        description: str,
        severity: Severity,
        required_tags: list[str],
        resource_types: Optional[list[str]] = None,
        remediation: str = "",
        references: Optional[list[str]] = None,
    ):
        super().__init__(rule_id, title, description, severity, "compliance", remediation, references)
        self.required_tags = required_tags
        self.resource_types = resource_types

    def applies_to(self, resource: Resource) -> bool:
        if self.resource_types is None:
            return True
        return any(rt in resource.resource_type for rt in self.resource_types)

    def check(self, resource: Resource) -> Optional[Finding]:
        if not self.applies_to(resource):
            return None

        tags = resource.properties.get("tags", {})
        if isinstance(tags, str):
            tags = {}
        elif not isinstance(tags, dict):
            tags = {}

        missing = [tag for tag in self.required_tags if tag not in tags]
        if missing:
            return Finding(
                rule_id=self.rule_id,
                title=self.title,
                description=f"{self.description}\nMissing tags: {', '.join(missing)}",
                severity=self.severity,
                resource=resource,
                file_path=resource.source_file,
                line_number=resource.line_start,
                remediation=self.remediation,
                references=self.references,
                category=self.category,
            )
        return None


class RuleEngine:
    """Engine that manages and executes rules."""

    def __init__(self):
        self._rules: list[Rule] = []

    def register(self, rule: Rule) -> None:
        """Register a rule."""
        if rule.enabled:
            self._rules.append(rule)

    def load_builtin_rules(self) -> None:
        """Load all built-in security, compliance, and cost rules."""
        self._load_security_rules()
        self._load_compliance_rules()
        self._load_cost_rules()

    def _load_security_rules(self) -> None:
        """Load built-in security rules."""
        security_rules = [
            PropertyRule(
                rule_id="SEC001",
                title="S3 Bucket Public Access Enabled",
                description="S3 bucket has public access enabled which may expose sensitive data",
                severity=Severity.CRITICAL,
                resource_types=["aws_s3_bucket"],
                property_name="acl",
                forbidden_value="public-read",
                remediation="Set acl to 'private' or remove the acl property",
                references=["https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html"],
            ),
            PropertyRule(
                rule_id="SEC002",
                title="S3 Bucket Public Read Write Access",
                description="S3 bucket has public read-write access enabled",
                severity=Severity.CRITICAL,
                resource_types=["aws_s3_bucket"],
                property_name="acl",
                forbidden_value="public-read-write",
                remediation="Set acl to 'private'",
            ),
            PropertyRule(
                rule_id="SEC003",
                title="Security Group Allows All Inbound Traffic",
                description="Security group allows inbound traffic from 0.0.0.0/0",
                severity=Severity.HIGH,
                resource_types=["aws_security_group", "aws_security_group_rule"],
                property_name="cidr_blocks",
                check_func=lambda v: "0.0.0.0/0" in str(v),
                remediation="Restrict CIDR blocks to specific IP ranges",
                references=["https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html"],
            ),
            PropertyRule(
                rule_id="SEC004",
                title="Unencrypted EBS Volume",
                description="EBS volume does not have encryption enabled",
                severity=Severity.HIGH,
                resource_types=["aws_ebs_volume"],
                property_name="encrypted",
                expected_value="true",
                remediation="Set encrypted = true",
            ),
            PropertyRule(
                rule_id="SEC005",
                title="IAM Policy with Full Admin Access",
                description="IAM policy grants full administrative access",
                severity=Severity.CRITICAL,
                resource_types=["aws_iam_policy", "aws_iam_role_policy", "aws_iam_user_policy"],
                property_name="policy",
                check_func=lambda v: '"Action": "*"' in str(v),
                remediation="Apply least-privilege principle - restrict actions and resources",
                references=["https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html"],
            ),
            PropertyRule(
                rule_id="SEC006",
                title="RDS Instance Publicly Accessible",
                description="RDS database instance is publicly accessible",
                severity=Severity.HIGH,
                resource_types=["aws_db_instance"],
                property_name="publicly_accessible",
                forbidden_value="true",
                remediation="Set publicly_accessible = false",
            ),
            PropertyRule(
                rule_id="SEC007",
                title="Unencrypted SQS Queue",
                description="SQS queue does not have server-side encryption enabled",
                severity=Severity.MEDIUM,
                resource_types=["aws_sqs_queue"],
                property_name="kms_master_key_id",
                required=True,
                remediation="Configure KMS key for SQS encryption",
            ),
            PropertyRule(
                rule_id="SEC008",
                title="S3 Bucket Versioning Disabled",
                description="S3 bucket does not have versioning enabled",
                severity=Severity.MEDIUM,
                resource_types=["aws_s3_bucket"],
                property_name="versioning",
                check_func=lambda v: "enabled" in str(v).lower() or "true" in str(v).lower(),
                remediation="Enable versioning for data protection",
            ),
            PropertyRule(
                rule_id="SEC009",
                title="CloudTrail Logging Disabled",
                description="CloudTrail logging is not enabled for the account",
                severity=Severity.HIGH,
                resource_types=["aws_cloudtrail"],
                property_name="enable_logging",
                forbidden_value="false",
                remediation="Enable CloudTrail logging",
            ),
            PropertyRule(
                rule_id="SEC010",
                title="Weak SSL/TLS Policy",
                description="Load balancer uses a deprecated SSL policy",
                severity=Severity.MEDIUM,
                resource_types=["aws_lb_listener", "aws_elb"],
                property_name="ssl_policy",
                check_func=lambda v: "ELBSecurityPolicy-TLS-1-0" in str(v) or "ELBSecurityPolicy-2016-08" in str(v),
                remediation="Use ELBSecurityPolicy-TLS13-1-2-2021-06 or newer",
            ),
        ]
        for rule in security_rules:
            self.register(rule)

    def _load_compliance_rules(self) -> None:
        """Load built-in compliance rules."""
        compliance_rules = [
            TagRule(
                rule_id="COMP001",
                title="Missing Required Tags - Environment",
                description="Resource is missing the required 'Environment' tag",
                severity=Severity.MEDIUM,
                required_tags=["Environment"],
                remediation="Add Environment tag (e.g., dev, staging, production)",
            ),
            TagRule(
                rule_id="COMP002",
                title="Missing Required Tags - Owner",
                description="Resource is missing the required 'Owner' tag",
                severity=Severity.LOW,
                required_tags=["Owner"],
                remediation="Add Owner tag to identify resource owner",
            ),
            TagRule(
                rule_id="COMP003",
                title="Missing Cost Center Tag",
                description="Resource is missing the required 'CostCenter' tag for chargeback",
                severity=Severity.LOW,
                required_tags=["CostCenter"],
                remediation="Add CostCenter tag for cost allocation",
            ),
            PropertyRule(
                rule_id="COMP004",
                title="Resource Naming Convention Violation",
                description="Resource name does not follow naming convention",
                severity=Severity.LOW,
                resource_types=["aws_"],
                property_name="name",
                check_func=lambda v: any(env in str(v).lower() for env in ["dev-", "staging-", "prod-", "test-"]),
                remediation="Prefix resource names with environment (e.g., prod-, dev-)",
                category="compliance",
            ),
        ]
        for rule in compliance_rules:
            self.register(rule)

    def _load_cost_rules(self) -> None:
        """Load built-in cost optimization rules."""
        cost_rules = [
            PropertyRule(
                rule_id="COST001",
                title="Oversized EC2 Instance",
                description="EC2 instance type is larger than necessary",
                severity=Severity.MEDIUM,
                resource_types=["aws_instance"],
                property_name="instance_type",
                check_func=lambda v: any(size in str(v) for size in [".2xlarge", ".4xlarge", ".8xlarge", ".12xlarge", ".16xlarge", ".24xlarge"]),
                remediation="Consider using smaller instance types or reserved instances",
                category="cost",
            ),
            PropertyRule(
                rule_id="COST002",
                title="RDS Multi-AZ in Non-Production",
                description="RDS instance has Multi-AZ enabled in a non-production environment",
                severity=Severity.LOW,
                resource_types=["aws_db_instance"],
                property_name="multi_az",
                expected_value="false",
                remediation="Disable Multi-AZ for non-production databases",
                category="cost",
            ),
            PropertyRule(
                rule_id="COST003",
                title="Unattached EBS Volume",
                description="EBS volume is defined but may not be attached to any instance",
                severity=Severity.LOW,
                resource_types=["aws_ebs_volume"],
                property_name="availability_zone",
                required=True,
                remediation="Remove unused EBS volumes or ensure they are attached",
                category="cost",
            ),
            PropertyRule(
                rule_id="COST004",
                title="NAT Gateway in Development",
                description="NAT Gateway is expensive and may not be needed in development",
                severity=Severity.MEDIUM,
                resource_types=["aws_nat_gateway"],
                property_name="tags",
                check_func=lambda v: "Environment" in str(v) and "dev" in str(v).lower(),
                remediation="Consider using NAT instances or VPC endpoints for dev environments",
                category="cost",
            ),
            PropertyRule(
                rule_id="COST005",
                title="S3 Intelligent Tiering Not Enabled",
                description="S3 bucket does not use Intelligent Tiering for cost optimization",
                severity=Severity.LOW,
                resource_types=["aws_s3_bucket"],
                property_name="lifecycle_rule",
                required=True,
                remediation="Enable S3 Intelligent Tiering lifecycle rules",
                category="cost",
            ),
        ]
        for rule in cost_rules:
            self.register(rule)

    def load_custom_rules(self, rules_file: Path) -> None:
        """Load custom rules from a YAML file."""
        if not rules_file.exists():
            return
        content = yaml.safe_load(rules_file.read_text(encoding="utf-8"))
        if not content or "rules" not in content:
            return

        for rule_def in content["rules"]:
            rule_type = rule_def.get("type", "property")
            if rule_type == "property":
                rule = PropertyRule(
                    rule_id=rule_def["id"],
                    title=rule_def["title"],
                    description=rule_def["description"],
                    severity=Severity(rule_def.get("severity", "medium")),
                    resource_types=rule_def.get("resource_types", []),
                    property_name=rule_def.get("property_name", ""),
                    expected_value=rule_def.get("expected_value"),
                    forbidden_value=rule_def.get("forbidden_value"),
                    required=rule_def.get("required", False),
                    category=rule_def.get("category", "security"),
                    remediation=rule_def.get("remediation", ""),
                    references=rule_def.get("references", []),
                )
                self.register(rule)
            elif rule_type == "tag":
                rule = TagRule(
                    rule_id=rule_def["id"],
                    title=rule_def["title"],
                    description=rule_def["description"],
                    severity=Severity(rule_def.get("severity", "medium")),
                    required_tags=rule_def.get("required_tags", []),
                    resource_types=rule_def.get("resource_types"),
                    remediation=rule_def.get("remediation", ""),
                    references=rule_def.get("references", []),
                )
                self.register(rule)

    def scan(self, resources: list[Resource]) -> list[Finding]:
        """Run all rules against a list of resources."""
        findings: list[Finding] = []
        for resource in resources:
            for rule in self._rules:
                try:
                    finding = rule.check(resource)
                    if finding is not None:
                        findings.append(finding)
                except Exception:
                    continue
        return findings

    @property
    def rule_count(self) -> int:
        return len(self._rules)
