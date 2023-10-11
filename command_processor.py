
from discord import User, Member
import discord.abc


import recipe_handler
from message_context import MessageContext
import message_sender
from discord import Embed
from discord import Colour
import os

from items import Recipe, Item
import item_generator




prefixes = dict()

def get_prefix_for_server(message: discord.Message) -> str:
    """
    Takes in a message object and returns the prefix used in the server.
    If the prefix does not exist, it is auto-added.
    :param message: The message
    :return: String of the prefix
    """
    server_id: int = message.guild.id
    if prefixes.__contains__(server_id):
        return prefixes[server_id]

    prefixes[server_id] = "!"
    return "!"


def set_prefix(message:discord.Message, prefix:str):
    server_id : int = message.guild.id
    prefixes[server_id] = prefix

async def chippy_command(content: MessageContext):
    prefix: str = get_prefix_for_server(content.message)
    if not (prefix == content.prefix):
        return

    message: discord.Message = content.message
    user: User | Member = message.author
    channel = message.channel

    if user.id == 753048923655897100:
        await message_sender.send_message("Hiya Chippy! How ya doin'?",channel)
    else:
        await message_sender.send_message("Hi "+str(user.name)+"!",channel)


async def show_manual(content: MessageContext):
    prefix: str = get_prefix_for_server(content.message)
    if not (prefix == content.prefix):
        return

    manual: Embed = Embed()
    manual.title = "Recipe tracker Help"
    manual.colour = Colour(0x546e7a)

    try:
        file_handle = open(os.getcwd() + "\data\help manual","r")
        title_set: bool = False
        title: str = ""
        data = ""

        lines = file_handle.readlines()
        index = -1

        for line in lines:
            index = index + 1

            if index == len(lines)-1:
                data = data + line
                manual.add_field(name=title,value=data,inline=False)
                break

            if line == "\n":

                if title_set:
                    manual.add_field(name=title, value=data, inline=False)

                title_set = False
                data = ""
                title = ""

            else:
                if not title_set:
                    title_set = True
                    title = line
                    continue

                data = data + line

        await message_sender.send_message(manual, content.message.channel)
    except Exception as e:
        await message_sender.send_message("Could not get data for the manual: "+str(e),content.message.channel)



async def create_recipe(content: MessageContext):
    prefix: str = get_prefix_for_server(content.message)
    if not (prefix == content.prefix):
        return

    arguments: [str] = content.args
    if arguments is None:
        await message_sender.send_message("Missing arguments. 4 required.", content.message.channel)
        return

    if len(arguments) < 4:
        await message_sender.send_message("Minimum of 4 arguments required, you have "+str(len(arguments))+".", content.message.channel)
        return

    if not arguments[len(arguments)-2] == "=":
        await message_sender.send_message("The = is missing or is in the wrong place.", content.message.channel)
        return

    try:
        name:str = arguments[0]
        ingredients: [Item] = item_generator.parse_items(arguments[1:len(arguments)-2])
        result:Item = item_generator.parse_item(arguments[len(arguments)-1])
    except ValueError:
        await message_sender.send_message("Invalid syntax detected in ingredients or result.", content.message.channel)
        return

    recipe_handler.add_recipe(content.message.guild.id, Recipe(name, result, ingredients))
    await message_sender.send_message("Added the recipe.", content.message.channel)


async def show_recipes(content: MessageContext):
    prefix: str = get_prefix_for_server(content.message)
    if not (prefix == content.prefix):
        return
    recipes = recipe_handler.get_recipes_as_list(content.message.guild.id)
    context = ""

    if recipes is None or len(recipes) == 0:
        await message_sender.send_message("There are no recipes.", content.message.channel)
        return

    for i in recipes:
        context = context + i.to_string() +"\n"
    context = "```" + context + "```"
    await message_sender.send_message(context, content.message.channel)

async def show_recipe(content: MessageContext):
    prefix: str = get_prefix_for_server(content.message)
    if not (prefix == content.prefix):
        return


    if content.args is None:
        await message_sender.send_message("Missing arguments. 1 required.", content.message.channel)
        return

    if not len(content.args) == 1:
        await message_sender.send_message("Expected 1 argument, you gave "+str(len(content.args)), content.message.channel)
        return

    recipe:Recipe = recipe_handler.get_recipe(content.message.guild.id, content.args[0])
    if not recipe is None:
        await message_sender.send_message(recipe.to_string(), content.message.channel)
    else:
        await message_sender.send_message("Recipe not found.", content.message.channel)


async def delete_recipes(content: MessageContext):
    prefix: str = get_prefix_for_server(content.message)
    if not (prefix == content.prefix):
        return

    del_list = ""
    for arg in content.args:

        try:
            recipe_handler.delete_recipe(content.message.guild.id, arg)
            del_list = del_list + arg +" "

        except ValueError | LookupError:
            await message_sender.send_message("Recipe "+arg+" not found.", content.message.channel)

    await message_sender.send_message("Deleted recipes: " +del_list+ ".", content.message.channel)

async def order_66(content: MessageContext):
    prefix: str = get_prefix_for_server(content.message)
    if not (prefix == content.prefix):
        return

    await message_sender.send_message("**Yes my Lord. Beginning the recipe purge...**", content.message.channel)
    sid: int = content.message.guild.id

    recipes: [Recipe] = recipe_handler.get_recipes_as_list(sid)
    if recipes is None:
        await message_sender.send_message("**There are no recipes to purge my lord.**", content.message.channel)
        return

    names: [str] = []
    for i in recipes:
        names.append(i.name)

    content.args = names

    await delete_recipes(content)
    await message_sender.send_message("**All recipes have been purged my lord.**", content.message.channel)

async def prefix_set(content: MessageContext):
    prefix: str = get_prefix_for_server(content.message)
    if not (prefix == content.prefix):
        return

    if not len(content.args) == 1:
        await message_sender.send_message("1 argument only.", content.message.channel)
        return

    if content.args[0] == "/":
        await message_sender.send_message("Cannot use / as it may conflict with slash commands", content.message.channel)
        return

    set_prefix(content.message, content.args[0])
    await message_sender.send_message("Set my prefix to "+get_prefix_for_server(content.message),content.message.channel)


async def print_prefix(message: discord.Message):
    prefix = get_prefix_for_server(message)
    await message_sender.send_message("Hi! My prefix here is: "+prefix
                                      +"\n Use "+prefix+"help for my manual.",message.channel)





async def create_calculation(content: MessageContext):

    if content.args is None:
        await message_sender.send_message("Requires 1 argument", content.message.channel)
        return

    if not len(content.args) == 1:
        await message_sender.send_message("1 argument only.", content.message.channel)
        return

    recipe_name = content.args[0]
    server_id = content.message.guild.id
    user_id = content.message.author.id

    recipe = recipe_handler.get_recipe(server_id, recipe_name)
    if recipe is None:
        await message_sender.send_message("Could not find recipe " + recipe_name, content.message.channel)
        return None

    await recipe_handler.add_calculation(recipe, user_id, server_id, content)




async def add_node_child(content: MessageContext):

    if content.args is None:
        await message_sender.send_message("Command requires 2 arguments", content.message.channel)
        return


    if not len(content.args) == 2:
        await message_sender.send_message("Command requires parent node, child node (2 args)", content.message.channel)
        return

    parent_node = content.args[0]
    child_node = content.args[1]

    server_id = content.message.guild.id
    child_recipe = recipe_handler.get_recipe(server_id, child_node)
    user_id = content.message.author.id

    if child_recipe is None:
        await message_sender.send_message("Could not find recipe "+child_node, content.message.channel)
        return

    await recipe_handler.add_node(user_id,server_id,parent_node,child_recipe,content)


async def clear_calculation(content: MessageContext):
    await recipe_handler.delete_calculation(content)


async def delete_node(content: MessageContext):
    if content.args is None:
        await message_sender.send_message("Require 1 argument", content.message.channel)
        return

    if len(content.args) != 1:
        await message_sender.send_message("Require 1 argument", content.message.channel)
        return

    node_key = content.args[0]
    await recipe_handler.delete_node(node_key, content)


async def print_node(content: MessageContext):
    if content.args is None:
        await message_sender.send_message("Requires 1 argument", content.message.channel)
        return

    if len(content.args) != 1:
        await message_sender.send_message("Requires 1 argument", content.message.channel)
        return

    await recipe_handler.get_node_info(content.args[0], content)


async def print_tree(content: MessageContext):
    user_id = content.message.author.id
    server_id = content.message.guild.id

    cid = str(user_id)+str(server_id)
    await recipe_handler.print_tree(cid, content)


async def calculate(content: MessageContext):

    if content.args is None:
        await message_sender.send_message("1 argument only.", content.message.channel)
        return

    if len(content.args) != 1:
        await message_sender.send_message("1 argument only.", content.message.channel)
        return

    user_id = content.message.author.id
    server_id = content.message.guild.id

    cid = str(user_id)+str(server_id)

    try:
        amount = int(content.args[0])
        if amount < 1:
            await message_sender.send_message("Amount must be at least 1", content.message.channel)
            return

        await recipe_handler.start_calculation(cid, amount, content)
    except ValueError:
        pass

