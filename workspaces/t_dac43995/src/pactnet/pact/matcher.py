"""Request/response matchers for contract definitions."""
import re
from typing import Any


class Matcher:
    """Base class for request/response matchers."""

    def to_pact_format(self) -> dict:
        raise NotImplementedError


class TypeMatcher(Matcher):
    """Match a value by its type."""

    def __init__(self, example: Any):
        self.example = example

    def to_pact_format(self) -> dict:
        return {"match": "type", "value": self.example}


class RegexMatcher(Matcher):
    """Match a string value against a regex pattern."""

    def __init__(self, pattern: str, example: str = ""):
        self.pattern = pattern
        self.example = example

    def to_pact_format(self) -> dict:
        return {"match": "regex", "regex": self.pattern, "value": self.example}


class IntegerMatcher(Matcher):
    """Match an integer value."""

    def __init__(self, example: int = 1):
        self.example = example

    def to_pact_format(self) -> dict:
        return {"match": "integer", "value": self.example}


class DecimalMatcher(Matcher):
    """Match a decimal/float value."""

    def __init__(self, example: float = 1.0):
        self.example = example

    def to_pact_format(self) -> dict:
        return {"match": "decimal", "value": self.example}


class BooleanMatcher(Matcher):
    """Match a boolean value."""

    def __init__(self, example: bool = True):
        self.example = example

    def to_pact_format(self) -> dict:
        return {"match": "boolean", "value": self.example}


class ArrayContainsMatcher(Matcher):
    """Match an array that contains specific elements."""

    def __init__(self, variants: list):
        self.variants = variants

    def to_pact_format(self) -> dict:
        return {"match": "arrayContains", "variants": self.variants}


class EachLikeMatcher(Matcher):
    """Match an array of similar items."""

    def __init__(self, example: Any, min_count: int = 1):
        self.example = example
        self.min_count = min_count

    def to_pact_format(self) -> dict:
        return {
            "match": "type",
            "value": self.example,
            "min": self.min_count,
        }


def like(example: Any) -> Matcher:
    """Convenience: match by type with an example value."""
    return TypeMatcher(example)


def regex(pattern: str, example: str = "") -> Matcher:
    """Convenience: match by regex pattern."""
    return RegexMatcher(pattern, example)


def integer(example: int = 1) -> Matcher:
    """Convenience: match an integer."""
    return IntegerMatcher(example)


def decimal(example: float = 1.0) -> Matcher:
    """Convenience: match a decimal."""
    return DecimalMatcher(example)


def boolean(example: bool = True) -> Matcher:
    """Convenience: match a boolean."""
    return BooleanMatcher(example)


def each_like(example: Any, min_count: int = 1) -> Matcher:
    """Convenience: match an array of similar items."""
    return EachLikeMatcher(example, min_count)


def is_matcher(value: Any) -> bool:
    """Check if a value is a Matcher instance."""
    return isinstance(value, Matcher)
