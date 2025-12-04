import sys, requests, json
from type_matchups import get_single_weaknesses_and_resistances, get_multi_weaknesses_and_resistances
from pathlib import Path

# create local cache folder
# check command line arg for pokemon name
# check local cache for json file
# reach out to API if cache misses
# store results in cache folder
# display pokedex info

api_pokemon_url = "https://pokeapi.co/api/v2/pokemon"
api_type_url = "https://pokeapi.co/api/v2/type"

def init() -> tuple[Path, Path, Path]:
    script_dir = Path(__file__).resolve().parent
    cache_dir = script_dir / "cache"
    types_dir = script_dir / "types"
    pokemon_names_file = cache_dir / "pokemon_names.txt"

    # Create cache folder and download list of all valid Pokemon names
    if not cache_dir.exists():
        print("INFO: Cache folder not found. Creating...")
        cache_dir.mkdir(parents=True)
        print(f"INFO: Cache folder created at {cache_dir}")

        print("INFO: Downloading list of Pokemon names...")
        params = {"limit": 10000, "offset": 0}
        headers = {"Accept": "application/json"}
        try:
            response = requests.get(api_pokemon_url, params=params, headers=headers)
            response.raise_for_status()
            pokemon_all_raw = response.json()
        except Exception as e:
            print(f"ERROR: {e}")

        pokemon_all = []

        for pkmn_obj in pokemon_all_raw["results"]:
            pokemon_all += pkmn_obj["name"] + "\n"

        with open(pokemon_names_file, "w", encoding="utf-8") as f:
            f.writelines(pokemon_all)
            f.close()
        print("INFO: Download complete!")

    # Create types folder and download json data for all 19 types. Used for type matchup data later
    if not types_dir.exists():
        print("INFO: Types folder not found. Creating...")
        types_dir.mkdir(parents=True)
        print(f"INFO: Types folder created at {types_dir}")

        print("INFO: Downloading Pokemon type data...")
        headers = {"Accept": "application/json"}

        for i in range(1,20):
            try:
                response = requests.get(f"{api_type_url}/{i}", headers=headers)
                response.raise_for_status()
                type_json = response.json()
                
            except Exception as e:
                print(f"ERROR: {e}")
            
            type_file = types_dir / f"{type_json["names"][7 if i < 19 else 8]["name"]}.json"
            with open(type_file, "w", encoding="utf-8") as f:
                json.dump(type_json, f, ensure_ascii=False, indent=2)
                f.close()

    return cache_dir, types_dir, pokemon_names_file

def normalize_name(raw_name: str) -> tuple[str, str]:
    prefixes = ["mega", "alolan", "galarian", "hisuian", "paldean"]
    suffixes = ["mega", "alola", "galar", "hisui", "paldea"]
    name_parts = raw_name.split(" ")

    pretty_pokemon_name = " ".join(part.capitalize() for part in name_parts)

    # Create api_pokemon_name
    if len(name_parts) > 1 and prefixes.__contains__(name_parts[0].lower()): 
        api_pokemon_name = f"{name_parts[1]}-{name_parts[0]}"

        name_parts = api_pokemon_name.split("-")
        suffix = name_parts[1].lower()
        api_pokemon_name = f"{name_parts[0]}-{suffixes[prefixes.index(suffix)]}"
    else:
        api_pokemon_name = name_parts[0].lower()
        
        # Replace dots and spaces with hyphens
        if len(name_parts) > 1: api_pokemon_name = pretty_pokemon_name.replace(". ", "-").replace(" ", "-").lower()

        api_pokemon_name = api_pokemon_name.replace(". ", "-").replace(" ", "-").lower()

    return (api_pokemon_name, pretty_pokemon_name)

def is_valid_pokemon_name(api_pokemon_name: str, pokemon_names_file: Path) -> bool:
    with open(pokemon_names_file, "r", encoding="utf-8") as f:
        for name in f:
            name = name.rstrip("\n")
            if name == api_pokemon_name: return True

    return False

def is_cached(api_pokemon_name: str, cache_dir: Path) -> bool:
    cache_file = cache_dir / f"{api_pokemon_name}.json"

    if cache_file.exists(): return True

    return False

def pull_pokedex_info(api_pokemon_name: str, cache_dir: Path) -> None:
    cache_file = cache_dir / f"{api_pokemon_name}.json"
    pokemon_url = f"{api_pokemon_url}/{api_pokemon_name}"
    headers = {"Accept": "application/json"}

    try:
        response = requests.get(pokemon_url, headers=headers)
        response.raise_for_status()
        pokemon_data = response.json()
    except Exception as e:
        print(f"ERROR: {e}")
        return

    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(pokemon_data, f, ensure_ascii=False, indent=2)
        f.close()
    return

def show_pokedex_info(api_pokemon_name: str, pretty_pokemon_name: str, cache_dir: Path, types_dir: Path) -> None:

    # Display:
    # Name (pkdex#)
    # Types
    # Weaknesses
    # Resistances
    # Abilities (indicate HA)
    # Sprite links
    # Cry link

    cache_file = cache_dir / f"{api_pokemon_name}.json"

    with open(cache_file, "r", encoding="utf-8") as f:
        pokemon_data_json = json.load(f)
        f.close()
    
    dex_num = f"{pokemon_data_json["species"]["url"]}".split("/")[6] # accounts for weird IDs for regional forms

    types = []
    for i in pokemon_data_json["types"]: types.append(i["type"]["name"])
    if len(types) == 1: 
        types_str = f"{types[0].capitalize()} type"
        weaknesses, resistances = get_single_weaknesses_and_resistances(types[0], types_dir)
    else: 
        types_str = f"{types[0].capitalize()}/{types[1].capitalize()} type"
        weaknesses, resistances = get_multi_weaknesses_and_resistances(types[0], types[1], types_dir)
    
    weaknesses_str = " \n".join(f"  - {i[0].capitalize()} (x{i[1]})" for i in (weaknesses or []))
    resistances_str = " \n".join(f"  - {i[0].capitalize()} (x{i[1]})" for i in (resistances or []))

    abilities = ""
    for i in pokemon_data_json["abilities"]:
        if len(pokemon_data_json["abilities"]) == 1: 
            abilities += f"  - {i["ability"]["name"].capitalize()}"
        else:
            if i["is_hidden"]: abilities += f"  - {i["ability"]["name"].capitalize()} (Hidden)"
            else: abilities += f"  - {i["ability"]["name"].capitalize()}\n"

    sprite_links = []
    sprite_links.append(pokemon_data_json["sprites"]["other"]["official-artwork"]["front_default"])
    sprite_links.append(pokemon_data_json["sprites"]["other"]["official-artwork"]["front_shiny"])

    cry_link = pokemon_data_json["cries"]["latest"]

    print(f"{pretty_pokemon_name} (#{dex_num}) - {types_str}\n",
          "--------------------------\n",
          f"Weaknesses:\n{weaknesses_str}\n",
          "--------------------------\n",
          f"Resistances:\n{resistances_str}\n"
          "--------------------------\n",
          f"Abilities:\n{abilities}\n",
          "--------------------------\n",
          f"Normal sprite: {sprite_links[0]}\n",
          f"Shiny sprite: {sprite_links[1]}\n",
          "--------------------------\n",
          f"Cry audio: {cry_link}")

    return

def main():
    cache_dir, types_dir, pokemon_names_file = init()

    if len(sys.argv) < 2:
        print("ERROR: Incomplete command.\n",
              "Usage: pokedex [pokemon_name]\n",
              "For megas, use the format \'pokemon-mega\'\n",
              "For regional forms, use the format \'pokemon-alola\' or \'pokemon-galar\'\n",
              "Find a full list of pokemon names in ./cache/pokemon_names.txt\n",
              "Exiting.")
        return
    
    raw_name = " ".join(sys.argv[1:])
    api_pokemon_name, pretty_pokemon_name = normalize_name(raw_name) # api_pokemon_name is formatted for the API call, pretty_pokemon_name is formatted for human readability

    if not is_valid_pokemon_name(api_pokemon_name, pokemon_names_file):
        print(f"ERROR: Invalid Pokemon name: {api_pokemon_name}\n"
              "For megas, use the format \'pokemon-mega\'\n",
              "For regional forms, use the format \'pokemon-alola\' or \'pokemon-galar\'\n",
              "Replace any spaces or other punctuation with \'-\' (e.g. \'mr-mime\', \'nidoran-m\')\n",
              "Find a full list of pokemon names in ./cache/pokemon_names.txt\n",
              "Exiting.")
        return
    
    if not is_cached(api_pokemon_name, cache_dir): pull_pokedex_info(api_pokemon_name, cache_dir)

    show_pokedex_info(api_pokemon_name, pretty_pokemon_name, cache_dir, types_dir)

    return

if __name__ == "__main__":
    main()
