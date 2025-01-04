from bs4 import BeautifulSoup
import re
import os
from fractions import Fraction


def parse_ingredient(line):
    # Define mapping to Mealmaster-style units
    mealmaster_units = {
        "c": "c",
        "cup": "c",
        "cups": "c",
        "ts": "ts",
        "teaspoon": "ts",
        "teaspoons": "ts",
        "tb": "tb",
        "tablespoon": "tb",
        "tablespoons": "tb",
        "oz": "oz",
        "ounce": "oz",
        "ounces": "oz",
        "lb": "lb",
        "pound": "lb",
        "pounds": "lb",
        "g": "g",
        "gram": "g",
        "grams": "g",
        "kg": "kg",
        "kilogram": "kg",
        "kilograms": "kg",
        "ml": "ml",
        "milliliter": "ml",
        "milliliters": "ml",
        "l": "l",
        "liter": "l",
        "liters": "l",
        "pn": "pn",
        "pinch": "pn",
        "ds": "ds",
        "dash": "ds",
        "sl": "sl",
        "slice": "sl"
    }
    units_pattern = "|".join(mealmaster_units.keys())  # Build unit regex dynamically
    pattern = rf"""
        ^\s*                         # Optional leading whitespace
        (?P<amount>\d+\s+\d+/\d+|\d+/\d+|\d+(?:\.\d+)?)? # Amount: fractions, decimals, or integers
        \s*                          # Optional whitespace
        (?P<unit>{units_pattern})?   # Unit (optional)
        \s*                          # Optional whitespace
        (?P<ingredient>.+?)          # Ingredient text (everything else)
        \s*$                         # Optional trailing whitespace
    """
    regex = re.compile(pattern, re.IGNORECASE | re.VERBOSE)

    match = regex.match(line)
    if match:
        amount = match.group("amount")
        unit = match.group("unit")
        ingredient = match.group("ingredient").strip()

        # Convert unit to Mealmaster-compatible format
        if unit:
            unit = unit.lower()
            unit = mealmaster_units.get(unit, unit)  # Map to Mealmaster units

        return {
            "amount": amount or "",
            "unit": unit or "",
            "ingredient": ingredient,
        }
    else:
        # If no match, treat the line as just the ingredient name
        return {
            "amount": "",
            "unit": "",
            "ingredient": line.strip(),
        }




def parse_recipe(html_file):
    # Load and parse the HTML file
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    recipes = []

    # Find all recipe-details containers
    recipe_elements = soup.find_all('div', class_='recipe-details')

    for recipe_element in recipe_elements:
        # Extract recipe title
        title = recipe_element.find('h2', itemprop='name').get_text(strip=True)

        # Extract recipe course
        course = recipe_element.find('span', itemprop='recipeCourse')
        course = course.get_text(strip=True) if course else "N/A"

        # Extract recipe categories
        categories_meta = recipe_element.find_all('meta', itemprop='recipeCategory')
        categories = [meta['content'] for meta in categories_meta if meta['content']]

        # Extract serving size
        serving_size = recipe_element.find('span', itemprop='recipeYield')
        serving_size = serving_size.get_text(strip=True) if serving_size else "N/A"

        # Extract ingredients
        ingredients_div = recipe_element.find('div', class_='recipe-ingredients', itemprop='recipeIngredients')
        ingredients = [
            parse_ingredient(p.get_text(strip=True)) for p in ingredients_div.find_all('p') if p.get_text(strip=True)
        ]

        # Extract directions
        directions_div = recipe_element.find('div', itemprop='recipeDirections')
        directions = [
            p.get_text(strip=True) for p in directions_div.find_all('p') if p.get_text(strip=True)
        ]

        recipes.append({
            'title': title,
            'course': course,
            'categories': categories,
            'serving_size': serving_size,
            'ingredients': ingredients,
            'directions': directions
        })

    return recipes


def generate_mealmaster(recipe):
    """
    Converts a recipe data structure into Mealmaster format.

    Parameters:
        recipe (dict): A dictionary containing the recipe details:
            - title (str): The recipe title.
            - categories (list): List of categories (e.g., ["Dessert", "Cookies"]).
            - yield_amount (str): Yield (e.g., "4 servings").
            - ingredients (list): List of dicts with 'amount', 'unit', 'ingredient'.
            - directions (str): Step-by-step directions.

    Returns:
        str: The recipe in Mealmaster format.
    """
    # Extract recipe components
    title = recipe.get("title", "Untitled Recipe")
    categories = recipe.get("categories", [])
    yield_amount = recipe.get("yield_amount", "")
    ingredients = recipe.get("ingredients", [])
    directions = recipe.get("directions", "")

    # Header
    mm_recipe = f"""
MMMMM----------------Meal-Master recipe exported by AnyMeal-----------------
     Title: {title}
Categories: {", ".join(categories)}
  Servings: {yield_amount or "1"} serving

"""
    # Add ingredients
    for ingredient in ingredients:
        amount = ingredient.get("amount", "").rjust(7)  # Align amount
        unit = ingredient.get("unit", "").ljust(2)  # Align unit
        ingredient_text = ingredient.get("ingredient", "")
        mm_recipe += f"{amount} {unit} {ingredient_text}\n"

    mm_recipe += "\n"

    for direction in directions:
        mm_recipe += f"{direction}\n\n"

    mm_recipe += "MMMMM\n"

    return mm_recipe.strip()


if __name__ == "__main__":
    # Path to Recipe Keeper HTML export
    input_html = "recipes.html"

    if not os.path.exists(input_html):
        print(f"File not found: {input_html}")
    else:
        recipes = parse_recipe(input_html)
        for recipe in recipes:
            print(generate_mealmaster(recipe))
