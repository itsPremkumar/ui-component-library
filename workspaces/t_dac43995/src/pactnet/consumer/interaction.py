"""Consumer-side contract definitions and interactions."""
import uuid
from typing import Any, Optional
from pactnet.pact.matcher import Matcher, is_matcher


class Interaction:
    """Defines an expected interaction between consumer and provider."""

    def __init__(
        self,
        description: str,
        provider_state: Optional[str] = None,
        request: Optional[dict] = None,
        response: Optional[dict] = None,
    ):
        self.id = str(uuid.uuid4())
        self.description = description
        self.provider_state = provider_state
        self.request = request or {}
        self.response = response or {}

    def given(self, state: str) -> "Interaction":
        """Set the provider state."""
        self.provider_state = state
        return self

    def upon_receiving(self, description: str) -> "Interaction":
        """Set the interaction description."""
        self.description = description
        return self

    def with_request(self, method: str, path: str, **kwargs) -> "Interaction":
        """Define the expected request."""
        req = {"method": method.upper(), "path": path}
        if "headers" in kwargs:
            req["headers"] = kwargs["headers"]
        if "body" in kwargs:
            req["body"] = kwargs["body"]
        if "query" in kwargs:
            req["query"] = kwargs["query"]
        self.request = req
        return self

    def will_respond_with(self, status: int, **kwargs) -> "Interaction":
        """Define the expected response."""
        resp = {"status": status}
        if "headers" in kwargs:
            resp["headers"] = kwargs["headers"]
        if "body" in kwargs:
            resp["body"] = kwargs["body"]
        self.response = resp
        return self

    def to_dict(self) -> dict:
        """Serialize to dictionary (Pact format)."""
        result: dict = {"description": self.description}
        if self.provider_state:
            result["providerState"] = self.provider_state
        if self.request:
            result["request"] = self.request
        if self.response:
            result["response"] = self.response
        return result


class Contract:
    """A collection of interactions between a consumer and a provider."""

    def __init__(self, consumer_name: str, provider_name: str):
        self.consumer_name = consumer_name
        self.provider_name = provider_name
        self.interactions: list[Interaction] = []

    def add_interaction(self, interaction: Interaction) -> Interaction:
        """Add an interaction to the contract."""
        self.interactions.append(interaction)
        return interaction

    def new_interaction(self, description: str) -> Interaction:
        """Create and add a new interaction."""
        interaction = Interaction(description)
        self.interactions.append(interaction)
        return interaction

    def to_dict(self) -> dict:
        """Serialize the full contract to Pact format."""
        return {
            "consumer": {"name": self.consumer_name},
            "provider": {"name": self.provider_name},
            "interactions": [i.to_dict() for i in self.interactions],
            "metadata": {
                "pactSpecification": {"version": "3.0.0"},
                "pact-python": {"version": "1.0.0"},
            },
        }

    def __len__(self) -> int:
        return len(self.interactions)

    def __repr__(self) -> str:
        return (
            f"Contract(consumer='{self.consumer_name}', "
            f"provider='{self.provider_name}', "
            f"interactions={len(self.interactions)})"
        )
