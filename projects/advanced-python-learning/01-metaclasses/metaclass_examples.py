"""
Advanced Metaclass Examples
Demonstrates practical metaclass patterns for real-world scenarios.
"""

from typing import Any, Dict, Type
from collections import OrderedDict


# Example 1: Singleton Metaclass
class SingletonMeta(type):
    """Ensures only one instance of a class exists."""

    _instances: Dict[Type, Any] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Database(metaclass=SingletonMeta):
    """Singleton database connection."""

    def __init__(self) -> None:
        self.connection = "Connected to DB"
        print(f"Database initialized: {id(self)}")


# Example 2: Auto-Registration Plugin System
class PluginRegistry(type):
    """Automatically registers all plugin classes."""

    plugins: Dict[str, Type] = {}

    def __new__(
        mcs, name: str, bases: tuple, attrs: Dict[str, Any]
    ) -> Type:
        cls = super().__new__(mcs, name, bases, attrs)

        # Don't register the base Plugin class itself
        if name != "Plugin" and any(
            isinstance(base, PluginRegistry) for base in bases
        ):
            mcs.plugins[name] = cls
            print(f"Registered plugin: {name}")

        return cls


class Plugin(metaclass=PluginRegistry):
    """Base plugin class."""

    def process(self) -> str:
        raise NotImplementedError


class ImagePlugin(Plugin):
    """Plugin for image processing."""

    def process(self) -> str:
        return "Processing image"


class VideoPlugin(Plugin):
    """Plugin for video processing."""

    def process(self) -> str:
        return "Processing video"


class AudioPlugin(Plugin):
    """Plugin for audio processing."""

    def process(self) -> str:
        return "Processing audio"


# Example 3: Validated Classes
class ValidatedMeta(type):
    """Validates that classes have required attributes and proper documentation."""

    def __new__(
        mcs, name: str, bases: tuple, attrs: Dict[str, Any]
    ) -> Type:
        # Skip validation for base class
        if name != "ValidatedBase":
            # Require 'required_field' attribute
            if "required_field" not in attrs:
                raise TypeError(
                    f"Class {name} must define 'required_field' attribute"
                )

            # Require docstrings on public methods
            for attr_name, attr_value in attrs.items():
                if (
                    callable(attr_value)
                    and not attr_name.startswith("_")
                    and not attr_value.__doc__
                ):
                    raise TypeError(
                        f"Method '{attr_name}' in class '{name}' must have a docstring"
                    )

        return super().__new__(mcs, name, bases, attrs)


class ValidatedBase(metaclass=ValidatedMeta):
    """Base class for validated classes."""

    pass


class DataProcessor(ValidatedBase):
    """Processes data with validation."""

    required_field = "processor"

    def process(self) -> str:
        """Process the data."""
        return "Processing data"


# Example 4: Ordered Attributes Metaclass
class OrderedMeta(type):
    """Preserves the order of class attribute definition."""

    @classmethod
    def __prepare__(
        mcs, name: str, bases: tuple, **kwargs: Any
    ) -> OrderedDict:
        """Return OrderedDict to preserve attribute order."""
        return OrderedDict()

    def __new__(
        mcs, name: str, bases: tuple, attrs: OrderedDict
    ) -> Type:
        cls = super().__new__(mcs, name, bases, dict(attrs))
        # Store the order of field definitions
        cls._field_order = [
            key
            for key in attrs.keys()
            if not key.startswith("__")
        ]
        return cls


class Schema(metaclass=OrderedMeta):
    """Schema with ordered fields."""

    id = int
    name = str
    email = str
    age = int
    created_at = str


# Example 5: ORM-Style Model with Field Validation
class Field:
    """Descriptor for typed fields with validation."""

    def __init__(self, field_type: Type, default: Any = None) -> None:
        self.field_type = field_type
        self.default = default
        self.name: str = ""

    def __set_name__(self, owner: Type, name: str) -> None:
        self.name = name

    def __get__(self, obj: Any, objtype: Type = None) -> Any:
        if obj is None:
            return self
        return obj.__dict__.get(self.name, self.default)

    def __set__(self, obj: Any, value: Any) -> None:
        if not isinstance(value, self.field_type):
            raise TypeError(
                f"Field '{self.name}' must be of type {self.field_type.__name__}, "
                f"got {type(value).__name__}"
            )
        obj.__dict__[self.name] = value


class ModelMeta(type):
    """Metaclass for ORM-style models."""

    def __new__(
        mcs, name: str, bases: tuple, attrs: Dict[str, Any]
    ) -> Type:
        # Collect all Field instances
        fields: Dict[str, Field] = {}
        for key, value in list(attrs.items()):
            if isinstance(value, Field):
                fields[key] = value

        cls = super().__new__(mcs, name, bases, attrs)
        cls._fields = fields
        return cls

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """Custom instantiation with field validation."""
        instance = super().__call__()

        # Initialize fields with defaults
        for field_name, field in cls._fields.items():
            if field_name in kwargs:
                setattr(instance, field_name, kwargs[field_name])
            elif field.default is not None:
                setattr(instance, field_name, field.default)

        return instance


class Model(metaclass=ModelMeta):
    """Base model class."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            name: getattr(self, name)
            for name in self._fields
            if hasattr(self, name)
        }


class User(Model):
    """User model with typed fields."""

    name = Field(str)
    age = Field(int)
    email = Field(str)
    active = Field(bool, default=True)


# Example 6: Method Interception Metaclass
class InterceptMeta(type):
    """Intercepts all method calls for logging/debugging."""

    def __new__(
        mcs, name: str, bases: tuple, attrs: Dict[str, Any]
    ) -> Type:
        # Wrap all callable attributes
        for attr_name, attr_value in attrs.items():
            if callable(attr_value) and not attr_name.startswith("__"):
                attrs[attr_name] = mcs._wrap_method(
                    attr_name, attr_value
                )

        return super().__new__(mcs, name, bases, attrs)

    @staticmethod
    def _wrap_method(name: str, method: callable) -> callable:
        """Wrap a method with logging."""

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            print(f"[CALL] {name}(args={args[1:]}, kwargs={kwargs})")
            result = method(*args, **kwargs)
            print(f"[RETURN] {name} -> {result}")
            return result

        return wrapper


class Calculator(metaclass=InterceptMeta):
    """Calculator with intercepted methods."""

    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    def multiply(self, a: int, b: int) -> int:
        """Multiply two numbers."""
        return a * b


def demo() -> None:
    """Demonstrate all metaclass examples."""
    print("=" * 60)
    print("METACLASS EXAMPLES DEMONSTRATION")
    print("=" * 60)

    # Demo 1: Singleton
    print("\n1. Singleton Pattern:")
    db1 = Database()
    db2 = Database()
    print(f"db1 is db2: {db1 is db2}")

    # Demo 2: Plugin Registry
    print("\n2. Plugin Registry:")
    print(f"Registered plugins: {list(PluginRegistry.plugins.keys())}")
    for plugin_name, plugin_class in PluginRegistry.plugins.items():
        plugin = plugin_class()
        print(f"  {plugin_name}: {plugin.process()}")

    # Demo 3: Validated Classes
    print("\n3. Validated Classes:")
    processor = DataProcessor()
    print(f"Processor field: {processor.required_field}")

    # Demo 4: Ordered Attributes
    print("\n4. Ordered Attributes:")
    print(f"Schema field order: {Schema._field_order}")

    # Demo 5: ORM-Style Model
    print("\n5. ORM-Style Model:")
    user = User(name="Alice", age=30, email="alice@example.com")
    print(f"User data: {user.to_dict()}")

    # Demo 6: Method Interception
    print("\n6. Method Interception:")
    calc = Calculator()
    result = calc.add(5, 3)
    result = calc.multiply(4, 7)


if __name__ == "__main__":
    demo()
