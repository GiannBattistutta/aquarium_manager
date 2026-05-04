"""Simple aquarium manager using a JSON file for persistence."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass
class Fish:
    name: str
    species: str
    quantity: int


@dataclass
class Equipment:
    name: str
    status: str


DEFAULT_DATA: dict[str, Any] = {
    "aquarium_name": "My Aquarium",
    "volume_liters": 100,
    "water": {
        "temperature_c": 25.0,
        "ph": 7.2,
        "salinity_ppt": 0.0,
    },
    "fish": [],
    "equipment": [],
    "maintenance_log": [],
}


class AquariumManager:
    def __init__(self, json_path: str | Path):
        self.path = Path(json_path)
        self.data = self._load_or_initialize()

    def _load_or_initialize(self) -> dict[str, Any]:
        if not self.path.exists():
            self._save(DEFAULT_DATA)
            return DEFAULT_DATA.copy()

        with self.path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: dict[str, Any] | None = None) -> None:
        payload = data if data is not None else self.data
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def add_fish(self, fish: Fish) -> None:
        self.data["fish"].append(asdict(fish))
        self._save()

    def add_equipment(self, equipment: Equipment) -> None:
        self.data["equipment"].append(asdict(equipment))
        self._save()

    def update_water(self, temperature_c: float | None, ph: float | None, salinity_ppt: float | None) -> None:
        if temperature_c is not None:
            self.data["water"]["temperature_c"] = temperature_c
        if ph is not None:
            self.data["water"]["ph"] = ph
        if salinity_ppt is not None:
            self.data["water"]["salinity_ppt"] = salinity_ppt
        self._save()

    def log_maintenance(self, note: str) -> None:
        self.data["maintenance_log"].append(note)
        self._save()

    def show(self) -> str:
        return json.dumps(self.data, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage an aquarium with a JSON file")
    parser.add_argument("--file", default="aquarium.json", help="Path to aquarium JSON file")

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_fish = subparsers.add_parser("add-fish", help="Add fish")
    add_fish.add_argument("name")
    add_fish.add_argument("species")
    add_fish.add_argument("quantity", type=int)

    add_equipment = subparsers.add_parser("add-equipment", help="Add equipment")
    add_equipment.add_argument("name")
    add_equipment.add_argument("status", choices=["on", "off", "maintenance"])

    update_water = subparsers.add_parser("update-water", help="Update water parameters")
    update_water.add_argument("--temperature", type=float)
    update_water.add_argument("--ph", type=float)
    update_water.add_argument("--salinity", type=float)

    maintenance = subparsers.add_parser("log", help="Add maintenance log entry")
    maintenance.add_argument("note")

    subparsers.add_parser("show", help="Print current aquarium data")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    manager = AquariumManager(args.file)

    if args.command == "add-fish":
        manager.add_fish(Fish(args.name, args.species, args.quantity))
    elif args.command == "add-equipment":
        manager.add_equipment(Equipment(args.name, args.status))
    elif args.command == "update-water":
        manager.update_water(args.temperature, args.ph, args.salinity)
    elif args.command == "log":
        manager.log_maintenance(args.note)
    elif args.command == "show":
        print(manager.show())


if __name__ == "__main__":
    main()