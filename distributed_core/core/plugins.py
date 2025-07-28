"""
distributed_core/plugins.py

An interface-aware, contract-enforcing plugin system.
"""

from abc import ABC
from typing import Any, Dict, List, Type, TypeVar

T = TypeVar("T")


class PluginError(Exception):
    """Base exception for plugin-related errors."""


class InterfaceNotRegisteredError(PluginError):
    """Raised when an interface is not found in the registry."""


class PluginAlreadyRegisteredError(PluginError):
    """Raised when a plugin with the same name is already registered."""


class ContractViolationError(PluginError):
    """Raised when a plugin fails to implement the interface's contract."""


class _PluginRegistry:
    """
    Manages the registration and validation of interfaces and their plugins.
    """

    def __init__(self):
        # { InterfaceClass -> \
        # {"plugins": {"name": PluginClass}, "contract": {"method1", "method2"}} }
        self._registry: Dict[Type[Any], Dict[str, Any]] = {}

    def define_interface(self, interface_class: Type[T]) -> Type[T]:
        """
        A decorator to register and define the contract for an interface.
        """
        if not issubclass(interface_class, ABC):
            raise TypeError("Interfaces must be an Abstract Base Class (ABC).")

        # Find all abstract methods to define the contract
        contract = {
            name
            for name, value in vars(interface_class).items()
            if getattr(value, "__isabstractmethod__", False)
        }

        self._registry[interface_class] = {"plugins": {}, "contract": contract}
        return interface_class

    def register_plugin(self, interface_class: Type[T], *, name: str):
        """
        A decorator to register a plugin for a given interface.
        Enforces the interface's contract upon registration.
        """
        if interface_class not in self._registry:
            raise InterfaceNotRegisteredError(
                f"Interface '{interface_class.__name__}' is not registered. "
                f"Please decorate it with @define_interface."
            )

        def decorator(plugin_class: Type[T]) -> Type[T]:
            # Check for contract violations
            contract = self._registry[interface_class]["contract"]
            implemented_methods = set(dir(plugin_class))
            missing_methods = contract - implemented_methods

            if missing_methods:
                raise ContractViolationError(
                    f"Plugin '{plugin_class.__name__}' fails to implement the "
                    f"'{interface_class.__name__}' interface. "
                    f"Missing methods: {', '.join(sorted(missing_methods))}"
                )

            plugins = self._registry[interface_class]["plugins"]
            if name in plugins:
                raise PluginAlreadyRegisteredError(
                    f"Plugin '{name}' is already registered for interface "
                    f"'{interface_class.__name__}'."
                )

            plugins[name] = plugin_class
            return plugin_class

        return decorator

    def get_plugin_class(self, interface_class: Type[T], name: str) -> Type[T]:
        """Retrieves a validated plugin class."""
        if interface_class not in self._registry:
            raise InterfaceNotRegisteredError(
                f"Interface '{interface_class.__name__}' is not registered."
            )

        plugins = self._registry[interface_class]["plugins"]
        if name not in plugins:
            available = list(plugins.keys())
            raise KeyError(
                f"Plugin '{name}' not found for interface '{interface_class.__name__}'. "
                f"Available plugins: {available}"
            )
        return plugins[name]

    def get_available_plugins(self, interface_class: Type[T]) -> List[str]:
        """Returns a list of available plugin names for an interface."""
        if interface_class not in self._registry:
            raise InterfaceNotRegisteredError(
                f"Interface '{interface_class.__name__}' is not registered."
            )
        return list(self._registry[interface_class]["plugins"].keys())


# --- Public API ---

_registry = _PluginRegistry()

define_interface = _registry.define_interface
register_plugin = _registry.register_plugin


class PluginFactory:
    """A factory for creating instances of registered plugins."""

    @staticmethod
    def get(interface_class: Type[T], name: str, *args: Any, **kwargs: Any) -> T:
        """
        Gets an instance of the specified plugin for the given interface.
        """
        plugin_class = _registry.get_plugin_class(interface_class, name)
        return plugin_class(*args, **kwargs)

    @staticmethod
    def get_available(interface_class: Type[T]) -> List[str]:
        """
        Gets the names of all available plugins for a given interface.
        """
        return _registry.get_available_plugins(interface_class)
