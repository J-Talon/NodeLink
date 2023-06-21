
from discord import User, Member
import discord.abc

import layer_data
import recipe_handler
from message_context import MessageContext
import message_sender
from discord import Embed
from discord import Colour
import os

from items import Recipe, Item, RecipeWrapper
import item_generator


from layer_data import LayerInputData


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
        await message_sender.send_message("Hi Dev!",channel)
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

    for arg in content.args:

        try:
            recipe_handler.delete_recipe(content.message.guild.id, arg)
            await message_sender.send_message("Deleted "+arg+".", content.message.channel)

        except ValueError | LookupError:
            await message_sender.send_message("Recipe "+arg+" not found.", content.message.channel)

async def calculate_recipe(content: MessageContext):
    prefix: str = get_prefix_for_server(content.message)
    if not (prefix == content.prefix):
        return

    args: str = content.args

    if args is None:
        await message_sender.send_message("Requires 3 arguments. None given.", content.message.channel)
        return


    if not len(args) == 3:
        await message_sender.send_message("Require 3 arguments, you gave "+str(len(args)),content.message.channel)
        return

    try:
        name: str = args[0]
        amount = item_generator.to_pos_int(args[1])
        if amount is None:
            await message_sender.send_message("Invalid param for layers or amount.", content.message.channel)
            return


        layers = item_generator.to_pos_int(args[2])
        if layers is None:
            await message_sender.send_message("Invalid param for layers or amount.", content.message.channel)
            return

        if layers > 25:
            await message_sender.send_message("Max layers is 25.",content.message.channel)
            return

        layers = layers - 1

        sid:int = content.message.guild.id
        recipe: Recipe = recipe_handler.get_recipe(sid, name)
        if recipe is None:
            await message_sender.send_message("Recipe not found.", content.message.channel)
            return

        data_for_layer:LayerInputData =  LayerInputData(sid, layers,[RecipeWrapper(amount, recipe)],content.message.channel)
        add_to_cache: bool = await data_for_layer.update_return_result()
        if add_to_cache:
            layer_data.add_to_cache(content.message.author.id,data_for_layer)

    except ValueError:
        await message_sender.send_message("Parameters for amount or layers is invalid.", content.message.channel)
        return


async def clear_cache(content: MessageContext):
    prefix: str = get_prefix_for_server(content.message)
    if not (prefix == content.prefix):
        return

    cid: int = content.message.author.id
    if layer_data.contains_cid(cid):
        layer_data.remove_from_cache(cid)
    await message_sender.send_message("Removed your previous calculation from the cache.",content.message.channel)


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



async def choose_recipe(content: MessageContext):
    prefix: str = get_prefix_for_server(content.message)
    if not (prefix == content.prefix):
        return

    if not len(content.args) == 1:
        await message_sender.send_message("Requires 1 argument.", content.message.channel)
        return

    cid:int = content.message.author.id
    sid: int = content.message.guild.id

    if not layer_data.contains_cid(cid):
        await message_sender.send_message("You have no on-going calculation.", content.message.channel)
        return

    cache_data:LayerInputData = layer_data.get_from_cache(cid,sid)
    if cache_data is None:
        await message_sender.send_message("Please reply in the correct server or clear the ongoing calculation.", content.message.channel)
        return

    recipe: Recipe = recipe_handler.get_recipe(sid,content.args[0])
    if recipe is None:
        await message_sender.send_message("Recipe not found.", content.message.channel)
        return

    possible_recipes: [Recipe] = cache_data.get_branch()
    if recipe in possible_recipes:
        await cache_data.choose_branch(recipe)
        layer_data.remove_from_cache(cid)

        cache_again = await cache_data.update_return_result()
        if cache_again:
            layer_data.add_to_cache(cid, cache_data)


    else:
        choices = ""
        for i in possible_recipes:
            choices = choices + i.to_string()
        choices = "```" + choices + "```"
        await message_sender.send_message(choices, content.message.channel)


async def prefix_set(content: MessageContext):
    prefix: str = get_prefix_for_server(content.message)
    if not (prefix == content.prefix):
        return

    if not len(content.args) == 1:
        await message_sender.send_message("1 argument only.", content.message.channel)
        return

    set_prefix(content.message, content.args[0])
    await message_sender.send_message("Set my prefix to "+get_prefix_for_server(content.message),content.message.channel)


async def print_prefix(message: discord.Message):
    await message_sender.send_message("Hi! My prefix here is: "+get_prefix_for_server(message),message.channel)





