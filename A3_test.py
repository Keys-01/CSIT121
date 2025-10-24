import os
import sys
import tempfile
import shutil
import json
import importlib.util
import unittest
from unittest.mock import patch

# Use non-interactive backend for matplotlib to avoid display issues in tests
import matplotlib
matplotlib.use("Agg")


def load_module_from_path(path, name="a3_module"):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestA3GraphSaveLoadEdit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Path to the user's active file in the workspace
        cls.module_path = "/workspaces/CSIT121/A3"
        cls.module = load_module_from_path(cls.module_path)

    def setUp(self):
        # Create a temporary working directory for file outputs and chdir into it
        self.tempdir = tempfile.mkdtemp()
        self._cwd = os.getcwd()
        os.chdir(self.tempdir)
        # fresh trainer/pokedex for each test
        self.trainer = self.module.Trainer("", "")

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self.tempdir)

    def test_graph_stats_saves_pngs(self):
        # add a few concrete pokemon to ensure stats are non-empty
        self.trainer.pokedex.Addprexisting(self.module.Bulbasaur_Pokemon())
        self.trainer.pokedex.Addprexisting(self.module.Charmander_Pokemon())
        self.trainer.pokedex.Addprexisting(self.module.Pikachu_Pokemon())

        # Call graphing method
        self.trainer.pokedex.graph_stats()

        # Expected files created by graph_stats()
        expected_files = [
            "pokemon_types_distribution.png",
            "pokemon_total_stats.png",
            "pokemon_hp_stats.png",
            "pokemon_attack_stats.png",
            "pokemon_Defense_stats.png",
            "pokemon_sp_attack_stats.png",
            "pokemon_sp_defense_stats.png",
            "pokemon_speed_stats.png",
        ]

        for fn in expected_files:
            with self.subTest(file=fn):
                self.assertTrue(os.path.exists(fn), f"{fn} should exist after graph_stats()")

    def test_load_save_file_json_loads_entries(self):
        # Create a JSON file with one pokemon entry
        test_pokemon = {
            "name": "Testmon",
            "National_number": 123,
            "Type": "Test",
            "species": "Tester",
            "Height": "1.0m",
            "Weight": "10.0kg",
            "Abilities": ["Tackle"],
            "total": 100,
            "hp": 10,
            "attack": 20,
            "Defense": 10,
            "sp_attack": 30,
            "sp_defense": 20,
            "speed": 10
        }
        filename = "test_pokemon.json"
        with open(filename, "w") as f:
            json.dump([test_pokemon], f)

        # load_save_file prompts for filename; patch input to return our filename
        with patch("builtins.input", return_value=filename):
            self.trainer.pokedex.load_save_file(filename)

        # Verify that the pokedex now has an entry with name "Testmon"
        names = [p.name for p in self.trainer.pokedex.PokemonList]
        self.assertIn("Testmon", names)

    def test_edit_special_stats_national_height_weight(self):
        # Create a simple Pokemon instance
        p = self.module.Pokemon(
            "Editmon", 1, "Normal", "Species", "1.0m", "1.0kg",
            [], 0, 10, 10, 10, 10, 10, 10
        )

        # National_number edit -> expect zero-padded string "0025"
        with patch("builtins.input", side_effect=["National_number", "25"]):
            returned = p.Edit_Pokemon()
            self.assertEqual(p.National_number, "0025")
            self.assertIs(returned, p)

        # Height edit with integer meters "10m" -> expect "10.0m"
        with patch("builtins.input", side_effect=["Height", "10m"]):
            p.Edit_Pokemon()
            self.assertEqual(p.Height, "10.0m")

        # Weight edit with integer kilograms "56kg" -> expect "56.0kg"
        with patch("builtins.input", side_effect=["Weight", "56kg"]):
            p.Edit_Pokemon()
            self.assertEqual(p.Weight, "56.0kg")


if __name__ == "__main__":
    unittest.main()