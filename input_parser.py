
import discord

import command_processor
from message_context import MessageContext as Context
import command_processor as cmd

#
commands = {
    "recipe":cmd.create_recipe,
    "r": cmd.create_recipe,

    "delete":cmd.delete_recipes,
    "get":cmd.show_recipe,
    "list":cmd.show_recipes,
    "help":cmd.show_manual,
    "chippy":cmd.chippy_command,
    "execute_order_66":cmd.order_66,

    "set_prefix":cmd.prefix_set,

    "node": cmd.create_calculation,
    "n": cmd.create_calculation,

    "clear":cmd.clear_calculation,

    "nc":cmd.add_node_child,  #add child to node
    "node_child":cmd.add_node_child,

    "np":cmd.print_node,
    "node_print":cmd.print_node,

    "cp":cmd.print_tree,
    "calculation_print":cmd.print_tree,

    "nd":cmd.delete_node,  #delete a node
    "node_delete": cmd.delete_node,

    "calculate":cmd.calculate
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

    prefix = cmd.get_prefix_for_server(message)
    if message.content[0] != prefix:
        return

    command: str = get_label(content)
    args: [str] = get_arguments(content)

    if command is None:
        return

    context:Context = Context(message, command, args, content[0])

    cmd_function = commands.get(command)
    await cmd_function(context)


