
import copy
from items import Recipe, Item

all_recipes = dict()
results_from_recipes = dict()


def add_recipe(sid: int, recipe: Recipe):
    global all_recipes
    global results_from_recipes

    #adding to dictionary with format {sid: {name: Recipe},...}
    if all_recipes.__contains__(sid):
        server = all_recipes[sid]
    else:
        all_recipes[sid] = dict()
        server = all_recipes[sid]

    server[recipe.name] = recipe

    #adding to dict with format {sid: {result: [...], result2: [...]} }

    if results_from_recipes.__contains__(sid):
        server:dict = results_from_recipes[sid]


        if server.__contains__(recipe.result.item_name):
            array: [] = server[recipe.result.item_name]

            for containing in array:
                if containing.name == recipe.name:
                    array.remove(containing)
                    break

            array.append(recipe)


        else:
            server[recipe.result.item_name] = [recipe]
    else:
        dictionary = dict()
        dictionary[recipe.result.item_name] = [recipe]
        results_from_recipes[sid] = dictionary


def delete_recipe(sid: int, name: str):

    # dictionary with format {sid: {name: Recipe},...}

    if not all_recipes.__contains__(sid):
        raise LookupError("No entry found.")

    server: dict = all_recipes.get(sid)
    if server.__contains__(name):
        recipe = server.pop(name)
    else:
        raise LookupError("Could not find value in map 1")

    # dict with format {sid: {result: [...], result2: [...]} }
    if results_from_recipes.__contains__(sid):
        server:dict = results_from_recipes[sid]

        if server.__contains__(recipe.result.item_name):
            array: [] = server[recipe.result.item_name]
            if recipe in array:
                array.remove(recipe)

            else:
                raise LookupError("Not in array")
        else:
            raise LookupError("Not in map 2.")


def get_recipes_as_list(sid: int) -> [Item]:
    global all_recipes
    if all_recipes.__contains__(sid):
        return all_recipes[sid].values()
    else:
        return None

def get_recipe(sid:int, name: str) -> Recipe | None:
    if all_recipes.__contains__(sid):

        recipes:dict = all_recipes[sid]
        if recipes.__contains__(name):
            return recipes[name]
        else:
            return None


def get_item_requirements(sid: int, name_of_recipe: str, quantity: int) -> [Item]:
    global all_recipes
    dictionary: dict = all_recipes.get(sid, None)

    if dictionary is None:
        return None

    recipe: Recipe = dictionary.get(name_of_recipe, None)
    if recipe is None:
        return None

    result = []

    for i in recipe.get_requirements():
        item = copy.deepcopy(i)
        item.set_quantity(item.quantity * quantity)
        result.append(item)

    return result


def get_recipe_items(recipe: Recipe, amount: int) -> [Item]:
    items: [Item] = []

    iterations = amount / recipe.get_result().get_quantity()
    if int(iterations) < iterations:
        iterations = iterations + 1

    iterations = int(iterations)

    for i in recipe.get_requirements():
        current: Item = copy.deepcopy(i)
        current.set_quantity(current.quantity * iterations)
        items.append(current)
    return items


def calculate_recipe_items(quantity: int, recipe: Recipe) -> (str, [Item]):
    if recipe is str:
        return None

    description: str = ""
    recipe_items: [Item] = get_recipe_items(recipe, quantity)
    for i in recipe_items:
        description = description + i.to_string() + ", "

    return description, recipe_items


def calculate_level_for_recipe(sid: int, recipe: Recipe, quantity: int) -> (str, [Item]):
    """
    :param sid: Server id
    :param recipe: The recipe to calculate
    :param quantity: the quantity required to craft
    :return: tuple containing:

    - Description of items
    - Items required in the layer calculated
    - Items required for the next layer

       or None
    """

    global results_from_recipes
    if quantity is None or quantity <= 0:
        return None

    level_items: (str, [Item]) = calculate_recipe_items(quantity, recipe)
    if level_items is None:
        return None

    server = results_from_recipes.get(sid, None)
    if server is None:
        return None

    recipes: [Recipe] = []
    for i in level_items[1]:
        recipe_list = server.get(i)  #

        if recipe_list is None:
            continue

        recipes.extend(recipe_list)

    return level_items[0], level_items[1]



def get_recipes_for_item(sid: int, item: Item) -> [Recipe]:
    global results_from_recipes

    server:dict = results_from_recipes.get(sid, None)

    if server is None:
        return []

    return server.get(item.item_name,[])