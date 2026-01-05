from tokens import DISCORD_TOKEN, HETZNER_API_TOKEN
from game import *
from settings import BOT_PREFIX, GAMES
import discord
import sys

intents = discord.Intents.default()
intents.message_content = True  # REQUIRED for reading commands

client = discord.Client(intents=intents)


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith(BOT_PREFIX + "help"):
        msg = (
            "!help - prints this help\n"
            "!ping - simple online check\n"
            "!start GAME - starts a server for GAME\n"
            "!stop GAME - stops the server for GAME\n"
            "!status [GAME] - prints basic infos about the server for GAME\n"
            "!exit - exit bot script - should restart it when used with systemd service unit"
        )
        await message.channel.send(msg)

    elif message.content.startswith(BOT_PREFIX + "ping"):
        msg = "I'm online {0.author.mention}".format(message)
        await message.channel.send(msg)

    elif message.content.startswith(BOT_PREFIX + "start"):
        cmd = message.content.split("start", 1)[1].lower().split()
        if not cmd:
            msg = "Syntax error:\n!start GAME"
            await message.channel.send(msg)
            return

        msg = f"Game '{cmd[0]}' not found."
        for i in GAMES:
            if i.name.lower() == cmd[0]:
                if i.isRunning() is False:
                    await client.change_presence(activity=discord.Game(name="starting server..."))
                    await i.start()
                    await client.change_presence(activity=discord.Game(name="ready"))
                msg = i.status()
                break

        await message.channel.send(msg)

    elif message.content.startswith(BOT_PREFIX + "stop"):
        cmd = message.content.split("stop", 1)[1].lower().split()
        if not cmd:
            msg = "Syntax error:\n!stop GAME"
            await message.channel.send(msg)
            return

        msg = f"Game '{cmd[0]}' not found."
        for i in GAMES:
            if i.name.lower() == cmd[0]:
                if i.isRunning() is True:
                    await client.change_presence(activity=discord.Game(name="stopping server..."))
                    await i.stop()
                    await client.change_presence(activity=discord.Game(name="ready"))
                msg = i.status()
                break

        await message.channel.send(msg)

    elif message.content.startswith(BOT_PREFIX + "status"):
        cmd = message.content.split("status", 1)[1].lower().split()

        # If no game specified, print all statuses in one message
        if not cmd:
            msg = "\n".join(i.status() for i in GAMES)
            await message.channel.send(msg)
            return

        msg = f"Game '{cmd[0]}' not found."
        for i in GAMES:
            if i.name.lower() == cmd[0]:
                msg = i.status()
                break
        await message.channel.send(msg)

    elif message.content.startswith(BOT_PREFIX + "exit"):
        sys.exit("exit requested")


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")
    await client.change_presence(activity=discord.Game(name="ready"))


client.run(DISCORD_TOKEN)
