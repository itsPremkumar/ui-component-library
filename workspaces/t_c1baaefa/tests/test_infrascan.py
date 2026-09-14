"""Tests for InfraScan."""

import json
import tempfile
from pathlib import Path

import pytest

from infrascan.schemas import Finding, Resource, ScanResult, Severity, ResourceType
from infrascan.parsers import ParserRegistry, TerraformParser, CloudFormationParser
from infrascan.rules import RuleEngine, PropertyRule, TagRule
from infrascan.cost import CostEstimator
from infrascan.reports import JsonReportGenerator, MarkdownReportGenerator, HtmlReportGenerator


# --- Schemas Tests ---

class TestSeverity:
    def test_severity_values(self):
        assert Severity.CRITICAL.value == "critical"
        assert Severity.HIGH.value == "high"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.LOW.value == "low"
        assert Severity.INFO.value == "info"


class TestResource:
    def test_resource_creation(self):
        r = Resource(
            name="my_bucket",
            resource_type="aws_s3_bucket",
            source_file="main.tf",
            line_start=1,
            line_end=10,
            properties={"acl": "private"},
            iac_type=ResourceType.TERRAFORM,
        )
        assert r.name == "my_bucket"
        assert r.resource_type == "aws_s3_bucket"


class TestFinding:
    def test_finding_to_dict(self):
        f = Finding(
            rule_id="SEC001",
            title="Test Finding",
            description="A test finding",
            severity=Severity.HIGH,
            file_path="main.tf",
            line_number=5,
        )
        d = f.to_dict()
        assert d["rule_id"] == "SEC001"
        assert d["severity"] == "high"


class TestScanResult:
    def test_empty_result(self):
        result = ScanResult()
        assert result.critical_count == 0

    def test_counts(self):
        result = ScanResult(findings=[
            Finding(rule_id="1", title="a", description="", severity=Severity.CRITICAL),
            Finding(rule_id="2", title="b", description="", severity=Severity.HIGH),
            Finding(rule_id="3", title="c", description="", severity=Severity.HIGH),
            Finding(rule_id="4", title="d", description="", severity=Severity.LOW),
        ])
        assert result.critical_count == 1
        assert result.high_count == 2
        assert result.low_count == 1

    def test_by_category(self):
        result = ScanResult(findings=[
            Finding(rule_id="1", title="a", description="", severity=Severity.HIGH, category="security"),
            Finding(rule_id="2", title="b", description="", severity=Severity.LOW, category="cost"),
        ])
        assert len(result.by_category("security")) == 1
        assert len(result.by_category("cost")) == 1

    def test_to_dict(self):
        result = ScanResult(findings=[
            Finding(rule_id="1", title="a", description="", severity=Severity.CRITICAL),
        ])
        d = result.to_dict()
        assert d["summary"]["total_findings"] == 1
        assert d["summary"]["critical"] == 1


# --- Parser Tests ---

class TestTerraformParser:
    def test_detect_tf_file(self):
        parser = TerraformParser()
        assert parser.detect(Path("main.tf"))
        assert not parser.detect(Path("template.yaml"))

    def test_parse_simple_resource(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
            f.write('resource "aws_s3_bucket" "my_bucket" {\n  acl = "private"\n}\n')
            f.flush()
            parser = TerraformParser()
            resources = parser.parse(Path(f.name))
            assert len(resources) == 1
            assert resources[0].name == "my_bucket"
            assert resources[0].resource_type == "aws_s3_bucket"
            assert resources[0].properties["acl"] == "private"

    def test_parse_multiple_resources(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
            f.write(
                'resource "aws_s3_bucket" "bucket1" {\n  acl = "private"\n}\n'
                'resource "aws_instance" "web" {\n  instance_type = "t3.micro"\n}\n'
            )
            f.flush()
            parser = TerraformParser()
            resources = parser.parse(Path(f.name))
            assert len(resources) == 2

    def test_parse_public_acl(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
            f.write('resource "aws_s3_bucket" "bad" {\n  acl = "public-read"\n}\n')
            f.flush()
            parser = TerraformParser()
            resources = parser.parse(Path(f.name))
            assert resources[0].properties["acl"] == "public-read"


class TestCloudFormationParser:
    def test_detect_yaml_with_resources(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("Resources:\n  MyBucket:\n    Type: AWS::S3::Bucket\n")
            f.flush()
            parser = CloudFormationParser()
            assert parser.detect(Path(f.name))

    def test_detect_non_cfn(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("foo: bar\n")
            f.flush()
            parser = CloudFormationParser()
            assert not parser.detect(Path(f.name))

    def test_parse_yaml_template(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                "Resources:\n"
                "  MyBucket:\n"
                "    Type: AWS::S3::Bucket\n"
                "    Properties:\n"
                "      BucketName: my-bucket\n"
            )
            f.flush()
            parser = CloudFormationParser()
            resources = parser.parse(Path(f.name))
            assert len(resources) == 1
            assert resources[0].name == "MyBucket"


class TestParserRegistry:
    def test_get_parser_for_tf(self):
        registry = ParserRegistry()
        parser = registry.get_parser(Path("main.tf"))
        assert isinstance(parser, TerraformParser)

    def test_scan_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "main.tf").write_text(
                'resource "aws_s3_bucket" "test" {\n  acl = "private"\n}\n'
            )
            registry = ParserRegistry()
            resources = registry.scan_directory(Path(tmpdir))
            assert len(resources) >= 1


# --- Rules Tests ---

class TestPropertyRule:
    def test_forbidden_value_triggers(self):
        rule = PropertyRule(
            rule_id="TEST001",
            title="Test",
            description="Test rule",
            severity=Severity.HIGH,
            resource_types=["aws_s3_bucket"],
            property_name="acl",
            forbidden_value="public-read",
        )
        resource = Resource(
            name="my_bucket",
            resource_type="aws_s3_bucket",
            source_file="main.tf",
            properties={"acl": "public-read"},
        )
        finding = rule.check(resource)
        assert finding is not None
        assert finding.rule_id == "TEST001"

    def test_forbidden_value_not_triggered(self):
        rule = PropertyRule(
            rule_id="TEST001",
            title="Test",
            description="Test rule",
            severity=Severity.HIGH,
            resource_types=["aws_s3_bucket"],
            property_name="acl",
            forbidden_value="public-read",
        )
        resource = Resource(
            name="my_bucket",
            resource_type="aws_s3_bucket",
            source_file="main.tf",
            properties={"acl": "private"},
        )
        assert rule.check(resource) is None

    def test_expected_value_triggers(self):
        rule = PropertyRule(
            rule_id="TEST002",
            title="Test",
            description="Test rule",
            severity=Severity.HIGH,
            resource_types=["aws_ebs_volume"],
            property_name="encrypted",
            expected_value="true",
        )
        resource = Resource(
            name="my_vol",
            resource_type="aws_ebs_volume",
            source_file="main.tf",
            properties={"encrypted": "false"},
        )
        assert rule.check(resource) is not None

    def test_required_property_missing(self):
        rule = PropertyRule(
            rule_id="TEST003",
            title="Test",
            description="Test rule",
            severity=Severity.MEDIUM,
            resource_types=["aws_sqs_queue"],
            property_name="kms_master_key_id",
            required=True,
        )
        resource = Resource(
            name="my_queue",
            resource_type="aws_sqs_queue",
            source_file="main.tf",
            properties={},
        )
        assert rule.check(resource) is not None


class TestTagRule:
    def test_missing_tags(self):
        rule = TagRule(
            rule_id="TAG001",
            title="Missing tags",
            description="Required tags missing",
            severity=Severity.MEDIUM,
            required_tags=["Environment", "Owner"],
        )
        resource = Resource(
            name="my_bucket",
            resource_type="aws_s3_bucket",
            source_file="main.tf",
            properties={"tags": {"Environment": "prod"}},
        )
        finding = rule.check(resource)
        assert finding is not None
        assert "Owner" in finding.description

    def test_all_tags_present(self):
        rule = TagRule(
            rule_id="TAG001",
            title="Missing tags",
            description="Required tags missing",
            severity=Severity.MEDIUM,
            required_tags=["Environment"],
        )
        resource = Resource(
            name="my_bucket",
            resource_type="aws_s3_bucket",
            source_file="main.tf",
            properties={"tags": {"Environment": "prod"}},
        )
        assert rule.check(resource) is None


class TestRuleEngine:
    def test_load_builtin_rules(self):
        engine = RuleEngine()
        engine.load_builtin_rules()
        assert engine.rule_count > 0

    def test_scan_finds_issues(self):
        engine = RuleEngine()
        engine.load_builtin_rules()
        resources = [
            Resource(
                name="bad_bucket",
                resource_type="aws_s3_bucket",
                source_file="main.tf",
                properties={"acl": "public-read"},
            )
        ]
        findings = engine.scan(resources)
        assert len(findings) > 0
        assert any(f.rule_id == "SEC001" for f in findings)

    def test_scan_clean_resource(self):
        engine = RuleEngine()
        engine.load_builtin_rules()
        resources = [
            Resource(
                name="good_bucket",
                resource_type="aws_s3_bucket",
                source_file="main.tf",
                properties={
                    "acl": "private",
                    "tags": {"Environment": "prod", "Owner": "team", "CostCenter": "123"},
                    "versioning": "Enabled",
                },
            )
        ]
        findings = engine.scan(resources)
        assert not any(f.rule_id in ("SEC001", "SEC002") for f in findings)


# --- Cost Tests ---

class TestCostEstimator:
    def test_estimate_ec2(self):
        estimator = CostEstimator()
        resource = Resource(
            name="web",
            resource_type="aws_instance",
            source_file="main.tf",
            properties={"instance_type": "t3.micro"},
        )
        est = estimator.estimate(resource)
        assert est is not None
        assert est.monthly_cost_usd == 8.50

    def test_estimate_rds(self):
        estimator = CostEstimator()
        resource = Resource(
            name="db",
            resource_type="aws_db_instance",
            source_file="main.tf",
            properties={"instance_class": "db.t3.micro"},
        )
        est = estimator.estimate(resource)
        assert est is not None
        assert est.monthly_cost_usd == 15.00

    def test_estimate_total(self):
        estimator = CostEstimator()
        resources = [
            Resource(
                name="web",
                resource_type="aws_instance",
                source_file="main.tf",
                properties={"instance_type": "t3.micro"},
            ),
            Resource(
                name="db",
                resource_type="aws_db_instance",
                source_file="main.tf",
                properties={"instance_class": "db.t3.micro"},
            ),
        ]
        estimates, total = estimator.estimate_total(resources)
        assert len(estimates) == 2
        assert total == 23.50

    def test_oversized_ec2_finding(self):
        estimator = CostEstimator()
        resources = [
            Resource(
                name="big",
                resource_type="aws_instance",
                source_file="main.tf",
                properties={"instance_type": "m5.4xlarge"},
            ),
        ]
        findings = estimator.find_optimizations(resources)
        assert len(findings) > 0
        assert findings[0].rule_id == "COST_OPT_001"


# --- Report Tests ---

class TestJsonReportGenerator:
    def test_generate(self):
        result = ScanResult(
            findings=[
                Finding(
                    rule_id="SEC001",
                    title="Test",
                    description="Test finding",
                    severity=Severity.HIGH,
                    file_path="main.tf",
                    line_number=1,
                )
            ],
            resources_scanned=5,
            files_scanned=2,
        )
        gen = JsonReportGenerator()
        content = gen.generate(result)
        data = json.loads(content)
        assert data["summary"]["total_findings"] == 1
        assert data["summary"]["severity_breakdown"]["high"] == 1

    def test_write_to_file(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            result = ScanResult(findings=[], resources_scanned=0, files_scanned=0)
            gen = JsonReportGenerator()
            gen.generate(result, Path(f.name))
            data = json.loads(Path(f.name).read_text())
            assert data["summary"]["total_findings"] == 0


class TestMarkdownReportGenerator:
    def test_generate(self):
        result = ScanResult(
            findings=[
                Finding(
                    rule_id="SEC001",
                    title="Test Finding",
                    description="A finding",
                    severity=Severity.CRITICAL,
                    file_path="main.tf",
                    line_number=5,
                )
            ],
            resources_scanned=1,
            files_scanned=1,
        )
        gen = MarkdownReportGenerator()
        content = gen.generate(result)
        assert "# InfraScan Report" in content
        assert "SEC001" in content


class TestHtmlReportGenerator:
    def test_generate(self):
        result = ScanResult(
            findings=[
                Finding(
                    rule_id="SEC001",
                    title="Test",
                    description="A finding",
                    severity=Severity.HIGH,
                    file_path="main.tf",
                    line_number=1,
                )
            ],
            resources_scanned=1,
            files_scanned=1,
        )
        gen = HtmlReportGenerator()
        content = gen.generate(result)
        assert "<!DOCTYPE html>" in content
        assert "InfraScan" in content


# --- Integration Tests ---

class TestEndToEnd:
    def test_full_scan_pipeline(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
            f.write(
                'resource "aws_s3_bucket" "bad_bucket" {\n'
                '  acl = "public-read"\n'
                '}\n'
                'resource "aws_instance" "web" {\n'
                '  instance_type = "t3.micro"\n'
                '}\n'
            )
            f.flush()

            registry = ParserRegistry()
            resources = registry.parse_file(Path(f.name))
            assert len(resources) == 2

            engine = RuleEngine()
            engine.load_builtin_rules()
            findings = engine.scan(resources)
            assert any(f.rule_id == "SEC001" for f in findings)

    def test_cost_estimation_pipeline(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "infra.tf").write_text(
                'resource "aws_instance" "web" {\n'
                '  instance_type = "t3.micro"\n'
                '}\n'
                'resource "aws_db_instance" "db" {\n'
                '  instance_class = "db.t3.micro"\n'
                '}\n'
            )
            registry = ParserRegistry()
            resources = registry.scan_directory(Path(tmpdir))
            assert len(resources) == 2

            estimator = CostEstimator()
            estimates, total = estimator.estimate_total(resources)
            assert len(estimates) == 2
            assert total > 0
