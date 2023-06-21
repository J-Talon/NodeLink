

from discord import Embed

async def send_message(message, channel):
    try:
        if type(message) is str:
            await channel.send(message)
        elif type(message) is [str]:
            for i in message:
                await channel.send(i)
        elif type(message) is Embed:
            await channel.send(embed=message)
    except Exception as err:
        print(err)
        print(err.__cause__)
        print(err.__traceback__)


