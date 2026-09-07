# UI Component Library — Reusable Components with Factory Pattern

A lightweight, extensible UI component library with a factory pattern for creating reusable interface elements.

## Features

- **Component Factory** — Register and create components by type
- **Built-in Components** — Button, Card, List, Form, Modal, Table
- **Event System** — Click, change, submit, open/close events
- **Serialization** — Full to_dict/from_dict support
- **Zero Dependencies** — Pure Python 3.11+

## Quick Start

```python
from ui_components.factory import ComponentFactory
from ui_components.button import Button
from ui_components.card import Card

factory = ComponentFactory()
factory.register("button", Button)
factory.register("card", Card)

btn = factory.create("button", text="Click Me", variant="primary")
card = factory.create("card", title="Grid Status", content="All systems nominal")

# Events
btn.on("click", lambda c, **kw: print(f"Clicked: {c.text}"))
btn.trigger("click")
```

## Tests

```bash
pytest tests/ -v
```

## License

MIT
