
import discord


#This class is used for storing the context of a message and possibly the associated command
class MessageContext:

    def __init__(self,message:discord.Message, label: str, args: [str], prefix: str):
        self.message = message
        self.label = label
        self.args = args
        self.prefix = prefix