"""Convenience alias for creating consumer contracts."""
from pactnet.consumer.interaction import Contract, Interaction


def consumer(name: str) -> Contract:
    """Create a new contract for the named consumer."""
    return Contract(consumer_name=name, provider_name="")


__all__ = ["Contract", "Interaction", "consumer"]
