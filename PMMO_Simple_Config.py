import flet as ft
from time import sleep
import re
from pathlib import Path
from os import remove, makedirs
from shutil import copyfile, rmtree
import json


class NotSaveFolder(Exception):
    def __init__(self, error_message: str) -> None:
        self.msg = error_message

class ForceExit(Exception):
    def __init__(self, error_message: str) -> None:
        self.msg = error_message


class SimpleSettings(ft.UserControl):
    def __init__(self):
        super().__init__()
        # Pre-compiled Regex
        self.integer_re = re.compile(r'^(?:[1-9]\d|100|[1-9])$')
        self.float_re = re.compile(r'^\d*(?:\.\d*)?$')
        self.requirements_re = re.compile(r'^(?P<pre_whitespace>\s*)(?P<option>"\S+ Req Enabled" = )(?:true|false)\s*$', flags=re.IGNORECASE)
        self.anticheese_re = re.compile(r'\[AntiCheese(?:\.AFK|\.DiminishingXP|\.Normalization)?\]')
        self.monster_buffs_re = re.compile(r'^(?P<pre_whitespace>\s*)(?P<option>"Enable Mob Scaling" = )(?:true|false)\s*$', flags=re.IGNORECASE)
        self.xp_loss_on_death_re = re.compile(r'^(?P<pre_whitespace>\s*)(?P<option>"Loss on death" = )(?P<value>\d*(?:\.\d*)?)\s*$', flags=re.IGNORECASE)
        self.xp_multiplier_re = re.compile(r'^(?P<pre_whitespace>\s*)(?P<option>"Global Modifier" = )(?P<value>\d*(?:\.\d*)?)\s*$', flags=re.IGNORECASE)
        self.veinminer_re = re.compile(r'^(?P<pre_whitespace>\s*)(?P<option>"vein enabled" = )(?:true|false)\s*$', flags=re.IGNORECASE)

        self.cwd = None

        # Datapack JSON
        self.biome_block = {
            "pack": {
                "description": "Remove biomes - Project MMO Basic Settings",
                "pack_format": 9
            },
            "filter": {
                "block": [
                    {"namespace": "minecraft","path": "pmmo/biomes/badlands.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/bamboo_jungle.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/basalt_deltas.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/beach.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/birch_forest.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/cold_ocean.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/crimson_forest.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/dark_forest.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/deep_cold_ocean.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/deep_frozen_ocean.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/deep_lukewarm_ocean.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/deep_ocean.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/desert.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/dripstone_caves.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/end_barrens.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/end_highlands.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/end_midlands.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/eroded_badlands.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/flower_forest.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/forest.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/frozen_ocean.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/frozen_peaks.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/frozen_river.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/grove.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/ice_spikes.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/jagged_peaks.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/jungle.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/lukewarm_ocean.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/lush_caves.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/meadow.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/mushroom_fields.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/nether_wastes.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/ocean.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/old_growth_birch_forest.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/old_growth_pine_taiga.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/old_growth_spruce_taiga.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/plains.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/river.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/savanna.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/savanna_plateau.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/small_end_islands.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/snowy_beach.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/snowy_plains.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/snowy_slopes.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/snowy_taiga.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/soul_sand_valley.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/sparse_jungle.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/stony_peaks.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/stony_shore.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/sunflower_plains.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/swamp.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/taiga.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/the_end.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/the_void.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/warm_ocean.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/warped_forest.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/windswept_forest.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/windswept_gravelly_hills.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/windswept_hills.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/windswept_savanna.json"},
                    {"namespace": "minecraft","path": "pmmo/biomes/wooded_badlands.json"}
                ]
            }
        }
        self.dimension_block = {
            "pack": {
                "description": "Remove dimensions - Project MMO Basic Settings",
                "pack_format": 9
            },
            "filter": {
                "block": [
                    {"namespace": "minecraft","path": "pmmo/dimensions/overworld.json"},
                    {"namespace": "minecraft","path": "pmmo/dimensions/the_end.json"},
                    {"namespace": "minecraft","path": "pmmo/dimensions/the_nether.json"}
                ]
            }
        }

    def build(self) -> ft.Column:

        # Folder location
        self.get_directory_dialog = ft.FilePicker(on_result=self.check_folder_event)
        self.check_path_button = ft.ElevatedButton(
            text="Open Save Folder",
            icon=ft.icons.FOLDER_OPEN,
            on_click=lambda _: self.get_directory_dialog.get_directory_path(),
        )
        self.directory_path = ft.Text()

        # Settings
        self.requirements_checkbox = ft.Checkbox(label="Requirements (to wear armor, use tools, etc)", value=True, on_change=self.update_requirements)
        self.veinminer_checkbox = ft.Checkbox(label="Vein-Miner", value=True, on_change=self.update_veinminer)
        self.anticheese_checkbox = ft.Checkbox(label="Anti-Cheese (makes some xp gains reduce over time)", value=True, on_change=self.update_anticheese)
        self.biome_modifiers_checkbox = ft.Checkbox(label="Biome Modifiers", value=True, on_change=self.update_biome_effects)
        self.dimension_modifiers_checkbox = ft.Checkbox(label="Dimension Modifiers", value=True, on_change=self.update_dimension_effects)
        self.speed_perk_checkbox = ft.Checkbox(label="Speed Effect Perk", value=True, on_change=self.update_speed_perk)
        self.night_vision_perk_checkbox = ft.Checkbox(label="Night Vision Effect Perk", value=True, on_change=self.update_night_vision_perk)
        self.perks_checkbox = ft.Checkbox(label="Perks (disable/enable all perks)", value=True, on_change=self.update_perks)
        self.monster_buffs_checkbox = ft.Checkbox(label="Buff Mobs", value=True, on_change=self.update_monster_buffs)
        self.lose_xp_on_death_checkbox = ft.Checkbox(label="Lose XP on Death?", value=True, on_change=self.update_lose_xp_on_death)
        self.lose_xp_on_death_textfield = ft.TextField(label="Amount To Lose?", value="5", suffix_text="%", max_length=3, on_change=self.update_lose_xp_on_death, keyboard_type=ft.KeyboardType.NUMBER)
        self.xp_multiplier_textfield = ft.TextField(label="XP Multiplier", value="1", suffix_text="X", max_length=10, on_change=self.update_xp_multiplier, keyboard_type=ft.KeyboardType.NUMBER)
        self.restore_defaults_button = ft.ElevatedButton(text="Restore Defaults", on_click=self.restore_defaults)
        self.dialogue = ft.AlertDialog(title=ft.Text(""))

        self.settings = ft.Column(
            width=400,
            controls=[
                self.requirements_checkbox,
                self.anticheese_checkbox,
                self.perks_checkbox,
                ft.Row(
                    controls=[
                        self.speed_perk_checkbox,
                        self.night_vision_perk_checkbox,
                    ]
                ),
                ft.Row(
                    controls=[
                        self.monster_buffs_checkbox,
                        self.veinminer_checkbox,
                    ]
                ),
                self.xp_multiplier_textfield,
                self.lose_xp_on_death_checkbox,
                self.lose_xp_on_death_textfield,
                ft.Row(
                    controls=[
                        self.biome_modifiers_checkbox,
                        self.dimension_modifiers_checkbox,
                    ]
                ),
                self.restore_defaults_button,
            ]
        )
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        self.check_path_button,
                        self.directory_path,
                    ]
                ),
                ft.Divider(),
                self.settings,
                self.dialogue,
            ],
        )

    def wait_for_cwd(self) -> bool:
        for i in range(0, 20):
            if self.cwd is None:
                sleep(i / 10)
                continue
            return True
        self.dialogue.title = ft.Text("Can't open `serverconfig/pmmo-server.toml`!")
        self.dialogue.open = True
        self.update()
        sleep(5)
        self.dialogue.open = False
        self.dialogue.title = ""
        self.update()
        return False

    def process_defaults(self) -> None:
        self.requirements_checkbox.value = self.get_requirements()
        self.anticheese_checkbox.value = self.get_anticheese()
        self.perks_checkbox.value = self.get_perks()
        self.speed_perk_checkbox.disabled = not self.get_perks()
        self.speed_perk_checkbox.value = self.get_speed_perk()
        self.night_vision_perk_checkbox.disabled = not self.get_perks()
        self.night_vision_perk_checkbox.value = self.get_night_vision_perk()
        self.monster_buffs_checkbox.value = self.get_monster_buffs()
        lose_xp_on_death_value = float(self.get_xp_loss_on_death())
        if not float(self.lose_xp_on_death_textfield.value) == lose_xp_on_death_value:
            if lose_xp_on_death_value == 0.0:
                self.lose_xp_on_death_textfield.disabled = True
            else:
                self.lose_xp_on_death_textfield.disabled = False
            self.lose_xp_on_death_textfield.value = int(lose_xp_on_death_value * 100)
            self.lose_xp_on_death_checkbox.value = False if lose_xp_on_death_value == 0.0 else True
        xp_multiplier = self.get_xp_multiplier()
        if not float(self.xp_multiplier_textfield.value) == float(xp_multiplier):
            self.xp_multiplier_textfield.value = self.get_xp_multiplier()
        self.biome_modifiers_checkbox.value = self.get_biome_datapack()
        self.dimension_modifiers_checkbox.value = self.get_dimension_datapack()
        self.veinminer_checkbox.value = self.get_veinminer()
        
    def update_requirements(self, e: ft.FilePickerResultEvent) -> None:
        requirements_path = self.cwd / 'serverconfig' / 'pmmo-server.toml'
        with requirements_path.open(mode="r") as file:
            requirements = file.readlines()
        save_data = []
        line: str
        for line in requirements:
            match = self.requirements_re.match(line)
            if match:
                line = f"{match['pre_whitespace']}{match['option']}{e.data}\n"
            save_data.append(line)
        with requirements_path.open(mode="w") as file:
            file.writelines(save_data)
        self.process_defaults()
        self.update()
    
    def restore_pmmoserver(self) -> None:
        pmmoserver_path = self.cwd / 'serverconfig' / 'pmmo-server.toml'
        pmmoserver_backup_path = self.cwd / 'serverconfig' / 'pmmo-server.toml.bak'
        if not pmmoserver_backup_path.exists():
            self.dialogue.title = ft.Text("Backup 'pmmo-server.toml' missing!")
            self.dialogue.open = True
            self.update()
            self.cwd = None
            self.settings.visible = False
            sleep(5)
            self.dialogue.open = False
            self.dialogue.title = ""
            self.update()
            return
        remove(pmmoserver_path)
        copyfile(pmmoserver_backup_path, pmmoserver_path)

    def backup_pmmoserver(self) -> None:
        requirements_path = self.cwd / 'serverconfig' / 'pmmo-server.toml'
        requirements_backup_path = self.cwd / 'serverconfig' / 'pmmo-server.toml.bak'
        self.fix_pmmoserver_mob()
        if requirements_backup_path.exists():
            return
        copyfile(requirements_path, requirements_backup_path)

    def fix_pmmoserver_mob(self) -> None:
        pmmoserver_path = self.cwd / 'serverconfig' / 'pmmo-server.toml'
        with pmmoserver_path.open(mode="r") as file:
            pmmoserver = file.readlines()
        output: list = []
        fixed: bool = False
        for line in pmmoserver:
            if '[Mob_Scaling.Scaling_Settings."Mob Scaling IDs and Ratios"."minecraft:generic".max_health]' in line:
                fixed = True
                line = line.replace('[Mob_Scaling.Scaling_Settings."Mob Scaling IDs and Ratios"."minecraft:generic".max_health]', '[Mob_Scaling.Scaling_Settings."Mob Scaling IDs and Ratios"."minecraft:generic.max_health"]')
            elif '[Mob_Scaling.Scaling_Settings."Mob Scaling IDs and Ratios"."minecraft:generic".attack_damage]' in line:
                fixed = True
                line = line.replace('[Mob_Scaling.Scaling_Settings."Mob Scaling IDs and Ratios"."minecraft:generic".attack_damage]', '[Mob_Scaling.Scaling_Settings."Mob Scaling IDs and Ratios"."minecraft:generic.attack_damage"]')
            elif '[Mob_Scaling.Scaling_Settings."Mob Scaling IDs and Ratios"."minecraft:generic".movement_speed]' in line:
                fixed = True
                line = line.replace('[Mob_Scaling.Scaling_Settings."Mob Scaling IDs and Ratios"."minecraft:generic".movement_speed]', '[Mob_Scaling.Scaling_Settings."Mob Scaling IDs and Ratios"."minecraft:generic.movement_speed"]')
            output.append(line)
        if not fixed:
            return
        with pmmoserver_path.open(mode="w") as file:
            file.writelines(output)    
        
    def get_requirements(self) -> bool:
        self.backup_pmmoserver()
        requirements_path = self.cwd / 'serverconfig' / 'pmmo-server.toml'
        line: str
        with requirements_path.open(mode="r") as file:
            while ( line := file.readline() ):
                if not self.requirements_re.match(line):
                    continue
                if line.strip().endswith("true"):
                    return True
                else:
                    return False
        self.dialogue.title = ft.Text("'pmmo-server.toml' is corrupt or missing values (requirements). Attempting to restore...")
        self.dialogue.open = True
        self.update()
        sleep(5)
        self.dialogue.open = False
        self.dialogue.title = ""
        self.update()
        self.restore_pmmoserver()
        return False
    
    def update_veinminer(self, e) -> None:
        requirements_path = self.cwd / 'serverconfig' / 'pmmo-server.toml'
        with requirements_path.open(mode="r") as file:
            requirements = file.readlines()
        save_data = []
        line: str
        for line in requirements:
            match = self.veinminer_re.match(line)
            if match:
                line = f"{match['pre_whitespace']}{match['option']}{e.data}\n"
            save_data.append(line)
        with requirements_path.open(mode="w") as file:
            file.writelines(save_data)
        self.process_defaults()
        self.update()

    def get_veinminer(self) -> bool:
        self.backup_pmmoserver()
        requirements_path = self.cwd / 'serverconfig' / 'pmmo-server.toml'
        line: str
        with requirements_path.open(mode="r") as file:
            while ( line := file.readline() ):
                if not self.veinminer_re.match(line):
                    continue
                if line.strip().endswith("true"):
                    return True
        return False

    def update_anticheese(self, e) -> None:
        anticheese_path = self.cwd / 'serverconfig' / 'pmmo-AntiCheese.toml'
        if e.data == "true":
            self.restore_anticheese()
            return
        with anticheese_path.open(mode="r") as file:
            anticheese = file.readlines()
        save_data = []
        line: str
        for line in anticheese:
            if self.anticheese_re.search(line): # Required lines
                save_data.append(line)
                continue
            elif line.startswith("#") and not line.startswith("# edited by Project MMO Basic Settings "): # Comments
                save_data.append(line)
                continue
            elif not line.strip(): # Empty lines
                save_data.append(line)
                continue
        with anticheese_path.open(mode="w") as file:
            file.writelines(save_data)
        self.process_defaults()
        self.update()

    def backup_anticheese(self) -> None:
        anticheese_path = self.cwd / 'serverconfig' / 'pmmo-AntiCheese.toml'
        anticheese_backup_path = self.cwd / 'serverconfig' / 'pmmo-AntiCheese.toml.bak'
        if anticheese_backup_path.exists():
            return
        copyfile(anticheese_path, anticheese_backup_path)
    
    def restore_anticheese(self) -> None:
        anticheese_path = self.cwd / 'serverconfig' / 'pmmo-AntiCheese.toml'
        anticheese_backup_path = self.cwd / 'serverconfig' / 'pmmo-AntiCheese.toml.bak'
        if not anticheese_backup_path.exists():
            self.dialogue.title = ft.Text("Backup 'pmmo-AntiCheese.toml' missing!")
            self.dialogue.open = True
            self.update()
            self.cwd = None
            self.settings.visible = False
            sleep(5)
            self.dialogue.open = False
            self.dialogue.title = ""
            self.update()
            return
        remove(anticheese_path)
        copyfile(anticheese_backup_path, anticheese_path)

    def get_anticheese(self) -> bool:
        self.backup_anticheese()
        anticheese_path = self.cwd / 'serverconfig' / 'pmmo-AntiCheese.toml'
        line: str
        with anticheese_path.open(mode="r") as file:
            while ( line := file.readline() ):
                if "cooloff_amount =" in line:
                    return True
        return False

    def update_biome_effects(self, e) -> None:
        if e.data == "true":
            self.remove_biome_datapack()
        else:
            self.make_biome_datapack()

    def update_dimension_effects(self, e) -> None:
        if e.data == "true":
            self.remove_dimension_datapack()
        else:
            self.make_dimension_datapack()

    def make_dimension_datapack(self) -> None:
        dimension_block_path = self.cwd / 'datapacks' / 'dimension_block'
        dimension_block_mcmeta_path = self.cwd / 'datapacks' / 'dimension_block' / 'pack.mcmeta'
        if dimension_block_path.exists():
            rmtree(dimension_block_path)
        makedirs(dimension_block_path)
        makedirs(dimension_block_path / 'data')
        with dimension_block_mcmeta_path.open("w") as file:
            json.dump(self.dimension_block, file, indent=4)

    def remove_dimension_datapack(self) -> None:
        dimension_block_path = self.cwd / 'datapacks' / 'dimension_block'
        if dimension_block_path.exists():
            rmtree(dimension_block_path)

    def get_dimension_datapack(self) -> bool:
        dimension_datapack_path = self.cwd / 'datapacks' / 'dimension_block'
        return not dimension_datapack_path.exists()

    def make_biome_datapack(self) -> None:
        biome_block_path = self.cwd / 'datapacks' / 'biome_block'
        biome_block_mcmeta_path = self.cwd / 'datapacks' / 'biome_block' / 'pack.mcmeta'
        if biome_block_path.exists():
            rmtree(biome_block_path)
        makedirs(biome_block_path)
        makedirs(biome_block_path / 'data')
        with biome_block_mcmeta_path.open("w") as file:
            json.dump(self.biome_block, file, indent=4)

    def remove_biome_datapack(self) -> None:
        biome_block_path = self.cwd / 'datapacks' / 'biome_block'
        if biome_block_path.exists():
            rmtree(biome_block_path)

    def get_biome_datapack(self) -> bool:
        biome_datapack_path = self.cwd / 'datapacks' / 'biome_block'
        return not biome_datapack_path.exists()

    def update_perks(self, e) -> None:
        perks_path = self.cwd / 'serverconfig' / 'pmmo-Perks.toml'
        if e.data == "true":
            self.restore_perks()
            self.process_defaults()
            self.update()
            return
        with perks_path.open(mode="r") as file:
            perks = file.readlines()
        save_data = []
        line: str
        for line in perks:
            if "[Perks.For_Event]" in line or "[Perks]" in line: # Required lines
                save_data.append(line)
                continue
            elif line.startswith("#"): # Comments
                save_data.append(line)
                continue
            elif not line.strip(): # Empty lines
                save_data.append(line)
                continue
        with perks_path.open(mode="w") as file:
            file.writelines(save_data)
        self.process_defaults()
        self.update()

    def backup_perks(self) -> None:
        perks_path = self.cwd / 'serverconfig' / 'pmmo-Perks.toml'
        perks_backup_path = self.cwd / 'serverconfig' / 'pmmo-Perks.toml.bak'
        if perks_backup_path.exists():
            return
        copyfile(perks_path, perks_backup_path)
    
    def restore_perks(self) -> None:
        perks_path = self.cwd / 'serverconfig' / 'pmmo-Perks.toml'
        perks_backup_path = self.cwd / 'serverconfig' / 'pmmo-Perks.toml.bak'
        if not perks_backup_path.exists():
            self.dialogue.title = ft.Text("Backup 'pmmo-Perks.toml' missing!")
            self.dialogue.open = True
            self.update()
            self.cwd = None
            self.settings.visible = False
            sleep(5)
            self.dialogue.open = False
            self.dialogue.title = ""
            self.update()
            return
        remove(perks_path)
        copyfile(perks_backup_path, perks_path)

    def get_perks(self) -> bool:
        self.backup_perks()
        perks_path = self.cwd / 'serverconfig' / 'pmmo-Perks.toml'
        line: str
        with perks_path.open(mode="r") as file:
            while ( line := file.readline() ):
                if "perk =" in line:
                    return True
        return False

    def update_monster_buffs(self, e) -> None:
        requirements_path = self.cwd / 'serverconfig' / 'pmmo-server.toml'
        with requirements_path.open(mode="r") as file:
            requirements = file.readlines()
        save_data = []
        line: str
        for line in requirements:
            match = self.monster_buffs_re.match(line)
            if match:
                line = f"{match['pre_whitespace']}{match['option']}{e.data}\n"
            save_data.append(line)
        with requirements_path.open(mode="w") as file:
            file.writelines(save_data)
        self.process_defaults()
        self.update()

    def get_monster_buffs(self) -> bool:
        self.backup_pmmoserver()
        requirements_path = self.cwd / 'serverconfig' / 'pmmo-server.toml'
        line: str
        with requirements_path.open(mode="r") as file:
            while ( line := file.readline() ):
                if not self.monster_buffs_re.match(line):
                    continue
                if line.strip().endswith("true"):
                    return True
        return False

    def update_lose_xp_on_death(self, e) -> None:
        requirements_path = self.cwd / 'serverconfig' / 'pmmo-server.toml'
        with requirements_path.open(mode="r") as file:
            requirements = file.readlines()
        save_data = []
        line: str
        value: float = None
        if isinstance(e.control, ft.TextField):
            if not self.integer_re.match(e.data):
                self.dialogue.title = ft.Text("Must be a number between 1 and 100 (inclusive)")
                self.dialogue.open = True
                self.process_defaults()
                self.update()
                sleep(5)
                self.dialogue.open = False
                self.dialogue.title = ""
                self.update()
                return
            value = (float(e.data) / 100)
        else:
            if e.data == "false":
                value = 0.0
                self.lose_xp_on_death_textfield.disabled = True
            else:
                value = 0.05
                self.lose_xp_on_death_textfield.disabled = False
        for line in requirements:
            match = self.xp_loss_on_death_re.match(line)
            if match:
                line = f"{match['pre_whitespace']}{match['option']}{str(value)}\n"
            save_data.append(line)
        with requirements_path.open(mode="w") as file:
            file.writelines(save_data)
        self.process_defaults()
        self.update()

    def get_xp_loss_on_death(self) -> float:
        self.backup_pmmoserver()
        requirements_path = self.cwd / 'serverconfig' / 'pmmo-server.toml'
        line: str
        with requirements_path.open(mode="r") as file:
            while ( line := file.readline() ):
                loss = self.xp_loss_on_death_re.match(line)
                if not loss:
                    continue
                return loss['value']
        self.dialogue.title = ft.Text("'pmmo-server.toml' is corrupt or missing values (xp loss). Attempting to restore...")
        self.dialogue.open = True
        self.update()
        sleep(5)
        self.dialogue.open = False
        self.dialogue.title = ""
        self.update()
        self.restore_pmmoserver()
        return 0.05

    def update_xp_multiplier(self, e) -> None:
        requirements_path = self.cwd / 'serverconfig' / 'pmmo-server.toml'
        with requirements_path.open(mode="r") as file:
            requirements = file.readlines()
        save_data = []
        line: str
        value: float = None
        if not self.float_re.match(e.data):
            self.dialogue.title = ft.Text("Must be a number larger-than or equal-to 0")
            self.dialogue.open = True
            self.process_defaults()
            self.update()
            sleep(5)
            self.dialogue.open = False
            self.dialogue.title = ""
            self.update()
            return
        value = float(e.data)
        for line in requirements:
            match = self.xp_multiplier_re.match(line)
            if match:
                line = f"{match['pre_whitespace']}{match['option']}{str(value)}\n"
            save_data.append(line)
        with requirements_path.open(mode="w") as file:
            file.writelines(save_data)
        self.process_defaults()
        self.update()

    def get_xp_multiplier(self) -> float:
        self.backup_pmmoserver()
        requirements_path = self.cwd / 'serverconfig' / 'pmmo-server.toml'
        line: str
        with requirements_path.open(mode="r") as file:
            while ( line := file.readline() ):
                xp_multiplier = self.xp_multiplier_re.match(line)
                if not xp_multiplier:
                    continue
                return float(xp_multiplier['value'])
        self.dialogue.title = ft.Text("'pmmo-server.toml' is corrupt or missing values (xp loss). Attempting to restore...")
        self.dialogue.open = True
        self.update()
        sleep(5)
        self.dialogue.open = False
        self.dialogue.title = ""
        self.update()
        self.restore_pmmoserver()
        return 1.0

    def update_speed_perk(self, e) -> None:
        perks_path = self.cwd / 'serverconfig' / 'pmmo-Perks.toml'
        with perks_path.open(mode="r") as file:
            perks = file.readlines()
        save_data = []
        line: str
        speed_block: bool = False
        found_speed_block: bool = False
        whitespace_one: str = None
        whitespace_two: str
        for line in perks:
            if "[[Perks" in line and whitespace_one is None:
                whitespace_one = line.split("[", 1)[0]
                whitespace_two = whitespace_one + whitespace_one[1:]
            if "[[Perks.For_Event.SPRINTING]]" in line:
                speed_block = True
                found_speed_block = True
                if e.data == "true":
                    save_data.append(line)
                continue
            elif not line.strip():
                if not speed_block:
                    save_data.append(line)
                speed_block = False
                continue
            elif speed_block: # Comments
                if e.data == "true":
                    save_data.append(line)
                continue
            save_data.append(line)
        if e.data == "true" and not found_speed_block:
            save_data.append(f'{whitespace_one}[[Perks.For_Event.SPRINTING]]\n')
            save_data.append(f'{whitespace_two}duration = 20\n')
            save_data.append(f'{whitespace_two}skill = "agility"\n')
            save_data.append(f'{whitespace_two}effect = "minecraft:speed"\n')
            save_data.append(f'{whitespace_two}modifier = 2\n')
            save_data.append(f'{whitespace_two}per_level = 1\n')
            save_data.append(f'{whitespace_two}perk = "pmmo:effect"\n')
        if save_data[len(save_data) - 1].strip():
            save_data.append("\n")
        with perks_path.open(mode="w") as file:
            file.writelines(save_data)
        self.process_defaults()
        self.update()

    def get_speed_perk(self) -> bool:
        perks_path = self.cwd / 'serverconfig' / 'pmmo-Perks.toml'
        with perks_path.open(mode="r") as file:
            perks = file.readlines()
        line: str
        for line in perks:
            if 'effect = "minecraft:speed"' in line:
                return True
        return False

    def update_night_vision_perk(self, e) -> None:
        perks_path = self.cwd / 'serverconfig' / 'pmmo-Perks.toml'
        with perks_path.open(mode="r") as file:
            perks = file.readlines()
        save_data = []
        potential_data = []
        line: str
        found_night_vision_block: bool = False
        current_night_vision_block: bool = False
        potential_night_vision_block: bool = False
        whitespace_one: str = None
        whitespace_two: str
        for line in perks:
            if "[[Perks" in line and whitespace_one is None:
                whitespace_one = line.split("[", 1)[0]
                whitespace_two = whitespace_one + whitespace_one[1:]
            if e.data == 'false':
                if "[[Perks.For_Event.SUBMERGED]]" in line:
                    potential_data.append(line)
                    potential_night_vision_block = True
                    continue
                elif not line.strip() and potential_night_vision_block:
                    if not current_night_vision_block:
                        save_data += potential_data
                        save_data.append(line)
                    potential_data = []
                    current_night_vision_block = False
                    continue
                elif potential_night_vision_block: 
                    if 'effect = "minecraft:night_vision"' in line.lower():
                        found_night_vision_block = True
                        current_night_vision_block = True
                    potential_data.append(line)
                    continue
            save_data.append(line)
        if e.data == "true" and not found_night_vision_block:
            save_data.append(f'{whitespace_one}[[Perks.For_Event.SUBMERGED]]\n')
            save_data.append(f'{whitespace_two}skill = "swimming"\n')
            save_data.append(f'{whitespace_two}effect = "minecraft:night_vision"\n')
            save_data.append(f'{whitespace_two}perk = "pmmo:effect""\n')
        if save_data[len(save_data) - 1].strip():
            save_data.append("\n")
        with perks_path.open(mode="w") as file:
            file.writelines(save_data)
        self.process_defaults()
        self.update()

    def get_night_vision_perk(self) -> bool:
        perks_path = self.cwd / 'serverconfig' / 'pmmo-Perks.toml'
        with perks_path.open(mode="r") as file:
            perks = file.readlines()
        line: str
        for line in perks:
            if 'effect = "minecraft:night_vision"' in line:
                return True
        return False

    def restore_defaults(self, e) -> None:
        self.restore_pmmoserver()
        self.restore_perks()
        self.restore_anticheese()
        self.remove_biome_datapack()
        self.remove_dimension_datapack()
        self.process_defaults()
        self.update()

    def settings_disabled(self, disabled: bool = False) -> None:
        self.settings.visible = not disabled
        self.settings.update()
    
    def check_folder_event(self, e: ft.FilePickerResultEvent) -> None:
        self.check_path_button.text = "Checking..."
        self.check_path_button.disabled = True
        self.update()
        if not e.path or not self.check_folder(e.path):
            self.directory_path.value = "No Active Folder"
            self.check_path_button.text = "Folder Not Found!"
            self.settings_disabled(True)
            self.update()
            sleep(2)
            self.check_path_button.disabled = False
            self.check_path_button.text = "Open"
            self.update()
        else:
            self.directory_path.value = e.path
            self.check_path_button.text = "Opening..."
            self.update()
            sleep(2)
            self.check_path_button.text = "Open"
            self.check_path_button.disabled = False
            self.process_defaults()
            self.settings_disabled(False)
            self.update()

    def check_folder(self, path_to_save: str = None) -> bool:
        if not path_to_save:
            return False
        try:
            path_to_save = Path(path_to_save)
            
            checks = {
                "'level.dat' doesn't exist (not a Minecraft save folder)": path_to_save / 'level.dat',
                "'serverconfig' doesn't exist (open save in Minecraft)": path_to_save / 'serverconfig',
                "'datapacks' doesn't exist (open save in Minecraft)": path_to_save / 'datapacks',
                "'pmmo-server.toml' doesn't exist (open save in Minecraft)": path_to_save / 'serverconfig' / 'pmmo-server.toml',
                "'pmmo-Perks.toml' doesn't exist (open save in Minecraft)": path_to_save / 'serverconfig' / 'pmmo-Perks.toml',
                "'pmmo-AntiCheese.toml' doesn't exist (open save in Minecraft)": path_to_save / 'serverconfig' / 'pmmo-AntiCheese.toml',
            }

            for error_message, query in checks.items():
                if not query.exists():
                    raise NotSaveFolder(error_message)
            self.cwd = path_to_save
            if not self.wait_for_cwd():
                raise NotSaveFolder("IO Error!")
            return True
        except NotSaveFolder as e:
            self.dialogue.title = ft.Text(e.msg)
            self.dialogue.open = True
            self.update()
            self.cwd = None
            sleep(5)
            self.dialogue.open = False
            self.dialogue.title = ""
            self.update()
            return False


def main(page: ft.Page) -> None:
    page.horizontal_alignment=ft.CrossAxisAlignment.CENTER
    page.title = "Project MMO Basic Settings"
    page.window_width = 500
    page.window_resizable = False

    # Main Layout
    contents = SimpleSettings()
    page.add(contents)
    page.overlay.extend([contents.get_directory_dialog])
    contents.settings_disabled(True)
    page.update()


ft.app(target=main)
