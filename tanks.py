import pygame


all_tanks = {
    "M1A1HA": {
        "name": "M1A1HA",
        "full_name": "M1A1(Heavy Armor) Abrams",
        "type": "Main Battle Tank",
        "ammo_options": ["M829", "M829A1", "M830"],
        "acceleration": 0.012,
        "stop_accelration": 0.012,
        "hull_turn_speed_sec": 9.3,
        "turret_turn_speed_sec": 9,
        "top_speed": 3,
        "top_reverse_speed": 2,
        "hull_sprite": "vehicle_sprites\M1A1HA_hull.png",
        "turret_sprite": "vehicle_sprites\M1A1HA_turret.png"
    },

    "T-72M": {
        "name": "T-72M",
        "full_name": "T-72M",
        "type": "Main Battle Tank",
        "ammo_options": ["3BK18M", "3FO26", "3BM22"]
    }
}