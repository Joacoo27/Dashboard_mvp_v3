from dataclasses import dataclass, field
from typing import Any, Callable
import importlib


Context = dict[str, Any]
ContextLoader = Callable[[], Context]
SidebarRenderer = Callable[[Context], Context]
ViewRenderer = Callable[[Context], None]


@dataclass
class TabSpec:
    key: str
    label: str
    render: ViewRenderer
    icon: str = "📊"


@dataclass
class ModuleSpec:
    key: str
    label: str
    icon: str
    sidebar_label: str | None = None
    order: int = 100
    tabs: list[TabSpec] = field(default_factory=list)
    load_context: ContextLoader | None = None
    render_sidebar: SidebarRenderer | None = None
    default_tab: str | None = None


def discover_modules(package_names: list[str]) -> dict[str, ModuleSpec]:
    modules: dict[str, ModuleSpec] = {}
    for name in package_names:
        package = importlib.import_module(name)
        spec = package.get_module()
        modules[spec.key] = spec
    return dict(sorted(modules.items(), key=lambda item: item[1].order))


def resolve_active_module(modules: dict[str, ModuleSpec], key: str | None) -> ModuleSpec:
    if key and key in modules:
        return modules[key]
    return next(iter(modules.values()))


def resolve_active_tab(module: ModuleSpec, key: str | None) -> TabSpec | None:
    if not module.tabs:
        return None

    active_key = key or module.default_tab or module.tabs[0].key
    for tab in module.tabs:
        if tab.key == active_key:
            return tab
    return module.tabs[0]
