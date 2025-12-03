# pokedexPy
A command-line Pokedex tool. Works for all current Pokemon (Gens 1-9) with all regional forms and mega evolutions.

Developed as a way for me to practice my Python, REST API, caching, and JSON parsing skills using information I'm already very familiar with.

Data is pulled from the amazing [PokeAPI](https://pokeapi.co) project.

# Setup
1. Clone the repository (`git clone https://github.com/garrett16r/pokedexPy.git`)
2. For the easiest setup, install [astral-sh/uv](https://github.com/astral-sh/uv)
3. Run `uv sync` to create the virtual environment and install dependencies
4. Use `uv run pokedex.py [pokemon_name]` to pull Pokemon data

## Notes
- On first run, two folders will be created in the same directory as pokedex.py
- `cache/` stores previously pulled Pokemon data and a list of all valid Pokemon names
- `types/` stores one .json file per type, which will be used for calculating type weaknesses and resistances
- pokemon_names.txt and \[type\].json will also be downloaded from PokeAPI at this time
