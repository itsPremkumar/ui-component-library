"""Tests for UI Component Library."""

import pytest

from ui_components.core import (
    Component,
    Button,
    TextInput,
    Container,
    Label,
    Image,
    Link,
    List,
    Form,
    Modal,
    ComponentFactory,
)


class TestComponent:
    def test_create(self):
        comp = Component(component_type="div")
        assert comp.component_type == "div"
        assert comp.visible is True
        assert comp.enabled is True

    def test_add_child(self):
        parent = Component(component_type="div")
        child = Component(component_type="span")
        parent.add_child(child)
        assert len(parent.children) == 1
        assert child.parent == parent

    def test_remove_child(self):
        parent = Component(component_type="div")
        child = Component(component_type="span")
        parent.add_child(child)
        parent.remove_child(child)
        assert len(parent.children) == 0

    def test_find_by_id(self):
        parent = Component(component_type="div")
        child = Component(component_type="span", component_id="child1")
        parent.add_child(child)
        found = parent.find_by_id("child1")
        assert found is not None
        found.component_id = "child1"

    def test_find_by_type(self):
        parent = Component(component_type="div")
        child1 = Component(component_type="button")
        child2 = Component(component_type="button")
        parent.add_child(child1)
        parent.add_child(child2)
        buttons = parent.find_by_type("button")
        assert len(buttons) == 2

    def test_set_get_property(self):
        comp = Component()
        comp.set_property("key", "value")
        assert comp.get_property("key") == "value"

    def test_set_style(self):
        comp = Component()
        comp.set_style("color", "red")
        assert comp.styles["color"] == "red"

    def test_add_remove_class(self):
        comp = Component()
        comp.add_class("active")
        assert "active" in comp.classes
        comp.remove_class("active")
        assert "active" not in comp.classes

    def test_on_trigger(self):
        comp = Component()
        comp.on("click", lambda: "clicked")
        result = comp.trigger("click")
        assert result == "clicked"

    def test_to_dict(self):
        comp = Component(component_type="div")
        data = comp.to_dict()
        assert data["type"] == "div"
        assert "id" in data

    def test_render(self):
        comp = Component(component_type="div")
        comp.add_class("container")
        output = comp.render()
        assert "<div" in output
        assert "container" in output


class TestButton:
    def test_create(self):
        btn = Button(label="Click me")
        assert btn.component_type == "button"
        assert btn.get_property("label") == "Click me"

    def test_click(self):
        btn = Button()
        btn.on("click", lambda: "clicked")
        assert btn.click() == "clicked"


class TestTextInput:
    def test_create(self):
        inp = TextInput(placeholder="Enter text")
        assert inp.component_type == "input"
        assert inp.get_property("placeholder") == "Enter text"

    def test_get_set_value(self):
        inp = TextInput()
        inp.set_value("hello")
        assert inp.get_value() == "hello"


class TestContainer:
    def test_create(self):
        cont = Container(layout="horizontal")
        assert cont.component_type == "div"
        assert cont.get_property("layout") == "horizontal"


class TestLabel:
    def test_create(self):
        lbl = Label(text="Hello")
        assert lbl.component_type == "label"
        assert lbl.get_property("text") == "Hello"


class TestImage:
    def test_create(self):
        img = Image(src="image.png", alt="An image")
        assert img.component_type == "img"
        assert img.get_property("src") == "image.png"


class TestLink:
    def test_create(self):
        link = Link(href="https://example.com", text="Click")
        assert link.component_type == "a"
        assert link.get_property("href") == "https://example.com"


class TestList:
    def test_create(self):
        lst = List(items=["item1", "item2"])
        assert lst.component_type == "ul"
        assert len(lst.get_property("items")) == 2

    def test_add_item(self):
        lst = List()
        lst.add_item("new item")
        assert len(lst.get_property("items")) == 1


class TestForm:
    def test_create(self):
        form = Form()
        assert form.component_type == "form"

    def test_add_field(self):
        form = Form()
        field = TextInput()
        form.add_field("username", field)
        assert "username" in form.get_property("fields")

    def test_get_data(self):
        form = Form()
        field = TextInput()
        field.set_value("john")
        form.add_field("username", field)
        data = form.get_data()
        assert data["username"] == "john"


class TestModal:
    def test_create(self):
        modal = Modal(title="Confirm")
        assert modal.get_property("title") == "Confirm"
        assert modal.get_property("open") is False

    def test_open_close(self):
        modal = Modal()
        modal.open()
        assert modal.get_property("open") is True
        modal.close()
        assert modal.get_property("open") is False


class TestComponentFactory:
    def test_register_create(self):
        ComponentFactory.register("custom", Component)
        comp = ComponentFactory.create("custom")
        assert isinstance(comp, Component)

    def test_get_registered_types(self):
        types = ComponentFactory.get_registered_types()
        assert "button" in types
        assert "input" in types
        assert "form" in types
