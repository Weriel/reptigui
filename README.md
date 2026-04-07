# ReptiGUI

<style>
figcaption {
  background-color: white;
  color: grey;
  font-style: normal;
  padding: 0px;
  text-align: center;
  font-size: 10px;
}

</style>
<p align="center">
  <img src="logo.svg" alt="ReptiGUI Logo" width="400">
    <figcaption>Logo is AI generated, because I suck at drawing ✌️</figcaption>
</p>
<p align="center">

A desktop application for managing and displaying reptile husbandry information — built with [Python](https://www.python.org) and [Kivy](https://kivy.org/).


![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white) ![Kivy](https://img.shields.io/badge/Kivy-GUI-green)

## Overview

ReptiGUI is a Kivy-based GUI application that provides a clear overview of reptile care information. Animals are organized into categories, with species-specific husbandry details (temperature, humidity, diet) and a care-tracking tab for recording weight, size, age, and feeding status.

## Features

- **Category tiles** — Animals are grouped and displayed as visual tiles by category, each with a custom accent color and icon
- **Species inheritance** — Husbandry defaults are defined per species in `arten.toml` and automatically inherited by all animals of that species. Individual animals can override any field.
- **Detail view with tabs** — Each animal has an *Info* tab (husbandry notes) and a *Pflege* (Care) tab for tracking data
- **Auto-persisted care data** — Weight, size, age, and feeding status are saved automatically to `pflege.toml` on every change
- **Dark UI** — Clean dark theme with accent-colored highlights, rounded tiles, and smooth scrolling

## Current Animals

| Name    | Species              |
|---------|----------------------|
| Mochi   | Corn Snake           |
| Noodle  | Corn Snake           |
| Popcorn | Corn Snake           |
| Bibble  | Western Hognose      |
| Mu-Shu  | Gargoyle Gecko       |
| Ichigo  | Gargoyle Gecko       |

## Project Structure
```
reptigui/
├── main.py            # Application entry point & all widget logic
├── tierhaltung.kv     # Kivy styling / layout rules
├── tiere.toml         # Animal definitions (names, categories, icons)
├── arten.toml         # Species defaults (husbandry info, inherited by animals)
├── pflege.toml        # Auto-generated care tracking data
├── icons/             # Animal photos and category icons
├── pyproject.toml     # Project metadata
└── uv.lock            # Dependency lock file
```

## Getting Started

This project uses [uv](https://docs.astral.sh/uv/) for fast, hassle-free dependency management. If you don't have it yet:
```bash
# Install uv (macOS / Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or on Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then run the app:
```bash
# Clone the repository
git clone https://github.com/Weriel/reptigui.git
cd reptigui

# Sync dependencies and run (uv handles the venv automatically)
uv sync
uv run python main.py
```

The window opens at 1280×800 with the category overview. Click a category to see its animals, then click an animal to view husbandry info or log care data.

### Without uv

If you prefer not to use uv:
```bash
pip install kivy tomli_w
python main.py
```

## Requirements

- Python $\geqslant$ 3.11
- [Kivy](https://kivy.org/)
- tomli_w

## Data Configuration

### Adding a new species (`arten.toml`)
```toml
[MySpecies]
Haltung = """
Species Name (Latin name)

- Temperature: 24-28°C
- Humidity: 50-60%
- Diet: ...
"""
```

### Adding a new animal (`tiere.toml`)
```toml
[Category.AnimalName]
_icon = "icons/photo.jpeg"
_art = "MySpecies"
```

The animal automatically inherits all fields from its species. To override, just define the field directly on the animal.

## License

This project is open source. See the repository for license details.