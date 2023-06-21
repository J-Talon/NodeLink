import os
import sys

import discord
import discord.client
import input_parser as messager

import dotenv


BOT_TOKEN = None
try:
    dotenv.load_dotenv("../bot_id.env")
    BOT_TOKEN = os.environ.get("BOT_ID")
except RuntimeError as e:
    print("Could not load bot token from the file.")
    sys.exit(1)

INTENTS = discord.Intents.default()
INTENTS.messages = True
INTENTS.message_content = True

def run_bot():
    '''
    
    :return:
    '''
    client = discord.Client(intents=INTENTS)

    @client.event
    async def on_ready():
        print(client.user.name + " is now running")

    @client.event
    async def on_message(message: discord.Message):
        try:
            if message.author == client.user:
                return

            await messager.await_message(message,client.user)

        except Exception as err:
            print(err)
            print(err.__cause__)

    client.run(BOT_TOKEN)


if __name__ == '__main__':
    run_bot()




