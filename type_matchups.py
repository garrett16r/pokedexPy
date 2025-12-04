import json
from pathlib import Path

# This shit's gonna be difficult
#
# Get list of weaknesses for both pokemon types
# If a given weakness appears in both lists, show "(x4)"
# 2 x 2 = 4
# 
# Get list of resistances for both pokemon types
# If a given resistance appears in both lists, show "(x0.25)"
# 0.5 x 0.5 = 0.25
#
# If one type is weak to a given type while the other resists, it becomes neutral 
# 2 x 0.5 = 1
#
# If one type has a nullification resistance while the other is weak to that type, immunity wins 
# 2 x 0 = 0

def get_single_weaknesses_and_resistances(pkmn_type: str, types_dir: Path) -> tuple[list, list]:

    type_file = types_dir / f"{pkmn_type.capitalize()}.json"

    weaknesses = []
    resistances = []
    with open(type_file, "r", encoding="utf-8") as f:
        type_data_json = json.load(f)
        weaknesses_json = type_data_json["damage_relations"]["double_damage_from"]
        resistances_json = type_data_json["damage_relations"]["half_damage_from"]
        nullifications_json = type_data_json["damage_relations"]["no_damage_from"]
        f.close()

    for weakness in weaknesses_json: weaknesses.append((weakness["name"], 2))
    for resistance in resistances_json: resistances.append((resistance["name"], 0.5))
    for nullification in nullifications_json: resistances.append((nullification["name"], 0))

    return weaknesses, resistances

def get_multi_weaknesses_and_resistances(pkmn_type1: str, pkmn_type2: str, types_dir: Path) -> tuple[list, list]:

    type_file = types_dir / f"{pkmn_type1.capitalize()}.json"

    weaknesses1 = []
    resistances1 = []
    nullifications1 = []
    with open(type_file, "r", encoding="utf-8") as f:
        type_data_json = json.load(f)
        weaknesses1_json = type_data_json["damage_relations"]["double_damage_from"]
        resistances1_json = type_data_json["damage_relations"]["half_damage_from"]
        nullifications1_json = type_data_json["damage_relations"]["no_damage_from"]
        f.close()

    for weakness in weaknesses1_json: weaknesses1.append(weakness["name"])
    for resistance in resistances1_json: resistances1.append(resistance["name"])
    for nullification in nullifications1_json: resistances1.append(nullification["name"]), nullifications1.append(nullification["name"])

##############################################################

    type_file = types_dir / f"{pkmn_type2.capitalize()}.json"

    weaknesses2 = []
    resistances2 = []
    nullifications2 = []
    with open(type_file, "r", encoding="utf-8") as f:
        type_data_json = json.load(f)
        weaknesses2_json = type_data_json["damage_relations"]["double_damage_from"]
        resistances2_json = type_data_json["damage_relations"]["half_damage_from"]
        nullifications2_json = type_data_json["damage_relations"]["no_damage_from"]
        f.close()
        
    for weakness in weaknesses2_json: weaknesses2.append(weakness["name"])
    for resistance in resistances2_json: resistances2.append(resistance["name"])
    for nullification in nullifications2_json: resistances2.append(nullification["name"]), nullifications2.append(nullification["name"])
    
##############################################################
    # All weaknesses and resistances loaded, now calculate 4x, 0.25x, and 0x matchups

    weaknesses_with_mults = []
    double_weaknesses = list(set(weaknesses1) & set(weaknesses2))
    for weakness in double_weaknesses: weaknesses_with_mults.append((weakness, 4))

    resistances_with_mults = []
    double_resistances = list(set(resistances1) & set(resistances2))
    for resistance in double_resistances: resistances_with_mults.append((resistance, 0.25))

    nullifications = list(set(nullifications1) | set(nullifications2))
    for nullification in nullifications: resistances_with_mults.append((nullification, 0))

    # All 4x, 0.25x, and 0x matchups found, now filter out 1x matchups

    standard_weaknesses = list((((set(weaknesses1) | set(weaknesses2)) ^ set(double_weaknesses)) - set(resistances1)) - set(resistances2))
    for weakness in standard_weaknesses: weaknesses_with_mults.append((weakness, 2))

    standard_resistances = list(((((set(resistances1) | set(resistances2)) ^ set(double_resistances)) ^ set(nullifications)) - set(weaknesses1)) - set(weaknesses2))
    for resistance in standard_resistances: resistances_with_mults.append((resistance, 0.5))

    weaknesses_with_mults.sort(key=lambda weakness: weakness[0])
    resistances_with_mults.sort(key=lambda resistance: resistance[0])

    return weaknesses_with_mults, resistances_with_mults