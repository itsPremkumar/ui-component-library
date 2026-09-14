"""Tests for PactNet contract testing framework."""
import json
import tempfile
import threading
import time
from pathlib import Path

import pytest

from pactnet.consumer import Contract, Interaction
from pactnet.consumer import consumer
from pactnet.pact import PactWriter, PactReader, read_pact, write_pact
from pactnet.pact.matcher import (
    TypeMatcher, RegexMatcher, IntegerMatcher, DecimalMatcher,
    BooleanMatcher, EachLikeMatcher, like, regex, integer, decimal, boolean, each_like,
    is_matcher,
)
from pactnet.mock_server import MockServer
from pactnet.provider import ProviderVerifier, VerificationResult, VerificationReport, verify_provider
from pactnet.versioning import (
    ContractVersioner, CompatibilityLevel, compare_contracts,
)


# ==========================================
# Matcher Tests
# ==========================================

class TestTypeMatcher:
    def test_basic_matching(self):
        m = TypeMatcher(example="hello")
        assert m.to_pact_format() == {"match": "type", "value": "hello"}

    def test_integer_example(self):
        m = TypeMatcher(example=42)
        assert m.to_pact_format() == {"match": "type", "value": 42}

    def test_dict_example(self):
        m = TypeMatcher(example={"id": 1})
        assert m.to_pact_format() == {"match": "type", "value": {"id": 1}}


class TestRegexMatcher:
    def test_email_pattern(self):
        m = RegexMatcher(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", example="user@test.com")
        result = m.to_pact_format()
        assert result["match"] == "regex"
        assert result["regex"] == r"^[\w\.-]+@[\w\.-]+\.\w+$"
        assert result["value"] == "user@test.com"

    def test_uuid_pattern(self):
        m = RegexMatcher(
            pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            example="abc12345-6789-0def-a123-4567890abcde",
        )
        result = m.to_pact_format()
        assert result["match"] == "regex"


class TestConvenienceMatchers:
    def test_like(self):
        m = like("test")
        assert isinstance(m, TypeMatcher)
        assert m.example == "test"

    def test_regex(self):
        m = regex(r"\d+", "123")
        assert isinstance(m, RegexMatcher)
        assert m.pattern == r"\d+"

    def test_integer(self):
        m = integer(42)
        assert isinstance(m, IntegerMatcher)
        assert m.example == 42

    def test_decimal(self):
        m = decimal(3.14)
        assert isinstance(m, DecimalMatcher)
        assert m.example == 3.14

    def test_boolean(self):
        m = boolean(False)
        assert isinstance(m, BooleanMatcher)
        assert m.example is False

    def test_each_like(self):
        m = each_like({"id": 1}, min_count=2)
        assert isinstance(m, EachLikeMatcher)
        assert m.min_count == 2

    def test_is_matcher(self):
        assert is_matcher(like("x"))
        assert is_matcher(regex(r"\d+"))
        assert not is_matcher("plain string")
        assert not is_matcher(42)
        assert not is_matcher({})


# ==========================================
# Contract / Interaction Tests
# ==========================================

class TestInteraction:
    def test_create_basic(self):
        i = Interaction("get user")
        assert i.description == "get user"
        assert i.provider_state is None
        assert i.request == {}
        assert i.response == {}

    def test_fluent_api(self):
        i = (
            Interaction("create user")
            .given("user does not exist")
            .with_request("POST", "/api/users", body={"name": "Alice"})
            .will_respond_with(201, body={"id": 1, "name": "Alice"})
        )
        assert i.provider_state == "user does not exist"
        assert i.request["method"] == "POST"
        assert i.request["path"] == "/api/users"
        assert i.request["body"] == {"name": "Alice"}
        assert i.response["status"] == 201

    def test_to_dict(self):
        i = (
            Interaction("get user")
            .given("user exists")
            .with_request("GET", "/api/users/1")
            .will_respond_with(200, body={"id": 1})
        )
        d = i.to_dict()
        assert d["description"] == "get user"
        assert d["providerState"] == "user exists"
        assert d["request"]["method"] == "GET"
        assert d["response"]["status"] == 200

    def test_unique_ids(self):
        i1 = Interaction("one")
        i2 = Interaction("two")
        assert i1.id != i2.id


class TestContract:
    def test_create_contract(self):
        c = Contract("order-service", "user-service")
        assert c.consumer_name == "order-service"
        assert c.provider_name == "user-service"
        assert len(c) == 0

    def test_add_interaction(self):
        c = Contract("order-service", "user-service")
        i = Interaction("test")
        c.add_interaction(i)
        assert len(c) == 1

    def test_new_interaction(self):
        c = Contract("order-service", "user-service")
        i = c.new_interaction("get user")
        assert len(c) == 1
        assert i.description == "get user"

    def test_to_dict(self):
        c = Contract("order-service", "user-service")
        c.new_interaction("test").with_request("GET", "/health").will_respond_with(200)
        d = c.to_dict()
        assert d["consumer"]["name"] == "order-service"
        assert d["provider"]["name"] == "user-service"
        assert len(d["interactions"]) == 1
        assert "metadata" in d

    def test_repr(self):
        c = Contract("order-service", "user-service")
        r = repr(c)
        assert "order-service" in r
        assert "user-service" in r

    def test_consumer_factory(self):
        c = consumer("order-service")
        assert c.consumer_name == "order-service"


# ==========================================
# Pact I/O Tests
# ==========================================

class TestPactIO:
    def test_write_and_read(self, tmp_path):
        contract = Contract("order-service", "user-service")
        contract.new_interaction("get user").with_request(
            "GET", "/api/users/1"
        ).will_respond_with(200, body={"id": 1, "name": "Alice"})

        output = tmp_path / "test-pact.json"
        PactWriter(contract).write(output)

        assert output.exists()

        read_contract = PactReader().read(output)
        assert read_contract.consumer_name == "order-service"
        assert read_contract.provider_name == "user-service"
        assert len(read_contract) == 1

    def test_convenience_functions(self, tmp_path):
        contract = Contract("a", "b")
        contract.new_interaction("test")

        output = tmp_path / "pact.json"
        write_pact(contract, output)
        read_contract = read_pact(output)
        assert read_contract.consumer_name == "a"

    def test_read_nonexistent_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            read_pact(tmp_path / "nonexistent.json")

    def test_multiple_interactions(self, tmp_path):
        contract = Contract("a", "b")
        contract.new_interaction("one").with_request("GET", "/one")
        contract.new_interaction("two").with_request("POST", "/two")
        contract.new_interaction("three").with_request("DELETE", "/three")

        output = tmp_path / "multi.json"
        write_pact(contract, output)
        read_contract = read_pact(output)
        assert len(read_contract) == 3

    def test_provider_state_preserved(self, tmp_path):
        contract = Contract("a", "b")
        contract.new_interaction("test").given("some state")

        output = tmp_path / "state.json"
        write_pact(contract, output)
        read_contract = read_pact(output)
        assert read_contract.interactions[0].provider_state == "some state"


# ==========================================
# Mock Server Tests
# ==========================================

class TestMockServer:
    def test_create_server(self):
        server = MockServer(host="localhost", port=9999)
        assert server.url == "http://localhost:9999"

    def test_load_pact_and_serve(self, tmp_path):
        # Create a pact file
        contract = Contract("test-consumer", "test-provider")
        contract.new_interaction("health check").with_request(
            "GET", "/health"
        ).will_respond_with(200, body={"status": "healthy"})

        pact_file = tmp_path / "test.json"
        write_pact(contract, pact_file)

        # Start mock server
        server = MockServer(host="localhost", port=18080)
        count = server.load_pact(pact_file)
        assert count == 1

        server.start()
        time.sleep(0.5)

        try:
            import urllib.request
            with urllib.request.urlopen("http://localhost:18080/health", timeout=5) as resp:
                body = json.loads(resp.read().decode())
                assert resp.status == 200
                assert body["status"] == "healthy"
        finally:
            server.stop()

    def test_context_manager(self, tmp_path):
        contract = Contract("a", "b")
        contract.new_interaction("test").with_request("GET", "/test").will_respond_with(200)
        pact_file = tmp_path / "cm.json"
        write_pact(contract, pact_file)

        server = MockServer(host="localhost", port=18081)
        server.load_pact(pact_file)

        with server:
            time.sleep(0.5)
            import urllib.request
            with urllib.request.urlopen("http://localhost:18081/test", timeout=5) as resp:
                assert resp.status == 200

    def test_no_match_returns_500(self, tmp_path):
        contract = Contract("a", "b")
        contract.new_interaction("test").with_request("GET", "/exists").will_respond_with(200)
        pact_file = tmp_path / "nm.json"
        write_pact(contract, pact_file)

        server = MockServer(host="localhost", port=18082)
        server.load_pact(pact_file)
        server.start()
        time.sleep(0.5)

        try:
            import urllib.request
            import urllib.error
            try:
                urllib.request.urlopen("http://localhost:18082/notfound", timeout=5)
            except urllib.error.HTTPError as e:
                assert e.code == 500
        finally:
            server.stop()

    def test_add_interaction_programmatically(self):
        server = MockServer(host="localhost", port=18083)
        server.add_interaction(
            "GET", "/api/items",
            {"method": "GET", "path": "/api/items"},
            {"status": 200, "body": [{"id": 1}]},
        )
        assert "/api/items" in server._interactions

    def test_reset(self):
        server = MockServer(host="localhost", port=18084)
        server.add_interaction("GET", "/x", {}, {})
        server.reset()
        assert len(server._interactions) == 0


# ==========================================
# Provider Verifier Tests
# ==========================================

class TestProviderVerifier:
    def test_create_verifier(self):
        v = ProviderVerifier("http://localhost:8080")
        assert v.provider_base_url == "http://localhost:8080"

    def test_verify_interaction_success(self):
        # Set up a mock provider
        contract = Contract("c", "p")
        contract.new_interaction("test").with_request("GET", "/test").will_respond_with(
            200, body={"ok": True}
        )
        pact_file = Path(tempfile.mktemp(suffix=".json"))
        write_pact(contract, pact_file)

        server = MockServer(host="localhost", port=18085)
        server.load_pact(pact_file)
        server.start()
        time.sleep(0.5)

        try:
            v = ProviderVerifier("http://localhost:18085")
            report = v.verify_pact_file(pact_file)
            assert report.success
            assert report.total == 1
            assert report.passed == 1
            assert report.failed == 0
        finally:
            server.stop()
            pact_file.unlink(missing_ok=True)

    def test_verify_with_status_mismatch(self):
        contract = Contract("c", "p")
        contract.new_interaction("test").with_request(
            "GET", "/missing"
        ).will_respond_with(200)  # mock returns 500 for /missing

        pact_file = Path(tempfile.mktemp(suffix=".json"))
        write_pact(contract, pact_file)

        # Start mock server WITHOUT loading the pact - so /missing returns 500
        server = MockServer(host="localhost", port=18086)
        server.start()
        time.sleep(0.5)

        try:
            v = ProviderVerifier("http://localhost:18086")
            report = v.verify_pact_file(pact_file)
            assert not report.success
            assert report.failed >= 1
        finally:
            server.stop()
            pact_file.unlink(missing_ok=True)

    def test_report_to_dict(self):
        from pactnet.provider import VerificationReport

        report2 = VerificationReport("prov", "cons")
        report2.results.append(VerificationResult(interaction_description="a", success=True))
        report2.results.append(VerificationResult(interaction_description="b", success=False, error="fail"))

        assert report2.total == 2
        assert report2.passed == 1
        assert report2.failed == 1
        assert not report2.success

        d = report2.to_dict()
        assert d["provider"] == "prov"
        assert d["consumer"] == "cons"
        assert d["summary"]["total"] == 2

    def test_str_representation(self):
        report = VerificationReport("prov", "cons")
        report.results.append(VerificationResult(interaction_description="a", success=True))
        s = str(report)
        assert "PASS" in s
        assert "1/1" in s

    def test_verify_interaction_manual(self):
        v = ProviderVerifier("http://localhost:18087")
        # Test with unreachable server
        result = v.verify_interaction(
            method="GET",
            path="/test",
            expected_response={"status": 200},
            description="manual test",
        )
        assert isinstance(result, VerificationResult)
        assert not result.success


# ==========================================
# Versioning Tests
# ==========================================

class TestContractVersioner:
    def test_save_and_load_version(self, tmp_path):
        versioner = ContractVersioner(tmp_path / "versions")
        contract = {"consumer": {"name": "a"}, "provider": {"name": "b"}, "interactions": []}
        versioner.save_version(contract, "1.0.0")

        loaded = versioner.load_version("1.0.0")
        assert loaded["consumer"]["name"] == "a"

    def test_list_versions(self, tmp_path):
        versioner = ContractVersioner(tmp_path / "versions")
        contract = {"consumer": {"name": "a"}, "provider": {"name": "b"}, "interactions": []}
        versioner.save_version(contract, "1.0.0")
        versioner.save_version(contract, "1.1.0")
        versioner.save_version(contract, "2.0.0")

        versions = versioner.list_versions()
        assert "1.0.0" in versions
        assert "1.1.0" in versions
        assert "2.0.0" in versions

    def test_compare_no_changes(self, tmp_path):
        versioner = ContractVersioner(tmp_path / "versions")
        contract = {
            "consumer": {"name": "a"},
            "provider": {"name": "b"},
            "interactions": [
                {
                    "description": "test",
                    "request": {"method": "GET", "path": "/x"},
                    "response": {"status": 200},
                }
            ],
        }
        versioner.save_version(contract, "1.0.0")
        versioner.save_version(contract, "1.0.1")

        report = versioner.compare("1.0.0", "1.0.1")
        assert report.level == CompatibilityLevel.UNKNOWN
        assert len(report.changes) == 0

    def test_compare_added_interaction(self, tmp_path):
        versioner = ContractVersioner(tmp_path / "versions")
        v1 = {
            "consumer": {"name": "a"},
            "provider": {"name": "b"},
            "interactions": [],
        }
        v2 = {
            "consumer": {"name": "a"},
            "provider": {"name": "b"},
            "interactions": [
                {
                    "description": "new endpoint",
                    "request": {"method": "GET", "path": "/new"},
                    "response": {"status": 200},
                }
            ],
        }
        versioner.save_version(v1, "1.0.0")
        versioner.save_version(v2, "1.1.0")

        report = versioner.compare("1.0.0", "1.1.0")
        assert any(c.type == "additive" for c in report.changes)

    def test_compare_removed_interaction_breaking(self, tmp_path):
        versioner = ContractVersioner(tmp_path / "versions")
        v1 = {
            "consumer": {"name": "a"},
            "provider": {"name": "b"},
            "interactions": [
                {
                    "description": "old endpoint",
                    "request": {"method": "GET", "path": "/old"},
                    "response": {"status": 200},
                }
            ],
        }
        v2 = {
            "consumer": {"name": "a"},
            "provider": {"name": "b"},
            "interactions": [],
        }
        versioner.save_version(v1, "1.0.0")
        versioner.save_version(v2, "2.0.0")

        report = versioner.compare("1.0.0", "2.0.0")
        assert report.level == CompatibilityLevel.BACKWARDS_INCOMPATIBLE
        assert len(report.breaking_changes) > 0

    def test_compare_changed_status(self, tmp_path):
        versioner = ContractVersioner(tmp_path / "versions")
        v1 = {
            "consumer": {"name": "a"},
            "provider": {"name": "b"},
            "interactions": [
                {
                    "description": "test",
                    "request": {"method": "GET", "path": "/x"},
                    "response": {"status": 200},
                }
            ],
        }
        v2 = {
            "consumer": {"name": "a"},
            "provider": {"name": "b"},
            "interactions": [
                {
                    "description": "test",
                    "request": {"method": "GET", "path": "/x"},
                    "response": {"status": 201},
                }
            ],
        }
        versioner.save_version(v1, "1.0.0")
        versioner.save_version(v2, "2.0.0")

        report = versioner.compare("1.0.0", "2.0.0")
        assert any("status" in c.description.lower() for c in report.changes)

    def test_compare_changed_path(self, tmp_path):
        versioner = ContractVersioner(tmp_path / "versions")
        v1 = {
            "consumer": {"name": "a"},
            "provider": {"name": "b"},
            "interactions": [
                {
                    "description": "test",
                    "request": {"method": "GET", "path": "/v1/users"},
                    "response": {"status": 200},
                }
            ],
        }
        v2 = {
            "consumer": {"name": "a"},
            "provider": {"name": "b"},
            "interactions": [
                {
                    "description": "test",
                    "request": {"method": "GET", "path": "/v2/users"},
                    "response": {"status": 200},
                }
            ],
        }
        versioner.save_version(v1, "1.0.0")
        versioner.save_version(v2, "2.0.0")

        report = versioner.compare("1.0.0", "2.0.0")
        assert any("path" in c.description.lower() for c in report.changes)

    def test_load_nonexistent_version(self, tmp_path):
        versioner = ContractVersioner(tmp_path / "versions")
        with pytest.raises(FileNotFoundError):
            versioner.load_version("999.0.0")

    def test_compare_contracts_files(self, tmp_path):
        v1 = tmp_path / "v1.json"
        v2 = tmp_path / "v2.json"

        v1.write_text(json.dumps({
            "consumer": {"name": "a"},
            "provider": {"name": "b"},
            "interactions": [
                {
                    "description": "endpoint",
                    "request": {"method": "GET", "path": "/x"},
                    "response": {"status": 200},
                }
            ],
        }))
        v2.write_text(json.dumps({
            "consumer": {"name": "a"},
            "provider": {"name": "b"},
            "interactions": [],
        }))

        report = compare_contracts(v1, v2)
        assert report.level == CompatibilityLevel.BACKWARDS_INCOMPATIBLE


# ==========================================
# Integration Tests
# ==========================================

class TestEndToEndEndToEnd:
    def test_full_consumer_driven_workflow(self, tmp_path):
        """Test the complete CDC workflow: define -> write -> mock -> verify."""
        # 1. Consumer defines expected interactions
        contract = Contract("order-service", "payment-service")
        contract.new_interaction("create payment").given(
            "valid payment request"
        ).with_request(
            "POST", "/api/payments",
            body={"order_id": "ord-123", "amount": 99.99, "currency": "USD"},
        ).will_respond_with(
            201,
            body={"payment_id": "pay-456", "status": "authorized", "amount": 99.99},
        )

        # 2. Write to pact file
        pact_file = tmp_path / "payment-pact.json"
        write_pact(contract, pact_file)
        assert pact_file.exists()

        # 3. Load into mock server
        server = MockServer(host="localhost", port=18090)
        count = server.load_pact(pact_file)
        assert count == 1

        # 4. Start mock and verify consumer expectations
        server.start()
        time.sleep(0.5)

        try:
            verifier = ProviderVerifier("http://localhost:18090")
            report = verifier.verify_pact_file(pact_file)
            assert report.success, f"Verification failed: {report}"
            assert report.passed == 1
        finally:
            server.stop()

    def test_multiple_interactions_workflow(self, tmp_path):
        """Test full workflow with multiple interactions."""
        contract = Contract("frontend", "backend-api")
        contract.new_interaction("get user profile").with_request(
            "GET", "/api/users/me"
        ).will_respond_with(200, body={"id": 1, "name": "Test User", "email": "test@example.com"})

        contract.new_interaction("update user profile").with_request(
            "PATCH", "/api/users/me", body={"name": "Updated"}
        ).will_respond_with(200, body={"id": 1, "name": "Updated", "email": "test@example.com"})

        contract.new_interaction("delete user").with_request(
            "DELETE", "/api/users/me"
        ).will_respond_with(204)

        pact_file = tmp_path / "multi-pact.json"
        write_pact(contract, pact_file)

        server = MockServer(host="localhost", port=18091)
        server.load_pact(pact_file)
        server.start()
        time.sleep(0.5)

        try:
            verifier = ProviderVerifier("http://localhost:18091")
            report = verifier.verify_pact_file(pact_file)
            assert report.success
            assert report.total == 3
            assert report.passed == 3
        finally:
            server.stop()
