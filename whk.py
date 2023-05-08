import csv
from itertools import combinations, permutations, product
from collections import defaultdict
import heapq

# Define a dictionary to hold recipes
recipes = {}
primary_ingredients = set()

# Read the CSV file
with open('recipes.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        item, ingredient1, quantity1, ingredient2, quantity2 = row
        quantity1, quantity2 = int(quantity1), int(quantity2)  # convert quantities to int
        recipes[item] = {ingredient1: quantity1, ingredient2: quantity2}

def break_into_primary(item, quantity=1):
    if item not in recipes:
        # Item is a primary ingredient
        return {item: quantity}
    else:
        # Item can be broken down further
        result = defaultdict(int)
        for ingredient, qty in recipes[item].items():
            for primary, primary_qty in break_into_primary(ingredient, qty).items():
                result[primary] += primary_qty * quantity
        return result

# Find and print primary ingredients for each item
for item in recipes.keys():
    print(f"{item} is made of:")
    primary_ingredients_list = break_into_primary(item)
    for primary, quantity in primary_ingredients_list.items():
        print(f"  {quantity} {primary}")
        primary_ingredients.add(primary)

# Print the list of all primary ingredients
print("\nPrimary ingredients:")
for ingredient in primary_ingredients:
    print(f"  {ingredient}")

# Reading map.csv
map_data = {}
with open('map.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    locations = next(reader)[1:]  # read first row and store location names (excluding first empty cell)
    for row in reader:
        ingredient = row[0]
        map_data[ingredient] = {location: int(qty) if qty else 0 for location, qty in zip(locations, row[1:])}

# Reading worker.csv
worker_data = {}
with open('worker.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    locations = next(reader)[1:]  # read first row and store location names (excluding first empty cell)
    for row in reader:
        worker = row[0]
        worker_data[worker] = {location: int(multiplier) for location, multiplier in zip(locations, row[1:])}

# Reading upgrade.csv
upgrade_data = {}
with open('upgrade.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        item, sub_item, qty = row
        qty = int(qty)
        upgrade_data[item] = {sub_item: qty}

# Proof of successful decoding
print("\nMap data:")
for ingredient, locations in map_data.items():
    print(f"{ingredient}: {locations}")

print("\nWorker data:")
for worker, locations in worker_data.items():
    print(f"{worker}: {locations}")

print("\nUpgrade data:")
for item, sub_item_data in upgrade_data.items():
    print(f"{item}: {sub_item_data}")

def factor_upgrade_data(item: str, sub_item: str, qty: int) -> dict[str, tuple[int, int]]:
    primary_ingredients_sub_item = break_into_primary(sub_item, qty)
    primary_ingredients_item = break_into_primary(item)

    result = {}
    for primary in set(primary_ingredients_sub_item.keys()) | set(primary_ingredients_item.keys()):
        const_qty = primary_ingredients_sub_item.get(primary, 0)
        inc_qty = primary_ingredients_item.get(primary, 0)
        result[primary] = (const_qty, inc_qty)
    return result

# Print the resulting equations
print("\nUpgrade equations:")
for item, sub_item_data in upgrade_data.items():
    for sub_item, qty in sub_item_data.items():
        equation = factor_upgrade_data(item, sub_item, qty)
        formatted_equation = ', '.join(f"{primary}{const_qty}+{inc_qty}n" for primary, (const_qty, inc_qty) in equation.items())
        print(f"{item}: {formatted_equation}")

def sum_upgrade_equations() -> dict[str, tuple[int, int]]:
    total = defaultdict(lambda: [0, 0])  # defaultdict with a list [constant part, incrementing part]

    for item, sub_item_data in upgrade_data.items():
        for sub_item, qty in sub_item_data.items():
            primary_ingredients_eq = factor_upgrade_data(item, sub_item, qty)
            for primary, (const_qty, inc_qty) in primary_ingredients_eq.items():
                total[primary][0] += const_qty
                total[primary][1] += inc_qty

    return {primary: (const_qty, n_qty) for primary, (const_qty, n_qty) in total.items()}

# Print the total equation
print("\nTotal upgrade equation:")
total_equation = sum_upgrade_equations()
formatted_total_equation = ', '.join(f"{primary}{const_qty}+{n_qty}n" for primary, (const_qty, n_qty) in total_equation.items())
print(f"총합: {formatted_total_equation}")

def print_equation(title: str, equation: dict[str, int]):
    print(title)
    for primary, qty in sorted(equation.items(), key=lambda x: -x[1]):
        print(f"{primary}{qty}", end=" ")
    print("\n")

def simplified_equations(upgrade_equations: dict[str, tuple[int, int]]) -> tuple[dict[str, int], dict[str, int]]:
    plus_5_equation = {}
    plus_n_equation = {}

    for primary, (const_qty, inc_qty) in upgrade_equations.items():
        plus_5_equation[primary] = const_qty + inc_qty * 5
        plus_n_equation[primary] = inc_qty

    return plus_5_equation, plus_n_equation

upgrade_equations = sum_upgrade_equations()
plus_5_equation, plus_n_equation = simplified_equations(upgrade_equations)

print_equation("+5 equation:", plus_5_equation)
print_equation("+n equation:", plus_n_equation)

location_multiplier = {}

# Get the list of locations from one of the worker's data
locations = list(worker_data.values())[0].keys()

for location in locations:
    # Get the top 3 workers for each location
    top_workers = sorted(worker_data, key=lambda x: worker_data[x][location], reverse=True)[:3]
    
    # Add the values of top 3 workers for each location and store it in the location_multiplier dictionary
    location_multiplier[location] = sum(worker_data[worker][location] for worker in top_workers)

multiplied_map_data = {}

for name, locations in map_data.items():
    multiplied_locations = {}
    for location, value in locations.items():
        multiplier = location_multiplier[location] / 100
        multiplied_value = value * multiplier
        multiplied_locations[location] = multiplied_value

    multiplied_map_data[name] = multiplied_locations

groups = {
    "religion": ["교회", "절"],
    "dark": ["슬럼가", "고주가", "골목길"],
    "aqua": ["등대", "연못", "모사", "항구"],
    "young": ["호텔", "묘지", "마을회관", "학교", "양궁장", "병원", "공장", "소방서"],
    "fit": ["우물", "터널", "등산로", "숲"],
    "strange": ["연구소"]
}

# Get all possible combinations of five groups out of six
group_combinations = list(combinations(groups.keys(), 5))
combination_map_data = {}

def get_ratio_score(equation, combination_data):
    ratios = {}
    # scoring
    for ingredient in combination_map_data[location_combination]:
        ratios[ingredient] = combination_map_data[location_combination][ingredient]/equation[ingredient]
    max_value = max(ratios.values())
    normalized_data = {key: value / max_value for key, value in ratios.items()}
    normalized_score = combination_map_data[location_combination]["나뭇가지"]
    return normalized_score

top_5_5 = []
top_5_n = []
for group_combination in group_combinations:
    # Combine the locations from the selected groups
    selected_locations = [groups[group] for group in group_combination]

    # Get the combination of combinations for each location
    location_combinations = list(product(*selected_locations))

    print(f"Group combination: {group_combination}")
    for location_combination in location_combinations:
        combination_map_data[location_combination] = {}
        print(f"Location combination: {location_combination}")
        for ingredient in multiplied_map_data:
            combination_map_data[location_combination][ingredient] = 0
            for location_name in multiplied_map_data[ingredient]:
                if location_name in location_combination:
                    if multiplied_map_data[ingredient][location_name] > 0:
                        combination_map_data[location_combination][ingredient] += multiplied_map_data[ingredient][location_name]

        ratio_score = get_ratio_score(plus_5_equation, combination_map_data[location_combination])
        current_combination = (ratio_score, location_combination)
        if len(top_5_5) < 5:
            heapq.heappush(top_5_5, current_combination)
        elif ratio_score > top_5_5[0][0]:
            heapq.heappushpop(top_5_5, current_combination)
            
        ratio_score = get_ratio_score(plus_n_equation, combination_map_data[location_combination])
        current_combination = (ratio_score, location_combination)
        if len(top_5_n) < 5:
            heapq.heappush(top_5_n, current_combination)
        elif ratio_score > top_5_n[0][0]:
            heapq.heappushpop(top_5_n, current_combination)

print("Equation +5")
for score, combination in sorted(top_5_5, reverse=True, key=lambda x: x[0]):
    ratios = {}
    # scoring
    for ingredient in combination_map_data[combination]:
        ratios[ingredient] = combination_map_data[combination][ingredient]/plus_5_equation[ingredient]
    max_value = max(ratios.values())
    normalized_data = {key: value / max_value for key, value in ratios.items()}
    percentage_dict = {key: f"{value * 100:.1f}%" for key, value in normalized_data.items()}
    print(f"{combination}, 점수: {score * 100:.1f}, 재료별 수급율: {combination_map_data[combination]}")

print("Equation +n")
for score, combination in sorted(top_5_n, reverse=True, key=lambda x: x[0]):
    ratios = {}
    # scoring
    for ingredient in combination_map_data[combination]:
        ratios[ingredient] = combination_map_data[combination][ingredient]/plus_n_equation[ingredient]
    max_value = max(ratios.values())
    normalized_data = {key: value / max_value for key, value in ratios.items()}
    percentage_dict = {key: f"{value * 100:.1f}%" for key, value in normalized_data.items()}
    print(f"{combination}, 점수: {score * 100:.1f}, 재료별 수급율: {combination_map_data[combination]}")

