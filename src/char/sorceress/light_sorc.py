import keyboard
import time
from char.sorceress import Sorceress
from utils.custom_mouse import mouse
from logger import Logger
from utils.misc import wait, rotate_vec, unit_vector
import random
from pather import Location
import numpy as np
from screen import convert_abs_to_monitor, grab, convert_screen_to_abs
from config import Config
from pather import Pather
from utils.misc import color_filter
from item.pickit import PickIt

class LightSorc(Sorceress):
    def __init__(self, skill_hotkeys: dict, pather: Pather, pickit: PickIt):
        Logger.info("Setting up Light Sorc")
        super().__init__(skill_hotkeys, pather)
        self._pickit = pickit
        self._picked_up_items = False

    def _chain_lightning(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.2, 0.3), spray: int = 10, iterations: int = 4):
        keyboard.send(Config().char["stand_still"], do_release=False)
        if self._skill_hotkeys["chain_lightning"]:
            keyboard.send(self._skill_hotkeys["chain_lightning"])
        for _ in range(iterations):
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            pos_m = convert_abs_to_monitor((x, y))
            mouse.move(*pos_m, delay_factor=[0.3, 0.6])
            mouse.press(button="left")
            wait(delay[0], delay[1])
            mouse.release(button="left")
        keyboard.send(Config().char["stand_still"], do_press=False)

    def _lightning(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.2, 0.3), spray: float = 10, iterations: int = 3):
        if not self._skill_hotkeys["lightning"]:
            raise ValueError("You did not set lightning hotkey!")
        keyboard.send(self._skill_hotkeys["lightning"])
        for _ in range(iterations):
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            cast_pos_monitor = convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor, delay_factor=[0.3, 0.6])
            mouse.press(button="right")
            wait(delay[0], delay[1])
            mouse.release(button="right")

    def _frozen_orb(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.2, 0.3), spray: float = 10):
        if self._skill_hotkeys["frozen_orb"]:
            keyboard.send(self._skill_hotkeys["frozen_orb"])
            for _ in range(3):
                x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
                y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
                cast_pos_monitor = convert_abs_to_monitor((x, y))
                mouse.move(*cast_pos_monitor)
                mouse.press(button="right")
                wait(delay[0], delay[1])
                mouse.release(button="right")

    def kill_pindle(self) -> bool:
        pindle_pos_abs = convert_screen_to_abs(Config().path["pindle_end"][0])
        cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]
        self._lightning(cast_pos_abs, spray=11)
        for _ in range(int(Config().char["atk_len_pindle"])):
            self._chain_lightning(cast_pos_abs, spray=11)
        wait(self._cast_duration, self._cast_duration + 0.2)
        # Move to items
        self._pather.traverse_nodes_fixed("pindle_end", self)
        return True

    def kill_eldritch(self) -> bool:
        eld_pos_abs = convert_screen_to_abs(Config().path["eldritch_end"][0])
        cast_pos_abs = [eld_pos_abs[0] * 0.9, eld_pos_abs[1] * 0.9]
        self._lightning(cast_pos_abs, spray=50)
        for _ in range(int(Config().char["atk_len_eldritch"])):
            self._chain_lightning(cast_pos_abs, spray=90)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        pos_m = convert_abs_to_monitor((70, -200))
        self.pre_move()
        self.move(pos_m, force_move=True)        
        self._pather.traverse_nodes(Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END)
        return True

    def kill_shenk(self) -> bool:
        shenk_pos_abs = self._pather.find_abs_node_pos(149, grab())
        if shenk_pos_abs is None:
            shenk_pos_abs = convert_screen_to_abs(Config().path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 0.9, shenk_pos_abs[1] * 0.9]
        self._lightning(cast_pos_abs, spray=60)
        for _ in range(int(Config().char["atk_len_shenk"] * 0.5)):
            self._chain_lightning(cast_pos_abs, spray=90)
        pos_m = convert_abs_to_monitor((150, 50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        shenk_pos_abs = convert_screen_to_abs(Config().path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 0.9, shenk_pos_abs[1] * 0.9]
        self._lightning(cast_pos_abs, spray=60)
        for _ in range(int(Config().char["atk_len_shenk"] * 0.5)):
            self._chain_lightning(cast_pos_abs, spray=90)
        pos_m = convert_abs_to_monitor((150, 50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        shenk_pos_abs = convert_screen_to_abs(Config().path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 0.9, shenk_pos_abs[1] * 0.9]
        self._lightning(cast_pos_abs, spray=60)
        for _ in range(int(Config().char["atk_len_shenk"])):
            self._chain_lightning(cast_pos_abs, spray=90)
        self.pre_move()
        self.move(pos_m, force_move=True)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, timeout=1.4, force_tp=True)
        return True

    def kill_council(self) -> bool:
        # Move inside to the right
        self._pather.traverse_nodes_fixed([(1110, 120)], self)
        self._pather.offset_node(300, (80, -110))
        self._pather.traverse_nodes([300], self, timeout=1.0, force_tp=True)
        self._pather.offset_node(300, (-80, 110))
        wait(0.5)
        self._frozen_orb((-150, -10), spray=10)
        self._lightning((-150, 0), spray=10)
        self._chain_lightning((-150, 15), spray=10)
        wait(0.5)
        pos_m = convert_abs_to_monitor((-50, 200))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(0.5)
        pos_m = convert_abs_to_monitor((-550, 230))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(0.5)
        self._pather.offset_node(226, (-80, 60))
        self._pather.traverse_nodes([226], self, timeout=1.0, force_tp=True)
        self._pather.offset_node(226, (80, -60))
        wait(0.5)
        self._frozen_orb((-150, -130), spray=10)
        self._chain_lightning((200, -185), spray=20)
        self._chain_lightning((-170, -150), spray=20)
        wait(0.5)
        self._pather.traverse_nodes_fixed([(1110, 15)], self)
        self._pather.traverse_nodes([300], self, timeout=1.0, force_tp=True)
        pos_m = convert_abs_to_monitor((300, 150))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(0.5)
        self._frozen_orb((-170, -100), spray=40)
        self._chain_lightning((-300, -100), spray=10)
        self._chain_lightning((-300, -90), spray=10)
        self._lightning((-300, -110), spray=10)
        wait(0.5)
        # Move back outside and attack
        pos_m = convert_abs_to_monitor((-430, 230))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._pather.offset_node(304, (0, -80))
        self._pather.traverse_nodes([304], self, timeout=1.0, force_tp=True)
        self._pather.offset_node(304, (0, 80))
        wait(0.5)
        self._frozen_orb((175, -170), spray=40)
        self._chain_lightning((-170, -150), spray=20)
        self._chain_lightning((300, -200), spray=20)
        self._chain_lightning((-170, -150), spray=20)
        wait(0.5)
        # Move back inside and attack
        pos_m = convert_abs_to_monitor((350, -350))
        self.pre_move()
        self.move(pos_m, force_move=True)
        pos_m = convert_abs_to_monitor((100, -30))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(0.5)
        # Attack sequence center
        self._frozen_orb((0, 20), spray=40)
        self._lightning((-50, 50), spray=30)
        self._lightning((50, 50), spray=30)
        wait(0.5)
        # Move inside
        pos_m = convert_abs_to_monitor((40, -30))
        self.pre_move()
        self.move(pos_m, force_move=True)
        # Attack sequence to center
        wait(0.5)
        self._chain_lightning((-150, 100), spray=20)
        self._chain_lightning((150, 200), spray=40)
        self._chain_lightning((-150, 0), spray=20)
        wait(0.5)
        pos_m = convert_abs_to_monitor((-200, 240))
        self.pre_move()
        self.move(pos_m, force_move=True)
        # Move outside since the trav.py expects to start searching for items there if char can teleport
        self._pather.traverse_nodes([226], self, timeout=2.5, force_tp=True)
        return True

    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        # Find nilhlatak position
        delay = [0.2, 0.3]
        atk_len = int(Config().char["atk_len_nihlathak"])
        nihlathak_pos_abs = None
        for i in range(atk_len):
            nihlathak_pos_abs_next = self._pather.find_abs_node_pos(end_nodes[-1], grab())

            if nihlathak_pos_abs_next is not None:
                nihlathak_pos_abs = nihlathak_pos_abs_next
            else:
                Logger.warning(f"Can't find Nihlathak next position at node {end_nodes[-1]}")
                if nihlathak_pos_abs is not None:
                    Logger.warning(f"Using previous position for attack sequence")

            if nihlathak_pos_abs is not None:
                cast_pos_abs = np.array([nihlathak_pos_abs[0] * 0.9, nihlathak_pos_abs[1] * 0.9])
                self._lightning(cast_pos_abs, spray=60)
                self._chain_lightning(cast_pos_abs, delay, 90)
                # Do some tele "dancing" after each sequence
                if i < atk_len - 1:
                    rot_deg = random.randint(-10, 10) if i % 2 == 0 else random.randint(170, 190)
                    tele_pos_abs = unit_vector(rotate_vec(cast_pos_abs, rot_deg)) * 100
                    pos_m = convert_abs_to_monitor(tele_pos_abs)
                    self.pre_move()
                    self.move(pos_m)
                else:
                    self._lightning(cast_pos_abs, spray=60)
            else:
                Logger.warning(f"Casting static as the last position isn't known. Skipping attack sequence")
                self._cast_static(duration=2)

        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes(end_nodes, self, timeout=0.8)
        return True

    def kill_summoner(self) -> bool:
        # Attack
        cast_pos_abs = np.array([0, 0])
        pos_m = convert_abs_to_monitor((-20, 20))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        for _ in range(int(Config().char["atk_len_arc"])):
            self._lightning(cast_pos_abs, spray=11)
            self._chain_lightning(cast_pos_abs, spray=11)
        wait(self._cast_duration, self._cast_duration + 0.2)
        return True

    def _move_and_attack(self, abs_move: tuple[int, int], atk_len: float, cast_target: tuple[int, int] = (0, 0)):
        pos_m = convert_abs_to_monitor(abs_move)
        self.pre_move()
        self.move(pos_m, force_move=True)
        # For Sorc, we just cast a few times. atk_len is treated as a multiplier for iterations.
        # Assuming atk_len is usually around 1-3.
        # _chain_lightning does 4 casts.
        duration = 1 if atk_len < 1 else int(atk_len)
        self._chain_lightning(cast_target, spray=15)
        for _ in range(duration - 1):
             self._chain_lightning(cast_target, spray=15)

    def _cs_attack_sequence(self, min_duration: float = Config().char["atk_len_cs_trashmobs"], max_duration: float = Config().char["atk_len_cs_trashmobs"] * 3):
        self._scan_and_attack_cs_mobs(min_duration, max_duration)

    def _check_trash_mob_active(self) -> bool:
        # Check if Health Bar (Red) is visible in "Enemy Info" ROI
        # We strictly check for RED to avoid detecting objects like Seals/Chests/Shrines which have nameplates but no health bar.
        img = grab()
        x, y, w, h = Config().ui_roi["enemy_info"]
        roi_img = img[y:y+h, x:x+w]
        
        # Check for RED pixels (Health Bar) AND Text presence (Name)
        # We need to ensure we are actually looking at a mob nameplate, not just red lava/blood on the floor.
        mask_red, _ = color_filter(roi_img, Config().colors["red"])
        if np.sum(mask_red) < 500:
            return False

        # If red is present, check if there is also text (White, Blue, Gold, Yellow)
        # This confirms it's a UI element (Nameplate) and not just environment
        mask_white, _ = color_filter(roi_img, Config().colors["white"])
        mask_blue, _ = color_filter(roi_img, Config().colors["blue"])
        mask_gold, _ = color_filter(roi_img, Config().colors["gold"])
        mask_yellow, _ = color_filter(roi_img, Config().colors["yellow"]) # Minions
        
        # Sum of all text pixels
        text_pixels = np.sum(mask_white) + np.sum(mask_blue) + np.sum(mask_gold) + np.sum(mask_yellow)
        
        # Threshold for text: even a short name should have some pixels. 
        # A few pixels could be noise, so let's say > 200 (arbitrary but safe for text)
        return text_pixels > 200

    def _scan_and_attack_cs_mobs(self, min_duration: float, max_duration: float):
        # Scan points (9-point Grid pattern)
        # Center, Cardinals, Corners
        scan_points = [
            (0, 0), 
            (90, 0), (-90, 0), (0, 90), (0, -90),
            (90, 90), (90, -90), (-90, 90), (-90, -90)
        ]
        
        start_global = time.time()
        for point in scan_points:
            if time.time() - start_global > max_duration:
                break

            # 1. Move mouse to target
            pos_m = convert_abs_to_monitor(point)
            mouse.move(*pos_m, delay_factor=[0.1, 0.2])
            wait(0.1) # Wait for UI to update
            
            # 2. Check if mob is there
            if self._check_trash_mob_active():
                # 3. Attack Loop
                start_attack = time.time()
                while (time.time() - start_attack) < (max_duration / len(scan_points) * 2): # Cap attack time per point
                    self._chain_lightning(point, spray=10, iterations=1)
                    
                    # 4. Re-check (Exit if dead/lost)
                    # Note: _chain_lightning moves mouse slightly. The ROI check relies on mouse hover.
                    # We accept that if the mouse moved off the mob, we consider it "lost" and move on.
                    # This prevents spamming empty space.
                    if not self._check_trash_mob_active():
                         break
            # Else: Skip point if nothing found

    def _cs_trash_mobs_attack_sequence(self, min_duration: float = 1.2, max_duration: float = Config().char["atk_len_cs_trashmobs"]):
        self._scan_and_attack_cs_mobs(min_duration, max_duration)

    def _cs_pickit(self, skip_inspect: bool = False):
        new_items = self._pickit.pick_up_items(self)
        self._picked_up_items |= new_items

    def kill_cs_trash(self, location:str) -> bool:
        match location:
            case "sealdance":
                self._cs_trash_mobs_attack_sequence()

            case "rof_01": #node 603 - outside CS in ROF
                if not self._pather.traverse_nodes([603], self, timeout=3): return False
                self._cs_trash_mobs_attack_sequence()
                self._cs_pickit()
                if not self._pather.traverse_nodes([603], self): return False

            case "rof_02": #node 604 - inside ROF
                if not self._pather.traverse_nodes([604], self, timeout=3): return False
                self._cs_trash_mobs_attack_sequence()
                self._cs_pickit()

            case "entrance_hall_01":
                self._pather.traverse_nodes_fixed("diablo_entrance_hall_1", self)
                self._cs_trash_mobs_attack_sequence()
                self._cs_pickit()

            case "entrance_hall_02":
                if not self._pather.traverse_nodes([670], self): return False
                self._pather.traverse_nodes_fixed("diablo_entrance_1_670_672", self)
                if not self._pather.traverse_nodes([670], self): return False
                self._cs_trash_mobs_attack_sequence()
                self._cs_pickit()
                if not self._pather.traverse_nodes([671], self): return False
                self._pather.traverse_nodes_fixed("diablo_entrance_hall_2", self)

            case "entrance1_01":
                self._cs_trash_mobs_attack_sequence()
                self._cs_pickit()
                if not self._pather.traverse_nodes([673], self): return False

            case "entrance1_02":
                self._cs_trash_mobs_attack_sequence()
                self._cs_pickit()
                self._pather.traverse_nodes_fixed("diablo_entrance_1_1", self)
                if not self._pather.traverse_nodes([674], self): return False

            case "entrance1_03":
                self._cs_trash_mobs_attack_sequence()
                self._cs_pickit()
                if not self._pather.traverse_nodes([675], self): return False
                self._pather.traverse_nodes_fixed("diablo_entrance_1_1", self)
                if not self._pather.traverse_nodes([676], self): return False

            case "entrance1_04":
                self._cs_trash_mobs_attack_sequence()
                self._cs_pickit()

            case "entrance2_01":
                self._cs_trash_mobs_attack_sequence()
                self._cs_pickit()

            case "entrance2_02":
                self._pather.traverse_nodes_fixed("diablo_trash_b_hall2_605_right", self)
                wait (0.2, 0.5)
                if not self._pather.traverse_nodes([605], self): return False
                self._cs_trash_mobs_attack_sequence()
                self._cs_pickit()

            case "entrance2_03":
                self._pather.traverse_nodes_fixed("diablo_trash_b_hall2_605_top1", self)
                wait (0.2, 0.5)
                self._pather.traverse_nodes_fixed("diablo_trash_b_hall2_605_top2", self)
                if not self._pather.traverse_nodes([605], self): return False
                self._cs_trash_mobs_attack_sequence()
                self._cs_pickit()

            case "entrance2_04":
                if not self._pather.traverse_nodes([605], self): return False
                self._pather.traverse_nodes_fixed("diablo_trash_b_hall2_605_hall3", self)
                if not self._pather.traverse_nodes([609], self): return False
                self._pather.traverse_nodes_fixed("diablo_trash_b_hall3_pull_609", self)
                if not self._pather.traverse_nodes([609], self): return False
                self._cs_trash_mobs_attack_sequence()
                self._cs_pickit(skip_inspect=True)
                if not self._pather.traverse_nodes([609], self): return False
                self._cs_pickit()
                if not self._pather.traverse_nodes([609], self): return False

            case "dia_trash_a" | "dia_trash_b" | "dia_trash_c":
                self._cs_trash_mobs_attack_sequence()
                self._cs_pickit()

            case "layoutcheck_a" | "layoutcheck_b" | "layoutcheck_c":
                self._cs_trash_mobs_attack_sequence()
                self._cs_pickit()

            case "pent_before_a":
                pass

            case "pent_before_b" | "pent_before_c":
                self._cs_trash_mobs_attack_sequence()
                self._cs_pickit()

            case "A1-L_01":
                if not self._pather.traverse_nodes([611], self): return False
                self._cs_trash_mobs_attack_sequence()

            case "A1-L_02":
                if not self._pather.traverse_nodes([612], self): return False
                self._cs_trash_mobs_attack_sequence()

            case "A1-L_03":
                if not self._pather.traverse_nodes([613], self): return False
                self._cs_trash_mobs_attack_sequence()
                self._cs_pickit()

            case "A1-L_seal1":
                self._cs_pickit()
                if not self._pather.traverse_nodes([614], self): return False
                self._cs_attack_sequence(min_duration=1)

            case "A1-L_seal2":
                if not self._pather.traverse_nodes([613, 615], self): return False
                self._cs_attack_sequence(min_duration=1)

            case "A2-Y_01":
                if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self): return False
                if not self._pather.traverse_nodes([622], self): return False
                self._cs_trash_mobs_attack_sequence()

            case "A2-Y_02":
                self._cs_trash_mobs_attack_sequence()

            case "A2-Y_03":
                pass

            case "A2-Y_seal1":
                if not self._pather.traverse_nodes([625], self): return False
                self._cs_attack_sequence(min_duration=1)

            case "A2-Y_seal2": #B only has 1 seal, which is the boss seal = seal2
                self._pather.traverse_nodes_fixed("dia_a2y_sealfake_sealboss", self)
                self._cs_attack_sequence(min_duration=1)

            case "B1-S_01" | "B1-S_02" | "B1-S_03":
                pass

            case "B1-S_seal2":
                if not self._pather.traverse_nodes([634], self): return False
                self._cs_trash_mobs_attack_sequence()

            case "B2-U_01" | "B2-U_02" | "B2-U_03":
                pass

            case "B2-U_seal2":
                self._pather.traverse_nodes_fixed("dia_b2u_bold_seal", self)
                if not self._pather.traverse_nodes([644], self): return False
                self._cs_attack_sequence(min_duration=1)

            case "C1-F_01" | "C1-F_02" | "C1-F_03":
                pass

            case "C1-F_seal1":
                wait(0.1,0.3)
                self._pather.traverse_nodes_fixed("dia_c1f_hop_fakeseal", self)
                wait(0.1,0.3)
                if not self._pather.traverse_nodes([655], self): return False
                self._cs_trash_mobs_attack_sequence()
                self._cs_pickit()
                if not self._pather.traverse_nodes([655], self): return False
                self._cs_attack_sequence(min_duration=1)

            case "C1-F_seal2":
                self._pather.traverse_nodes_fixed("dia_c1f_654_651", self)
                if not self._pather.traverse_nodes([652], self): return False
                self._cs_trash_mobs_attack_sequence()
                self._cs_pickit()
                if not self._pather.traverse_nodes([652], self): return False
                self._cs_attack_sequence(min_duration=1)

            case "C2-G_01" | "C2-G_02" | "C2-G_03":
                pass

            case "C2-G_seal1":
                if not self._pather.traverse_nodes([663, 662], self) or not self._pather.traverse_nodes_fixed("dia_c2g_lc_661", self): return False
                self._cs_trash_mobs_attack_sequence()
                self._cs_pickit()
                if not self._pather.traverse_nodes([662], self): return False
                self._cs_attack_sequence(min_duration=1)

            case "C2-G_seal2":
                seal_layout="C2-G"
                if not self._pather.traverse_nodes([662], self) or not self._pather.traverse_nodes_fixed("dia_c2g_663", self): return False
                atk_dur_min = Config().char["atk_len_diablo_infector"]
                atk_dur_max = atk_dur_min * 3
                Logger.debug(seal_layout + ": Attacking Infector at position 1/2")
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                if not self._pather.traverse_nodes([663], self): return False
                Logger.debug(seal_layout + ": Attacking Infector at position 2/2")
                self._cs_attack_sequence(min_duration=2, max_duration=atk_dur_max)
                self._cs_pickit(skip_inspect=True)
                if not self._pather.traverse_nodes([664, 665], self): return False

            case _:
                Logger.error("No location argument given for kill_cs_trash(" + location + "), should not happen")
                self._cs_trash_mobs_attack_sequence()
                self._cs_pickit()
        return True

    def kill_vizier(self, seal_layout:str) -> bool:
        atk_dur_min = Config().char["atk_len_diablo_vizier"]
        atk_dur_max = atk_dur_min * 3
        match seal_layout:
            case "A1-L":
                if not self._pather.traverse_nodes([612], self): return False
                Logger.debug(seal_layout + ": Attacking Vizier at position 1/2")
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                Logger.debug(seal_layout + ": Attacking Vizier at position 2/2")
                self._pather.traverse_nodes([611], self, timeout=3)
                self._cs_attack_sequence(min_duration=2, max_duration=atk_dur_max)
                self._cs_pickit(skip_inspect=True)
                if not self._pather.traverse_nodes([612], self): return False
                self._cs_pickit()
                if not self._pather.traverse_nodes([612], self): return False

            case "A2-Y":
                if not self._pather.traverse_nodes([627, 622], self): return False
                Logger.debug(seal_layout + ": Attacking Vizier at position 1/3")
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                Logger.debug(seal_layout + ": Attacking Vizier at position 2/3")
                self._pather.traverse_nodes([623], self, timeout=3)
                self._cs_attack_sequence(min_duration=1.5, max_duration=atk_dur_max)
                Logger.debug(seal_layout + ": Attacking Vizier at position 3/3")
                if not self._pather.traverse_nodes([624], self): return False
                self._cs_attack_sequence(min_duration=1.5, max_duration=atk_dur_max)
                self._cs_pickit(skip_inspect=True)
                if not self._pather.traverse_nodes([624], self): return False
                Logger.debug(seal_layout + ": Approaching Hop")
                if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self): return False
                Logger.debug(seal_layout + ": Hop!")
                if not self._pather.traverse_nodes([622], self): return False
                self._cs_pickit()
                if not self._pather.traverse_nodes([622], self): return False

            case _:
                Logger.warning(seal_layout + ": Invalid location for kill_vizier("+ seal_layout +"), should not happen.")
                return False
        return True

    def kill_deseis(self, seal_layout:str) -> bool:
        atk_dur_min = Config().char["atk_len_diablo_deseis"]
        atk_dur_max = atk_dur_min * 3
        match seal_layout:
            case "B1-S":
                self._pather.traverse_nodes_fixed("dia_b1s_seal_deseis_foh", self)
                nodes = [631]
                Logger.debug(f"{seal_layout}: Attacking De Seis at position 1/{len(nodes)+1}")
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                for i, node in enumerate(nodes):
                    Logger.debug(f"{seal_layout}: Attacking De Seis at position {i+2}/{len(nodes)+1}")
                    self._pather.traverse_nodes([node], self, timeout=3)
                    self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                self._cs_pickit()

            case "B2-U":
                self._pather.traverse_nodes_fixed("dia_b2u_644_646", self)
                nodes = [646, 641]
                Logger.debug(seal_layout + f": Attacking De Seis at position 1/{len(nodes)+1}")
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                for i, node in enumerate(nodes):
                    Logger.debug(f"{seal_layout}: Attacking De Seis at position {i+2}/{len(nodes)+1}")
                    self._pather.traverse_nodes([node], self, timeout=3)
                    self._cs_attack_sequence(min_duration=2, max_duration=atk_dur_max)
                self._cs_pickit(skip_inspect=True)
                if not self._pather.traverse_nodes([641], self): return False
                if not self._pather.traverse_nodes([646], self): return False
                self._cs_pickit(skip_inspect=True)
                if not self._pather.traverse_nodes([646], self): return False
                if not self._pather.traverse_nodes([640], self): return False
                self._cs_pickit()

            case _:
                Logger.warning(seal_layout + ": Invalid location for kill_deseis("+ seal_layout +"), should not happen.")
                return False
        return True

    def kill_infector(self, seal_layout:str) -> bool:
        atk_dur_min = Config().char["atk_len_diablo_infector"]
        atk_dur_max = atk_dur_min * 3
        match seal_layout:
            case "C1-F":
                Logger.debug(seal_layout + ": Attacking Infector at position 1/1")
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                self._pather.traverse_nodes_fixed("dia_c1f_652", self)
                Logger.debug(seal_layout + ": Attacking Infector at position 2/2")
                self._cs_attack_sequence(min_duration=2, max_duration=atk_dur_max)
                self._cs_pickit()

            case "C2-G":
                if not self._pather.traverse_nodes([665], self): return False
                Logger.debug(seal_layout + ": Attacking Infector at position 1/2")
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                if not self._pather.traverse_nodes([663], self): return False
                Logger.debug(seal_layout + ": Attacking Infector at position 2/2")
                self._cs_attack_sequence(min_duration=2, max_duration=atk_dur_max)
                self._cs_pickit()
                if not self._pather.traverse_nodes([664, 665], self): return False

            case _:
                Logger.warning(seal_layout + ": Invalid location for kill_infector("+ seal_layout +"), should not happen.")
                return False
        return True

    def _scan_and_lock_diablo(self) -> tuple[int, int]:
        # Scan in a cone/area around the expected spawn point (Upper Right)
        scan_points = [
            (100, -50), (120, -50), (80, -50), (100, -70), (100, -30),
            (60, -20), (100, -100), (50, -50)
        ]
        
        for point in scan_points:
             pos_m = convert_abs_to_monitor(point)
             mouse.move(*pos_m, delay_factor=[0.1, 0.2])
             wait(0.05)
             
             # Check for Boss Nameplate color (Gold) in Enemy Info ROI
             img = grab()
             x, y, w, h = Config().ui_roi["enemy_info"]
             roi_img = img[y:y+h, x:x+w]
             
             # Check for "gold" (Unique Monster Name)
             # Use a threshold sum to avoid noise
             mask, _ = color_filter(roi_img, Config().colors["gold"])
             if np.sum(mask) > 500: # Threshold of gold pixels indicating text
                  Logger.info(f"Target locked at {point}")
                  return point
        
        Logger.debug("Diablo target lock failed")
        return None

    def _check_boss_active(self) -> bool:
        # Check if "gold" nameplate is visible in top center
        img = grab()
        x, y, w, h = Config().ui_roi["enemy_info"]
        roi_img = img[y:y+h, x:x+w]
        mask, _ = color_filter(roi_img, Config().colors["gold"])
        return np.sum(mask) > 500

    def kill_diablo(self) -> bool:
        atk_len_dur = float(Config().char["atk_len_diablo"])
        Logger.debug("Attacking Diablo...")
        self._cast_static(1.0)
        
        start_time = time.time()
        diablo_target = None
        force_exit = False
        scan_failures = 0
        
        # Dynamic Combat Loop
        while (time.time() - start_time) < atk_len_dur:
            if force_exit:
                break

            # 1. Acquire Target if needed
            if diablo_target is None:
                diablo_target = self._scan_and_lock_diablo()
                if diablo_target is None:
                    scan_failures += 1
                    if scan_failures >= 3: # ~1.5 - 2.0 seconds of failing to find him
                        Logger.info("Diablo not found for extended time. Assuming dead.")
                        force_exit = True
                        break
                    continue
                else:
                    scan_failures = 0 # Reset on success
            
            # 2. Attack
            
            # 2. Attack
            # Cast Lightning (High Single Target DPS)
            # Use small iterations (2) to allow frequent re-checks
            self._lightning(diablo_target, spray=10, iterations=2) 
            
            # 3. Re-Verify Target
            # If he moved or died, the nameplate should be gone from the current mouse position.
            if not self._check_boss_active():
                # Check 5 times quickly to be sure (anti-flicker)
                # But _check_boss_active is instant. 
                # Let's assume if it's gone, it's gone.
                Logger.info("Diablo target lost (Dead or Moved). Re-scanning.")
                diablo_target = None
        
        # After loop ends (timeout)
        self._picked_up_items |= self._pickit.pick_up_items(self)
        return True

if __name__ == "__main__":
    import os
    import keyboard
    from pather import Pather
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    pather = Pather()
    char = LightSorc(Config().light_sorc, Config().char, pather)
    char.kill_council()
