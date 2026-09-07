"""UI Component Library — reusable components for web applications."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional
import uuid


@dataclass
class Component:
    """Base component."""
    component_id: str = field(default_factory=lambda: f"comp_{uuid.uuid4().hex[:8]}")
    component_type: str = "div"
    props: dict[str, Any] = field(default_factory=dict)
    children: list["Component"] = field(default_factory=list)
    parent: Optional["Component"] = None
    visible: bool = True
    enabled: bool = True
    classes: list[str] = field(default_factory=list)
    styles: dict[str, str] = field(default_factory=dict)
    event_handlers: dict[str, Callable] = field(default_factory=dict)

    def add_child(self, child: "Component") -> "Component":
        child.parent = self
        self.children.append(child)
        return child

    def remove_child(self, child: "Component") -> None:
        self.children = [c for c in self.children if c.component_id != child.component_id]

    def find_by_id(self, component_id: str) -> Optional["Component"]:
        if self.component_id == component_id:
            return self
        for child in self.children:
            found = child.find_by_id(component_id)
            if found:
                return found
        return None

    def find_by_type(self, component_type: str) -> list["Component"]:
        results = []
        if self.component_type == component_type:
            results.append(self)
        for child in self.children:
            results.extend(child.find_by_type(component_type))
        return results

    def set_property(self, key: str, value: Any) -> None:
        self.props[key] = value

    def get_property(self, key: str, default: Any = None) -> Any:
        return self.props.get(key, default)

    def set_style(self, key: str, value: str) -> None:
        self.styles[key] = value

    def add_class(self, class_name: str) -> None:
        if class_name not in self.classes:
            self.classes.append(class_name)

    def remove_class(self, class_name: str) -> None:
        self.classes = [c for c in self.classes if c != class_name]

    def on(self, event: str, handler: Callable) -> None:
        self.event_handlers[event] = handler

    def trigger(self, event: str, *args, **kwargs) -> Any:
        handler = self.event_handlers.get(event)
        if handler:
            return handler(*args, **kwargs)
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.component_id,
            "type": self.component_type,
            "props": self.props,
            "visible": self.visible,
            "enabled": self.enabled,
            "classes": self.classes,
            "styles": self.styles,
            "children": [c.to_dict() for c in self.children],
        }

    def render(self, indent: int = 0) -> str:
        """Render component tree as string."""
        if not self.visible:
            return ""

        props_str = " ".join(f'{k}="{v}"' for k, v in self.props.items())
        classes_str = " ".join(self.classes)
        styles_str = "; ".join(f"{k}: {v}" for k, v in self.styles.items())

        tag = self.component_type
        attrs = []
        if props_str:
            attrs.append(props_str)
        if classes_str:
            attrs.append(f'class="{classes_str}"')
        if styles_str:
            attrs.append(f'style="{styles_str}"')

        attrs_str = " " + " ".join(attrs) if attrs else ""
        prefix = "  " * indent

        if not self.children:
            return f"{prefix}<{tag}{attrs_str} />"

        children_str = "\n".join(c.render(indent + 1) for c in self.children)
        return f"{prefix}<{tag}{attrs_str}>\n{children_str}\n{prefix}</{tag}>"


class Button(Component):
    """Button component."""

    def __init__(self, label: str = "", **kwargs):
        super().__init__(component_type="button", **kwargs)
        self.set_property("label", label)

    def click(self) -> Any:
        return self.trigger("click")


class TextInput(Component):
    """Text input component."""

    def __init__(self, placeholder: str = "", value: str = "", **kwargs):
        super().__init__(component_type="input", **kwargs)
        self.set_property("placeholder", placeholder)
        self.set_property("value", value)

    def get_value(self) -> str:
        return self.get_property("value", "")

    def set_value(self, value: str) -> None:
        self.set_property("value", value)


class Container(Component):
    """Container component."""

    def __init__(self, layout: str = "vertical", **kwargs):
        super().__init__(component_type="div", **kwargs)
        self.set_property("layout", layout)


class Label(Component):
    """Label component."""

    def __init__(self, text: str = "", **kwargs):
        super().__init__(component_type="label", **kwargs)
        self.set_property("text", text)


class Image(Component):
    """Image component."""

    def __init__(self, src: str = "", alt: str = "", **kwargs):
        super().__init__(component_type="img", **kwargs)
        self.set_property("src", src)
        self.set_property("alt", alt)


class Link(Component):
    """Link component."""

    def __init__(self, href: str = "", text: str = "", **kwargs):
        super().__init__(component_type="a", **kwargs)
        self.set_property("href", href)
        self.set_property("text", text)


class List(Component):
    """List component."""

    def __init__(self, items: list[str] | None = None, ordered: bool = False, **kwargs):
        super().__init__(component_type="ol" if ordered else "ul", **kwargs)
        self.set_property("items", items or [])

    def add_item(self, item: str) -> None:
        items = self.get_property("items", [])
        items.append(item)
        self.set_property("items", items)


class Form(Component):
    """Form component."""

    def __init__(self, **kwargs):
        super().__init__(component_type="form", **kwargs)
        self.set_property("fields", {})

    def add_field(self, name: str, field: Component) -> None:
        fields = self.get_property("fields", {})
        fields[name] = field
        self.set_property("fields", fields)
        self.add_child(field)

    def get_data(self) -> dict[str, Any]:
        data = {}
        for name, field in self.get_property("fields", {}).items():
            if isinstance(field, TextInput):
                data[name] = field.get_value()
            elif isinstance(field, Component):
                data[name] = field.props.get("value")
        return data


class Modal(Component):
    """Modal dialog component."""

    def __init__(self, title: str = "", **kwargs):
        super().__init__(component_type="div", **kwargs)
        self.set_property("title", title)
        self.set_property("open", False)

    def open(self) -> None:
        self.set_property("open", True)
        self.visible = True

    def close(self) -> None:
        self.set_property("open", False)
        self.visible = False


class ComponentFactory:
    """Factory for creating components."""

    _registry: dict[str, type[Component]] = {}

    @classmethod
    def register(cls, component_type: str, component_class: type[Component]) -> None:
        cls._registry[component_type] = component_class

    @classmethod
    def create(cls, component_type: str, **kwargs) -> Component:
        component_class = cls._registry.get(component_type, Component)
        return component_class(**kwargs)

    @classmethod
    def get_registered_types(cls) -> list[str]:
        return list(cls._registry.keys())


# Register built-in components
ComponentFactory.register("button", Button)
ComponentFactory.register("input", TextInput)
ComponentFactory.register("container", Container)
ComponentFactory.register("label", Label)
ComponentFactory.register("image", Image)
ComponentFactory.register("link", Link)
ComponentFactory.register("list", List)
ComponentFactory.register("form", Form)
ComponentFactory.register("modal", Modal)
