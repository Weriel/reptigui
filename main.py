"""Tierhaltung Info – Kivy-Anwendung zur Anzeige von Tierhaltungsinformationen."""

import os
os.environ["KIVY_NO_CONSOLELOG"] = "1"

from pathlib import Path

import tomllib
import tomli_w

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty, BooleanProperty, NumericProperty

# ─── Fenstergröße ─────────────────────────────────────────────────────────────
Window.size = (1280, 800)
Window.clearcolor = (0.059, 0.071, 0.098, 1)

# ─── Pfade ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "tiere.toml"
PFLEGE_PATH = BASE_DIR / "pflege.toml"
KV_PATH = BASE_DIR / "tierhaltung.kv"

# ─── Daten laden ──────────────────────────────────────────────────────────────
with open(DATA_PATH, "rb") as f:
    DATA = tomllib.load(f)

for cat in DATA.values():
    if "_color" in cat:
        r, g, b = cat["_color"]
        cat["_color"] = [r / 255, g / 255, b / 255, 1.0]

# ─── Pflege-Feld-Definitionen ────────────────────────────────────────────────
PFLEGE_INPUT_FIELDS = [
    {"key": "gewicht", "label": "Gewicht", "suffix": "g"},
    {"key": "groesse", "label": "Größe", "suffix": "cm"},
    {"key": "alter", "label": "Alter", "suffix": "Jahre"},
]

PFLEGE_CHECKBOXES = [
    {"key": "gefuettert", "label": "Gefüttert"},
]


# ─── Pflege-Persistenz ───────────────────────────────────────────────────────


def load_pflege() -> dict:
    if PFLEGE_PATH.exists():
        with open(PFLEGE_PATH, "rb") as f:
            return tomllib.load(f)
    return {}


def save_pflege(data: dict) -> None:
    with open(PFLEGE_PATH, "wb") as f:
        tomli_w.dump(data, f)


def get_pflege_entry(pflege_data: dict, cat_key: str, animal_key: str) -> dict:
    entry = pflege_data.setdefault(cat_key, {}).setdefault(animal_key, {})
    for field in PFLEGE_INPUT_FIELDS:
        entry.setdefault(field["key"], "")
    for cb in PFLEGE_CHECKBOXES:
        entry.setdefault(cb["key"], False)
    return entry


def animal_keys(category: dict) -> list[str]:
    return [k for k in category if not k.startswith("_")]


# ─── Widget-Klassen (gestylt via .kv) ────────────────────────────────────────
# Diese Klassen werden in Python instanziiert. Das Styling kommt aus
# tierhaltung.kv über class-rules (<ClassName>:), die genau 1x angewendet werden.


class AppHeader(BoxLayout):
    title = StringProperty("")
    accent_color = ListProperty([0.902, 0.922, 0.961, 1])
    show_back = BooleanProperty(False)
    header_icon = StringProperty("")
    is_header_image = BooleanProperty(False)

    def on_header_icon(self, _instance, value: str) -> None:
        self.is_header_image = value.endswith((".png", ".jpg", ".jpeg", ".webp"))


class Tile(ButtonBehavior, BoxLayout):
    tile_name = StringProperty("")
    tile_icon = StringProperty("?")
    tile_subtitle = StringProperty("")
    accent_color = ListProperty([1, 1, 1, 1])
    is_image = BooleanProperty(False)
    tile_height = NumericProperty(dp(150))

    def on_tile_icon(self, _instance, value: str) -> None:
        self.is_image = value.endswith((".png", ".jpg", ".jpeg", ".webp"))


class TabButton(ToggleButton):
    accent_color = ListProperty([1, 1, 1, 1])


class PflegeInput(BoxLayout):
    field_label = StringProperty("")
    field_suffix = StringProperty("")
    field_key = StringProperty("")


class PflegeCheckbox(BoxLayout):
    cb_label = StringProperty("")
    cb_key = StringProperty("")
    accent_color = ListProperty([1, 1, 1, 1])


# ─── Root-Widget ──────────────────────────────────────────────────────────────


class RootWidget(BoxLayout):
    """Container der die gesamte App hält."""

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.nav_stack: list[tuple[str, object]] = []

    def show_screen(self, screen_type: str, key: object = None) -> None:
        self.nav_stack.append((screen_type, key))
        self._rebuild()

    def go_back(self) -> None:
        if len(self.nav_stack) > 1:
            self.nav_stack.pop()
            self._rebuild()

    def _rebuild(self) -> None:
        self.clear_widgets()
        screen_type, key = self.nav_stack[-1]

        if screen_type == "main":
            self._build_main()
        elif screen_type == "category":
            self._build_category(key)
        elif screen_type == "detail":
            self._build_detail(*key)

    # ── Main ──────────────────────────────────────────────────────────────────

    def _build_main(self) -> None:
        self.add_widget(AppHeader(title="Tierhaltung", show_back=False))

        categories = list(DATA.keys())
        scroll = ScrollView(size_hint=(1, 1))
        grid = GridLayout(
            cols=min(len(categories), 3),
            spacing=dp(20),
            padding=[dp(24), dp(20), dp(24), dp(20)],
            size_hint_y=None,
        )
        grid.bind(minimum_height=grid.setter("height"))

        for name in categories:
            cat = DATA[name]
            n = len(animal_keys(cat))
            tile = Tile(
                tile_name=name,
                tile_icon=cat.get("_icon", "?"),
                tile_subtitle=f"{n} Tiere",
                accent_color=cat["_color"],
                tile_height=dp(300),
            )
            tile.bind(on_release=lambda _, n=name: self.show_screen("category", n))
            grid.add_widget(tile)

        scroll.add_widget(grid)
        self.add_widget(scroll)

    # ── Kategorie ─────────────────────────────────────────────────────────────

    def _build_category(self, cat_key: str) -> None:
        cat = DATA[cat_key]
        accent = cat["_color"]
        self.add_widget(AppHeader(title=cat_key, accent_color=accent, show_back=True))

        animals = animal_keys(cat)
        scroll = ScrollView(size_hint=(1, 1))
        grid = GridLayout(
            cols=min(len(animals), 4),
            spacing=dp(20),
            padding=[dp(24), dp(20), dp(24), dp(20)],
            size_hint_y=None,
        )
        grid.bind(minimum_height=grid.setter("height"))

        for name in animals:
            icon = cat[name].get("_icon", "?")
            tile = Tile(tile_name=name, tile_icon=icon, accent_color=accent, tile_height=dp(180))
            tile.bind(
                on_release=lambda _, n=name: self.show_screen("detail", (cat_key, n))
            )
            grid.add_widget(tile)

        scroll.add_widget(grid)
        self.add_widget(scroll)

    # ── Detail ────────────────────────────────────────────────────────────────

    def _build_detail(self, cat_key: str, animal_key: str) -> None:
        cat = DATA[cat_key]
        animal = cat[animal_key]
        accent = cat["_color"]
        icon = animal.get("_icon", "?")

        is_img = icon.endswith((".png", ".jpg", ".jpeg", ".webp"))
        header = AppHeader(
            title=animal_key if is_img else f"{icon}  {animal_key}",
            accent_color=accent,
            show_back=True,
            header_icon=icon if is_img else "",
        )
        self.add_widget(header)

        # Tab-Bar
        tab_bar = BoxLayout(
            size_hint_y=None, height=dp(48),
            padding=[dp(24), dp(6), dp(24), dp(6)], spacing=dp(10),
        )
        tab_info = TabButton(text="Info", group="detail_tabs", state="down", accent_color=accent)
        tab_pflege = TabButton(text="Pflege", group="detail_tabs", accent_color=accent)

        content = BoxLayout(orientation="vertical")
        self._detail_content = content
        self._detail_cat = cat_key
        self._detail_animal = animal_key
        self._detail_accent = accent

        tab_info.bind(on_release=lambda *_: self._show_info_tab())
        tab_pflege.bind(on_release=lambda *_: self._show_pflege_tab())

        tab_bar.add_widget(tab_info)
        tab_bar.add_widget(tab_pflege)
        tab_bar.add_widget(Widget())
        self.add_widget(tab_bar)
        self.add_widget(content)

        self._show_info_tab()

    def _show_info_tab(self) -> None:
        content = self._detail_content
        content.clear_widgets()

        animal = DATA[self._detail_cat][self._detail_animal]
        text = animal.get("Haltung", "Kein Text vorhanden.")

        scroll = ScrollView(size_hint=(1, 1), bar_color=self._detail_accent)
        panel = BoxLayout(
            orientation="vertical", size_hint_y=None,
            padding=[dp(30), dp(20), dp(30), dp(20)],
        )
        panel.bind(minimum_height=panel.setter("height"))

        lbl = Label(
            text=text,
            font_size=dp(17),
            color=(0.902, 0.922, 0.961, 1),
            size_hint_y=None,
            halign="left", valign="top",
        )
        lbl.bind(size=lambda *_: setattr(lbl, "text_size", (lbl.width, None)))
        lbl.bind(texture_size=lambda *_: setattr(lbl, "height", lbl.texture_size[1]))
        panel.add_widget(lbl)

        scroll.add_widget(panel)
        content.add_widget(scroll)

    def _show_pflege_tab(self) -> None:
        content = self._detail_content
        content.clear_widgets()
        accent = self._detail_accent
        cat_key = self._detail_cat
        animal_key = self._detail_animal

        app = App.get_running_app()
        entry = get_pflege_entry(app.pflege_data, cat_key, animal_key)

        scroll = ScrollView(size_hint=(1, 1), bar_color=accent)
        panel = BoxLayout(
            orientation="vertical", size_hint_y=None,
            padding=[dp(30), dp(20), dp(30), dp(20)],
            spacing=dp(10),
        )
        panel.bind(minimum_height=panel.setter("height"))

        # Titel
        title = Label(
            text="Pflegedaten",
            font_size=dp(24), bold=True, color=accent,
            size_hint_y=None, height=dp(36),
            halign="left", valign="center",
        )
        title.bind(size=lambda *_: setattr(title, "text_size", (title.width, None)))
        panel.add_widget(title)

        hint = Label(
            text="Änderungen werden automatisch gespeichert",
            font_size=dp(14),
            color=(0.549, 0.588, 0.667, 1),
            size_hint_y=None, height=dp(24),
            halign="left", valign="top",
        )
        hint.bind(size=lambda *_: setattr(hint, "text_size", (hint.width, None)))
        panel.add_widget(hint)

        panel.add_widget(Widget(size_hint_y=None, height=dp(10)))

        # Inputfelder
        for field in PFLEGE_INPUT_FIELDS:
            row = PflegeInput(
                field_label=field["label"],
                field_suffix=field["suffix"],
                field_key=field["key"],
            )
            # Text nach dem nächsten Frame setzen (ids sind erst nach KV-apply verfügbar)
            stored_val = str(entry.get(field["key"], ""))
            fkey = field["key"]

            def _bind_input(widget, val=stored_val, key=fkey):
                from kivy.clock import Clock
                def _init(_dt):
                    widget.ids.tinput.text = val
                    widget.ids.tinput.bind(
                        text=lambda _inst, v, k=key: self._on_pflege_input(cat_key, animal_key, k, v)
                    )
                Clock.schedule_once(_init, 0)

            _bind_input(row)
            panel.add_widget(row)

        panel.add_widget(Widget(size_hint_y=None, height=dp(10)))

        # Checkboxen
        for cb_def in PFLEGE_CHECKBOXES:
            row = PflegeCheckbox(
                cb_label=cb_def["label"],
                cb_key=cb_def["key"],
                accent_color=accent,
            )
            stored_active = bool(entry.get(cb_def["key"], False))
            ckey = cb_def["key"]

            def _bind_cb(widget, active=stored_active, key=ckey):
                from kivy.clock import Clock
                def _init(_dt):
                    widget.ids.cb.active = active
                    widget.ids.cb.bind(
                        active=lambda _inst, v, k=key: self._on_pflege_checkbox(cat_key, animal_key, k, v)
                    )
                Clock.schedule_once(_init, 0)

            _bind_cb(row)
            panel.add_widget(row)

        panel.add_widget(Widget(size_hint_y=None, height=dp(40)))

        scroll.add_widget(panel)
        content.add_widget(scroll)

    def _on_pflege_input(self, cat_key: str, animal_key: str, field_key: str, value: str) -> None:
        app = App.get_running_app()
        entry = get_pflege_entry(app.pflege_data, cat_key, animal_key)
        entry[field_key] = value
        save_pflege(app.pflege_data)

    def _on_pflege_checkbox(self, cat_key: str, animal_key: str, field_key: str, value: bool) -> None:
        app = App.get_running_app()
        entry = get_pflege_entry(app.pflege_data, cat_key, animal_key)
        entry[field_key] = value
        save_pflege(app.pflege_data)


# ─── App ──────────────────────────────────────────────────────────────────────


class TierhaltungApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pflege_data = load_pflege()

    def build(self):
        # KV wird automatisch geladen: Kivy sucht "tierhaltung.kv" für "TierhaltungApp"
        # NICHT manuell laden, sonst werden alle Rules doppelt angewendet!
        root = RootWidget()
        self._root = root
        root.show_screen("main")
        return root

    def go_back(self) -> None:
        self._root.go_back()


if __name__ == "__main__":
    TierhaltungApp().run()