
import copy

import tree
from items import Recipe, Item
from tree import Node
import message_sender
import message_context
from discord import Embed
from discord import Colour

recipes = dict()
user_calculations = dict()

def add_recipe(sid: int, recipe: Recipe):
    global recipes


    #adding to dictionary with format {sid: {name: Recipe},...}
    if recipes.__contains__(sid):
        server = recipes[sid]
    else:
        recipes[sid] = dict()
        server = recipes[sid]

    server[recipe.name] = recipe

    #adding to dict with format {sid: {result: [...], result2: [...]} }



def delete_recipe(sid: int, name: str):

    # dictionary with format {sid: {name: Recipe},...}

    if not recipes.__contains__(sid):
        raise LookupError("No recipe found.")

    server: dict = recipes.get(sid)
    if server.__contains__(name):
        server.pop(name)
    else:
        raise LookupError("Could not find recipe "+ name +" in server "+str(sid))


def get_recipes_as_list(sid: int) -> [Item]:
    global recipes
    if recipes.__contains__(sid):
        return recipes[sid].values()
    else:
        return None

def get_recipe(sid:int, name: str) -> Recipe | None:
    if recipes.__contains__(sid):

        server_recipes:dict = recipes[sid]
        if server_recipes.__contains__(name):
            return server_recipes[name]
        else:
            return None


def get_item_requirements(sid: int, name_of_recipe: str, quantity: int) -> [Item]:
    global recipes
    dictionary: dict = recipes.get(sid, None)

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


# returns the iterator amount required for n results from a given recipe
def get_amount_required(recipe: Recipe, amount: int) -> int:
    iterations = amount / recipe.get_result().get_quantity()
    if int(iterations) < iterations:
        iterations = iterations + 1

    iterations = int(iterations)
    return iterations


def get_recipe_items(recipe: Recipe, amount: int) -> [Item]:
    items: [Item] = []
    iterations = get_amount_required(recipe, amount)

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




#Creates a new calculation
async def add_calculation(recipe: Recipe, user_id: int, server_id: int, content: message_context.MessageContext):
    calculation_id = str(user_id)+str(server_id)
    if user_calculations.__contains__(calculation_id):


        await message_sender.send_message("You already have an ongoing calculation in this server.",
                                          content.message.channel)
        return

    base = Node(recipe)
    user_calculations[calculation_id] = base
    await message_sender.send_message("Started a new calculation with target: "+str(recipe.name), content.message.channel)


async def add_node(user_id: int, server_id: int, parent_node_key: str, recipe: Recipe, content: message_context.MessageContext):
    calculation_id = str(user_id)+str(server_id)
    if not user_calculations.__contains__(calculation_id):
        await message_sender.send_message("You have no ongoing calculation, make one first!", content.message.channel)
        return

    base_node = user_calculations[calculation_id]
    new_node = Node(recipe)
    parent_node = tree.tree_search(parent_node_key, base_node)

    instance = tree.tree_search(recipe.get_recipe_name(), base_node)
    if not instance is None:
        await message_sender.send_message("Duplicate node "+recipe.get_recipe_name()+" found.", content.message.channel)
        await message_sender.send_message("(There are future plans to allow duplicates.)",content.message.channel)
        return



    if parent_node is None:
        await message_sender.send_message("Could not find node "+parent_node_key+".", content.message.channel)
        return


    requirements = parent_node.get_recipe_requirements()
    children = parent_node.get_children()

    for i in children.values():
        if recipe.get_result().get_name() == i.get_recipe().get_result().get_name():

            await message_sender.send_message("The node "+ i.get_recipe().get_recipe_name()+" already supplies the ingredient"+
                                              recipe.get_result().get_name()+".", content.message.channel)
            return

    if recipe.result.get_name() not in requirements:
        await message_sender.send_message(recipe.result.get_name()+" is not needed in "+parent_node.get_name()+".", content.message.channel)
        return


    parent_node.add_child(new_node)

    children = ""
    for i in parent_node.get_children().keys():
        children = children + " "+ i

    await message_sender.send_message(parent_node_key+" has children: "+children, content.message.channel)



async def delete_calculation(content: message_context.MessageContext):
    user_id = content.message.author.id
    server_id = content.message.guild.id

    cid = str(user_id)+str(server_id)
    user_calculations.pop(cid)



    await message_sender.send_message("Cleared calculation.", content.message.channel)


async def delete_node(node_key: str, content: message_context.MessageContext):
    user_id = content.message.author.id
    server_id = content.message.guild.id

    calc_id = str(user_id)+str(server_id)
    if not user_calculations.__contains__(calc_id):
        await message_sender.send_message("No current ongoing calculation.", content.message.channel)
        return

    node = tree.tree_search(node_key, user_calculations[calc_id])
    if node is None:
        await message_sender.send_message("Cannot find node "+node_key+".", content.message.channel)
        return

    parent = node.get_parent()

    if parent is None:
        await message_sender.send_message("Node is the root node. To delete the tree use !clear.", content.message.channel)
        return

    parent.remove_child(node.key)
    await message_sender.send_message("Removed the child node.", content.message.channel)


async def get_node_info(node_key: str, content: message_context.MessageContext):
    user_id = content.message.author.id
    server_id = content.message.guild.id

    calc_id = str(user_id)+str(server_id)
    if not user_calculations.__contains__(calc_id):
        await message_sender.send_message("No ongoing calculation.", content.message.channel)
        return

    node = user_calculations[calc_id]
    info_node = tree.tree_search(node_key, node)

    if info_node is None:
        await message_sender.send_message("No node found.", content.message.channel)
        return

    child_info = ""
    for s in info_node.get_children().keys():
        child_info = child_info + " "+s

    requirements = ""
    for s in info_node.get_recipe_requirements():
        requirements = requirements + " "+s

    parent = info_node.get_parent()
    if parent is None:
        parent_info = "No parent"
    else:
        parent_info = parent.get_name()

    message = "Node "+info_node.get_name()+": \nRequires: "+requirements +"\nChildren: "+child_info +"\nParent:"+parent_info
    await message_sender.send_message(message, content.message.channel)


async def print_tree(cid: str, content: message_context.MessageContext):
    if not user_calculations.__contains__(cid):
        await message_sender.send_message("No ongoing calculation.", content.message.channel)
        return

    node = user_calculations.get(cid)
    message = tree.print_tree(node)


    await message_sender.send_message(message, content.message.channel)


def calculate(amount: int, node: Node, dictionary: dict):
    node_children = node.get_children()
    if node_children:

        orphan_data = copy.deepcopy(node.get_recipe_requirements())
        iterator = get_amount_required(node.get_recipe(), amount)

        for child in node_children.values():

            children_required = 0
            child_name = child.get_recipe().get_result().get_name()
            for item in node.get_recipe().get_requirements():
                if item.get_name() == child_name:
                    children_required = iterator * item.get_quantity()

         #   child_recipe_name = child.get_recipe().get_result().get_name()

            if child_name in orphan_data:
                 orphan_data.remove(child_name)


            if dictionary.__contains__(node.get_name()):
                dictionary[node.get_name()].append((children_required, child_name))
            else:
                dictionary[node.get_name()] = [(children_required, child_name)]
            calculate(children_required, child, dictionary)


        node_recipe = node.get_recipe()
        for item in node_recipe.get_requirements():
            item_name = item.get_name()
            if item_name in orphan_data:
                amount_required = iterator * item.get_quantity()
                dictionary[node.get_name()].append((amount_required, item_name))


    else:
        items = get_recipe_items(node.get_recipe(), amount)

        if not dictionary.__contains__(node.get_name()):
            dictionary[node.get_name()] = []

        for i in items:
            dictionary[node.get_name()].append((i.get_quantity(), i.get_name()))


async def start_calculation(cid: str, amount: int, content: message_context.MessageContext):

    if not user_calculations.__contains__(cid):
        await message_sender.send_message("No ongoing calculation.", content.message.channel)
        return

    root_node:Node = user_calculations.get(cid)

    dictionary = dict()
    calculate(amount, root_node, dictionary)

    total_resources = dict()

    result: Embed = Embed()
    result.title = "Calculation result: "+root_node.get_name()
    result.colour = Colour(0x546e7a)

    for key, array in dictionary.items():
        title = key
        layer_message = ""
        for tup in array:
            layer_message = layer_message + str(tup[0]) + " "+ str(tup[1]) +"\n"
            if total_resources.__contains__(tup[1]):
                total_resources[tup[1]] = (total_resources.get(tup[1])) + tup[0]
            else:
                total_resources[tup[1]] = tup[0]
        layer_message += "\n"
        result.add_field(name=title, value=layer_message, inline=False)

    title = "==Summary=="
    message = ""
    for key, value in total_resources.items():
        message = message + key +" - " + str(value) + "\n"

    result.add_field(name=title, value=message, inline=False)
    await message_sender.send_message(result, content.message.channel)

