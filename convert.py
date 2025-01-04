from bs4 import BeautifulSoup
import os


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
            p.get_text(strip=True) for p in ingredients_div.find_all('p') if p.get_text(strip=True)
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

def save_recipes_to_file(recipes, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        for recipe in recipes:
            file.write(f"Title: {recipe['title']}\n")
            file.write(f"Course: {recipe['course']}\n")
            file.write("Categories: " + ", ".join(recipe['categories']) + "\n")
            file.write(f"Serving Size: {recipe['serving_size']}\n")
            file.write("Ingredients:\n")
            for ingredient in recipe['ingredients']:
                file.write(f"  - {ingredient}\n")
            file.write("Directions:\n")
            for direction in recipe['directions']:
                file.write(f"  - {direction}\n")
            file.write("\n")


if __name__ == "__main__":
    # Path to Recipe Keeper HTML export
    input_html = "recipes.html"
    output_txt = "output.txt"

    if not os.path.exists(input_html):
        print(f"File not found: {input_html}")
    else:
        recipes = parse_recipe(input_html)
        if recipes:
            save_recipes_to_file(recipes, output_txt)
            print(f"Extracted {len(recipes)} recipes to {output_txt}")
        else:
            print("No recipes found in the file.")
