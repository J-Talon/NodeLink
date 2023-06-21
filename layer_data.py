import message_sender
import recipe_handler
from items import Item, Recipe, RecipeWrapper
import copy



cache = dict()

class LayerInputData:

    #@NotNull server id, @NotNull list of options, @NotNull results from previous layer
    def __init__(self, sid: int, layers: int, recipes: [RecipeWrapper], channel):
        self.sid = sid
        self.layers = layers
        self.recipes = recipes

        self.layer_items: [Item] = []
        self.items_for_next_layer:[Item] = []
        self.channel = channel
        self.description = ""
        self.add_to_cache = False

        self.summary: [str] = []
        self.complete = False

    def update(self) -> bool:

        if self.layers < 0:
            self.complete = True
            return False

        if len(self.items_for_next_layer) == 0:
            desc = ""
#desc, curr layer items, next layer items

            if len(self.recipes) == 0:
                return False

            self.layers = self.layers - 1
            for wrapper in self.recipes:

                result: (str, [Item]) = recipe_handler.calculate_level_for_recipe(self.sid, wrapper.recipe, wrapper.amount)
                if result is None:
                    pass

                desc = desc + result[0] + "\n"
                self.layer_items.extend(result[1])
                self.items_for_next_layer.extend(result[1])

            self.description = self.description + desc
            self.recipes = []
            return True
        else:

            while len(self.items_for_next_layer) > 0:

                item:Item = self.items_for_next_layer[0]
                recipes: [Recipe] = recipe_handler.get_recipes_for_item(self.sid, item)
  #If there are no recipes, then we should not append to the thing

                if len(recipes) == 1:
                    self.recipes.append(RecipeWrapper(item.quantity,recipes[0]))
                    self.items_for_next_layer.pop()

                    return True

                elif len(recipes) > 1:
                    self.add_to_cache = True
                    return False
                else:
                    self.description = self.description + "No recipe for "+item.to_string()
                    self.items_for_next_layer.pop()
                    return False

    #returns whether we should add to cache
    async def update_return_result(self) -> bool:
        update:bool = True
        while update:
            update = self.update()


            if len(self.description) > 0:
                await message_sender.send_message(self.description, self.channel)
                self.summary.append(copy.copy(self.description))
                self.description = ""

        if not update and self.add_to_cache:
            item: Item = self.items_for_next_layer[0]
            recipes: [Recipe] = recipe_handler.get_recipes_for_item(self.sid, item)

            await message_sender.send_message("I require a branch decision of the following recipes:", self.channel)
            content:str = ""
            for i in recipes:
                content = content + i.to_string() + "\n"

            await message_sender.send_message("```"+content+"```", self.channel)

            self.add_to_cache = False
            return True
        return False

    def get_branch(self) -> [Recipe]:
        recipes: [Recipe] = recipe_handler.get_recipes_for_item(self.sid, self.items_for_next_layer[0])
        return recipes

    async def choose_branch(self, recipe: Recipe):
        amount: int = self.items_for_next_layer.pop().quantity
        self.recipes.append(RecipeWrapper(amount, recipe))


def add_to_cache(cid:int, data: LayerInputData) -> bool:
    if cache.__contains__(cid):
        cache_data: LayerInputData = cache[cid]

        if cache_data.sid == data.sid:
            cache[cid] = data
            return True
    else:
        cache[cid] = data
        return True

    return False



def contains_cid(cid:int) -> bool:
    return cache.__contains__(cid)

def get_from_cache(cid: int, sid: int):
    if cache.__contains__(cid):
        data: LayerInputData = cache[cid]
        if data.sid == sid:
            return data
        else:
            return None

    return None


def remove_from_cache(cid:int):
    cache.pop(cid)
