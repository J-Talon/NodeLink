
import discord

import command_processor
from message_context import MessageContext as Context
import command_processor as cmd

#
commands = {
    "recipe":cmd.create_recipe,
    "delete":cmd.delete_recipes,
    "calculate":cmd.calculate_recipe,
    "get":cmd.show_recipe,
    "list":cmd.show_recipes,
    "help":cmd.show_manual,
    "chippy":cmd.chippy_command,
    "execute_order_66":cmd.order_66,
    "clear_calculation":cmd.clear_cache,
    "set_prefix":cmd.prefix_set,
    "choose_recipe":cmd.choose_recipe
}


def get_label(content: str) -> str | None:
    '''

    :param content:
    :return:
    '''
    command = content.split(" ")[0]
    if len(command) == 0:
        return None
    else:
        string: str = command[1:len(command)]
        if commands.__contains__(string):
            return string
        return None

def get_arguments(content: str) -> [str]:
    '''

    :param content:
    :return:
    '''
    args = content.split()
    if len(args) > 1:
        return args[1:len(args)]
    else:
        return None

async def await_message(message:discord.Message, client):
    '''

    :param message:
    :param client:
    :return:
    '''

    content: str = message.content
    if len(content) == 0:
        return

    if message.mentions.__contains__(client):
        await command_processor.print_prefix(message)
        return

    command: str = get_label(content)
    args: [str] = get_arguments(content)

    if command is None:
        return

    context:Context = Context(message, command, args, content[0])
    cmd_function = commands.get(command)
    await cmd_function(context)


