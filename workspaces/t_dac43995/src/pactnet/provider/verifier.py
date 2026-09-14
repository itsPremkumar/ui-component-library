"""Provider-side verification suite - validates provider responses against contracts."""
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field

from pactnet.consumer.interaction import Interaction
from pactnet.pact.io import PactReader
from pactnet.pact.matcher import is_matcher, TypeMatcher


@dataclass
class VerificationResult:
    """Result of verifying a single interaction."""
    interaction_description: str
    success: bool
    error: Optional[str] = None
    details: dict = field(default_factory=dict)

    def __bool__(self):
        return self.success


@dataclass
class VerificationReport:
    """Aggregated report of all verification results."""
    provider_name: str
    consumer_name: str
    results: list[VerificationResult] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.success)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.success)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def success(self) -> bool:
        return self.failed == 0 and self.total > 0

    def to_dict(self) -> dict:
        return {
            "provider": self.provider_name,
            "consumer": self.consumer_name,
            "summary": {
                "total": self.total,
                "passed": self.passed,
                "failed": self.failed,
                "success": self.success,
            },
            "results": [
                {
                    "interaction": r.interaction_description,
                    "success": r.success,
                    "error": r.error,
                    "details": r.details,
                }
                for r in self.results
            ],
        }

    def __str__(self) -> str:
        status = "PASS" if self.success else "FAIL"
        return (
            f"[{status}] {self.provider_name} <- {self.consumer_name}: "
            f"{self.passed}/{self.total} passed"
        )


class ProviderVerifier:
    """Verifies a provider against a Pact contract."""

    def __init__(
        self,
        provider_base_url: str,
        pact_path: Optional[Path] = None,
    ):
        self.provider_base_url = provider_base_url.rstrip("/")
        self.pact_path = pact_path
        self._setup_hooks: list = []
        self._teardown_hooks: list = []

    def add_setup_hook(self, hook) -> None:
        """Add a function to run before each interaction verification."""
        self._setup_hooks.append(hook)

    def add_teardown_hook(self, hook) -> None:
        """Add a function to run after each interaction verification."""
        self._teardown_hooks.append(hook)

    def verify_pact_file(self, pact_path: Optional[Path] = None) -> VerificationReport:
        """Verify provider against a Pact contract file."""
        path = pact_path or self.pact_path
        if path is None:
            raise ValueError("No Pact file path provided")

        reader = PactReader()
        contract = reader.read(path)

        report = VerificationReport(
            provider_name=contract.provider_name,
            consumer_name=contract.consumer_name,
        )

        for interaction in contract.interactions:
            result = self._verify_interaction(interaction)
            report.results.append(result)

        return report

    def verify_interaction(
        self,
        method: str,
        path: str,
        expected_response: dict,
        request_headers: Optional[dict] = None,
        request_body: Any = None,
        description: str = "manual interaction",
    ) -> VerificationResult:
        """Verify a single interaction against the provider."""
        try:
            url = f"{self.provider_base_url}{path}"
            headers = request_headers or {}

            body = None
            if request_body is not None:
                body = (
                    json.dumps(request_body).encode()
                    if isinstance(request_body, (dict, list))
                    else str(request_body).encode()
                )
                headers.setdefault("Content-Type", "application/json")

            req = urllib.request.Request(
                url, data=body, headers=headers, method=method.upper()
            )

            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    actual_status = resp.status
                    actual_body = resp.read().decode("utf-8")
            except urllib.error.HTTPError as e:
                actual_status = e.code
                actual_body = e.read().decode("utf-8")

            expected_status = expected_response.get("status", 200)

            if actual_status != expected_status:
                return VerificationResult(
                    interaction_description=description,
                    success=False,
                    error=f"Expected status {expected_status}, got {actual_status}",
                    details={"expected_status": expected_status, "actual_status": actual_status},
                )

            expected_body = expected_response.get("body", {})
            if expected_body:
                try:
                    actual_json = json.loads(actual_body)
                    body_match = self._match_body(expected_body, actual_json)
                    if not body_match:
                        return VerificationResult(
                            interaction_description=description,
                            success=False,
                            error=f"Body mismatch: expected {expected_body}, got {actual_json}",
                            details={"expected_body": expected_body, "actual_body": actual_json},
                        )
                except json.JSONDecodeError:
                    return VerificationResult(
                        interaction_description=description,
                        success=False,
                        error=f"Response body is not valid JSON: {actual_body[:200]}",
                    )

            return VerificationResult(
                interaction_description=description,
                success=True,
            )

        except Exception as e:
            return VerificationResult(
                interaction_description=description,
                success=False,
                error=str(e),
            )

    def _verify_interaction(self, interaction: Interaction) -> VerificationResult:
        """Verify a single interaction with setup/teardown hooks."""
        for hook in self._setup_hooks:
            hook(interaction.provider_state)

        try:
            result = self.verify_interaction(
                method=interaction.request.get("method", "GET"),
                path=interaction.request.get("path", "/"),
                expected_response=interaction.response,
                request_headers=interaction.request.get("headers"),
                request_body=interaction.request.get("body"),
                description=interaction.description,
            )
        finally:
            for hook in self._teardown_hooks:
                hook(interaction.provider_state)

        return result

    def _match_body(self, expected: Any, actual: Any) -> bool:
        """Match response body against expected schema."""
        if is_matcher(expected):
            return True  # Matchers accept any value

        if isinstance(expected, dict):
            if not isinstance(actual, dict):
                return False
            for key, value in expected.items():
                if key not in actual:
                    return False
                if not self._match_body(value, actual[key]):
                    return False
            return True

        if isinstance(expected, list):
            if not isinstance(actual, list):
                return False
            if len(expected) != len(actual):
                return False
            for e_item, a_item in zip(expected, actual):
                if not self._match_body(e_item, a_item):
                    return False
            return True

        return expected == actual


def verify_provider(
    provider_base_url: str,
    pact_path: Path,
) -> VerificationReport:
    """Convenience: verify a provider against a Pact file."""
    verifier = ProviderVerifier(provider_base_url=provider_base_url, pact_path=pact_path)
    return verifier.verify_pact_file()
