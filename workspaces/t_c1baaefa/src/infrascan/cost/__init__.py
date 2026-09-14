"""Cost estimation and optimization for cloud resources."""

from dataclasses import dataclass
from typing import Any, Optional

from infrascan.schemas import Finding, Resource, Severity


@dataclass
class CostEstimate:
    """Estimated monthly cost for a resource."""
    resource_name: str
    resource_type: str
    monthly_cost_usd: float
    unit: str = "USD/month"
    confidence: str = "medium"
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "resource_name": self.resource_name,
            "resource_type": self.resource_type,
            "monthly_cost_usd": round(self.monthly_cost_usd, 2),
            "unit": self.unit,
            "confidence": self.confidence,
            "notes": self.notes,
        }


# Approximate monthly costs for common AWS resources
EC2_PRICING = {
    "t3.micro": 8.50,
    "t3.small": 17.00,
    "t3.medium": 34.00,
    "t3.large": 68.00,
    "t3.xlarge": 136.00,
    "t3.2xlarge": 272.00,
    "m5.large": 70.00,
    "m5.xlarge": 140.00,
    "m5.2xlarge": 280.00,
    "m5.4xlarge": 560.00,
    "m5.8xlarge": 1120.00,
    "m5.12xlarge": 1680.00,
    "m5.16xlarge": 2240.00,
    "m5.24xlarge": 3360.00,
    "c5.large": 62.00,
    "c5.xlarge": 124.00,
    "c5.2xlarge": 248.00,
    "c5.4xlarge": 496.00,
    "c5.9xlarge": 1116.00,
    "c5.18xlarge": 2232.00,
    "r5.large": 91.00,
    "r5.xlarge": 182.00,
    "r5.2xlarge": 364.00,
    "r5.4xlarge": 728.00,
    "r5.8xlarge": 1456.00,
    "r5.12xlarge": 2184.00,
    "r5.16xlarge": 2912.00,
    "r5.24xlarge": 4368.00,
}

RDS_PRICING = {
    "db.t3.micro": 15.00,
    "db.t3.small": 30.00,
    "db.t3.medium": 60.00,
    "db.t3.large": 120.00,
    "db.m5.large": 140.00,
    "db.m5.xlarge": 280.00,
    "db.m5.2xlarge": 560.00,
    "db.m5.4xlarge": 1120.00,
    "db.r5.large": 180.00,
    "db.r5.xlarge": 360.00,
    "db.r5.2xlarge": 720.00,
    "db.r5.4xlarge": 1440.00,
}

EBS_PRICING_PER_GB = {
    "gp3": 0.08,
    "gp2": 0.10,
    "io1": 0.125,
    "io2": 0.125,
    "st1": 0.045,
    "sc1": 0.025,
}

S3_PRICING_PER_GB = 0.023
NAT_GATEWAY_MONTHLY = 32.40

ELB_MONTHLY = {
    "application": 16.20,
    "network": 16.20,
    "classic": 18.00,
}


class CostEstimator:
    """Estimates monthly costs for cloud resources."""

    def estimate(self, resource: Resource) -> Optional[CostEstimate]:
        rtype = resource.resource_type
        props = resource.properties

        if rtype == "aws_instance":
            return self._estimate_ec2(props, resource.name)
        elif rtype == "aws_db_instance":
            return self._estimate_rds(props, resource.name)
        elif rtype == "aws_ebs_volume":
            return self._estimate_ebs(props, resource.name)
        elif rtype == "aws_s3_bucket":
            return CostEstimate(
                resource_name=resource.name,
                resource_type=rtype,
                monthly_cost_usd=0.0,
                confidence="low",
                notes="S3 cost depends on storage used; minimal base cost",
            )
        elif rtype == "aws_nat_gateway":
            return CostEstimate(
                resource_name=resource.name,
                resource_type=rtype,
                monthly_cost_usd=NAT_GATEWAY_MONTHLY,
                notes="Does not include data processing charges",
            )
        elif rtype in ("aws_lb", "aws_alb", "aws_lb_listener"):
            lb_type = props.get("load_balancer_type", "application")
            return CostEstimate(
                resource_name=resource.name,
                resource_type=rtype,
                monthly_cost_usd=ELB_MONTHLY.get(lb_type, 16.20),
                notes="Does not include LCU charges",
            )
        elif rtype == "aws_eks_cluster":
            return CostEstimate(
                resource_name=resource.name,
                resource_type=rtype,
                monthly_cost_usd=73.00,
                notes="EKS cluster fee only; node costs not included",
            )
        elif rtype == "aws_lambda_function":
            return CostEstimate(
                resource_name=resource.name,
                resource_type=rtype,
                monthly_cost_usd=0.0,
                notes="Lambda is pay-per-invocation; typically free tier eligible",
            )
        return None

    def _estimate_ec2(self, props: dict[str, Any], name: str) -> Optional[CostEstimate]:
        instance_type = props.get("instance_type", "")
        if not instance_type:
            return None
        cost = EC2_PRICING.get(instance_type)
        if cost:
            return CostEstimate(
                resource_name=name,
                resource_type="aws_instance",
                monthly_cost_usd=cost,
                notes=f"On-demand pricing for {instance_type} (750 hrs/month)",
            )
        for key, cost in EC2_PRICING.items():
            if instance_type.startswith(key.rsplit(".", 1)[0]):
                return CostEstimate(
                    resource_name=name,
                    resource_type="aws_instance",
                    monthly_cost_usd=cost * 1.5,
                    confidence="low",
                    notes=f"Approximate pricing for {instance_type}",
                )
        return None

    def _estimate_rds(self, props: dict[str, Any], name: str) -> Optional[CostEstimate]:
        instance_class = props.get("instance_class", "db.t3.micro")
        cost = RDS_PRICING.get(instance_class)
        multi_az = str(props.get("multi_az", "false")).lower() == "true"
        if cost:
            if multi_az:
                cost *= 2
            notes = f"On-demand pricing for {instance_class}"
            if multi_az:
                notes += " (Multi-AZ doubles cost)"
            return CostEstimate(
                resource_name=name,
                resource_type="aws_db_instance",
                monthly_cost_usd=cost,
                notes=notes,
            )
        return None

    def _estimate_ebs(self, props: dict[str, Any], name: str) -> Optional[CostEstimate]:
        size = props.get("size", "100")
        volume_type = props.get("type", "gp3")
        try:
            size_gb = int(size)
        except (ValueError, TypeError):
            size_gb = 100
        per_gb = EBS_PRICING_PER_GB.get(volume_type, 0.08)
        cost = size_gb * per_gb
        return CostEstimate(
            resource_name=name,
            resource_type="aws_ebs_volume",
            monthly_cost_usd=cost,
            notes=f"{size_gb} GB of {volume_type}",
        )

    def estimate_total(self, resources: list[Resource]) -> tuple[list[CostEstimate], float]:
        estimates: list[CostEstimate] = []
        total = 0.0
        for resource in resources:
            est = self.estimate(resource)
            if est is not None:
                estimates.append(est)
                total += est.monthly_cost_usd
        return estimates, total

    def find_optimizations(self, resources: list[Resource]) -> list[Finding]:
        findings: list[Finding] = []
        for resource in resources:
            rtype = resource.resource_type
            props = resource.properties

            if rtype == "aws_instance":
                itype = props.get("instance_type", "")
                if any(s in itype for s in [".2xlarge", ".4xlarge", ".8xlarge"]):
                    findings.append(Finding(
                        rule_id="COST_OPT_001",
                        title="Potential Over-Provisioned EC2 Instance",
                        description=f"Instance {resource.name} uses {itype}. Consider rightsizing.",
                        severity=Severity.MEDIUM,
                        resource=resource,
                        file_path=resource.source_file,
                        line_number=resource.line_start,
                        remediation="Monitor CPU/memory usage and downsize if underutilized",
                        category="cost",
                    ))

            elif rtype == "aws_db_instance":
                multi_az = str(props.get("multi_az", "false")).lower() == "true"
                tags = props.get("tags", {})
                env = str(tags.get("Environment", "")).lower()
                if multi_az and env in ("dev", "test", "staging"):
                    findings.append(Finding(
                        rule_id="COST_OPT_002",
                        title="Multi-AZ Not Needed in Non-Production",
                        description=f"RDS {resource.name} has Multi-AZ enabled in {env}",
                        severity=Severity.LOW,
                        resource=resource,
                        file_path=resource.source_file,
                        line_number=resource.line_start,
                        remediation="Disable Multi-AZ for non-production environments",
                        category="cost",
                    ))

        return findings
