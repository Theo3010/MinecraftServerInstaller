# Progam to connect ngrok to mineccraft port (25565) and sendes it to discord server.
# by Warpmines
import asyncio
import json
import os
import shutil
import threading
import time
from datetime import date, datetime

import discord
from mcstatus import MinecraftServer
from pyngrok import conf, ngrok
from pyperclip import copy

ip = ""
lastIp = ""


def get_settings():
    Settings = json.load(open("settings.json", "r"))["Settings"]
    return Settings["RAM"], Settings["Region"], Settings["ServerName"], Settings["ChannelId"]


def get_ip(region):
    # change the region
    conf.get_default().region = region

    # create tunnel and get the ip
    ssh_tunnel = ngrok.connect(25565, "tcp")
    ssh_tunnel = str(ssh_tunnel)[20:]
    ssh_tunnel = str(ssh_tunnel)[:-22]

    # save the ip to gobal
    global ip
    ip = ssh_tunnel
    copy(ssh_tunnel)
    print('Server running on: ' + str(ssh_tunnel) +
          '. Send to discord server and copyed to clipboard. Ctrl+c to quit')

    # keep ngork proccess running
    ngrok_process = ngrok.get_ngrok_process()

    try:
        # Block until CTRL-C or some other terminating event
        ngrok_process.proc.wait()
    except KeyboardInterrupt:
        print("Shutting down server.")

        ngrok.kill()


def discordBot(channelId):
    client = discord.Client()

    intents = discord.Intents.none()
    intents.reactions = True
    intents.members = True
    intents.guilds = True

    async def update_stats(channelId):
        await client.wait_until_ready()

        global ip, lastIp

        while not client.is_closed():
            try:
                if lastIp != ip:
                    # send message to the channels
                    channel = client.get_channel(channelId)
                    await channel.send(ip)

                    lastIp = ip
                    await asyncio.sleep(1800)
            except Exception as e:
                print(e)
                await asyncio.sleep(1800)

    client.loop.create_task(update_stats(channelId))
    client.run({KEY}) # THIS WILL NOT WORK BECAUSE IT NEEDS A DISCORD KEY


def startServer(RAM, serverName):
    print(f"Running {serverName} with {RAM} RAM")
    os.system(f"java -Xmx{RAM} -Xms{RAM} -jar {serverName} nogui")
    # ngrok.kill()
    quit()


def get_players_online():
    try:
        serverStatus = MinecraftServer.lookup("localhost:25565").status()
        return serverStatus.players.online
    except Exception:
        print("Server down")
        return 0


def backup():
    while True:
        if get_players_online() > 0:
            YMD = str(date.today())  # year, month, day
            YMD = YMD.split("-")
            y, m, d = YMD[0], YMD[1], YMD[2]

            # get the hours and minutes
            timer = datetime.now().strftime("%H:%M")
            timer = timer.split(":")
            hours, minutes = timer[0], timer[1]

            path = f"{os.getcwd()}/backup/{y}/{m}/{d}/world-{y}-{m}-{d}--{hours}-{minutes}"
            try:
                shutil.copytree("world", path)
            except Exception:
                pass
            print("Backup Created")
            time.sleep(1800)  # 1800 secunds = 0.5 hours
        else:
            print("No player online, no backup")
            time.sleep(1800)  # 1800 secunds = 0.5 hours


def multiplayer():
    RAM, region, serverName, channelId = get_settings()  # Get settins
    threading.Thread(target=get_ip, args=(region,)).start()  # ngrok ip
    threading.Thread(target=startServer, args=(
        RAM, serverName, )).start()  # Start server
    threading.Thread(target=backup).start()  # Backup
    # discordBot(channelId) # Discord bot
    #startServer(RAM, serverName)


def Main():
    multiplayer()


if __name__ == "__main__":
    Main()
    # RAM, region, serverName, channelId = get_settings() # Get settins
    # startServer(RAM, serverName)
