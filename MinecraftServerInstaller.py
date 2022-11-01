import json
import os
import re

import progressbar
import requests
from bs4 import BeautifulSoup


def InstallStartServer(path): # NOT DONE
    # url for the correct version
    url = "https://www.dropbox.com/s/1xg96sj9wa3xi03/StartServerNgrok.py?dl=1"
    
    r = requests.get(url, allow_redirects=True)
    if str(r.status_code) == "420":
        return False

    open(path + "\\" + "StartServer.exe", 'wb').write(r.content)
    return True

def installServerJar(version, path):
    # url for the correct version
    url = f'https://mcversions.net/download/{version}'
   
    try: 
        # get the download url
        source = requests.get(url).text
        soup = BeautifulSoup(source, 'lxml')
        download_url = soup.find("a", class_="text-xs whitespace-nowrap py-3 px-8 bg-green-700 hover:bg-green-900 rounded text-white no-underline font-bold transition-colors duration-200")
    
        # remove html code from the url
        pattern = re.compile(r'href=".+server.jar"')
        macthes = pattern.finditer(str(download_url))
        for match in macthes:
            download_url = match.group(0)
        download_url = download_url[5:].strip('""')
    except:
        return False
    
    r = requests.get(download_url, allow_redirects=True)
    if str(r.status_code) == "420":
        return False
    
    serverName = f"server_{version}.jar"

    open(path + "\\" + serverName, 'wb').write(r.content)
    return serverName

def editEula(serverName, path):
    os.chdir(path)
    #process = subprocess.Popen("start.bat" , shell=True)
    open("eula.txt", "w").write("#By changing the setting below to TRUE you are indicating your agreement to our EULA (https://account.mojang.com/documents/minecraft_eula).\n#Sat Feb 06 21:29:55 CET 2021\neula=true")
    os.chdir("..")
    return True

def getlastestVersion():
    try:
        # get the HTML code for the lastest minecraft version
        url = "https://mcversions.net/"
        source = requests.get(url).text
        soup = BeautifulSoup(source, 'lxml')
        versionHTML = soup.find("div", class_="item flex items-center p-3 border-b border-gray-700 ss-align-start")
        
        # remove html code from the url
        pattern = re.compile(r'data-version=".?.?.?.?.?"')
        macthes = pattern.finditer(str(versionHTML))
        for match in macthes:
            version = match.group(0)
        version = version[13:].strip('""')
        
        return version
    except:
        return False

def settings(path, RAM, region, serverName, channelid):
    try:
        # save the settings
        SettingsInJson = {"Settings":{"RAM": RAM,"Region": region,"ServerName": serverName,"ChannelId": channelid}}
        json.dump(SettingsInJson, open(path + "\settings.json", "w"))
    except Exception as e:
        print(e)
        return False

def main():
    # vars
    RAM = None    
    
    # inputs
    version = input("What verstion of minecraft? (Press enter for the latest vertion): ")
   
    RAMInput = input("How many bytes of RAM? (Default = 1024M | Recommended = 1-2G): ")
   
    region = input("What region [us|eu|ap|au|sa|jp|in] (Default = eu): ")

    channelid = input("To get the channel id Settings --> advanced --> developer mode. Then go out of settings and right click the channel and click copy id\nPast the Channel id to send ip automatic. (Optional): ")

    print("To get a discord bot sending the ip add this bot to your server. https://discord.com/api/oauth2/authorize?client_id=862212595552485387&permissions=2048&scope=bot")
   
    print("Downloading the server files...")
    
    bar = progressbar.ProgressBar(maxval=6, \
        widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    bar.update(0)
    
    #version = 1.17
    #RAMInput = None

    #get the lastestVersion
    if version == "" or version == " ":
        version = getlastestVersion()
        if not version:
            print("Can't get the lastest minecraft version.")
            quit()
    bar.update(1)
    
    path = f"Minecraft Server {version}"
    if not os.path.isdir(path):
            os.mkdir(path)
    
    # check if RAM input is vaild...
    pattern = re.compile(r'\d+(M|G)')
    macthes = pattern.finditer(str(RAMInput))
    for match in macthes:
        RAM = match.group(0)
    if not RAM:
        RAM = "1024M"
    bar.update(2)
    
    # Install Start Server file
    if not InstallStartServer(path):
        print("Error couldn't install the server start file. Check internet connection and try agin!")
        quit()
    bar.update(3)

    # Install the server.jar fille
    serverName = installServerJar(version, path)
    if not serverName:
        print("invalid minecraft version")
        main()
    bar.update(4)
    
    # Make a settings file for start server progam
    if not settings(path, RAM, region, serverName, channelid = "None"):
        print("couldn't save the settigns. Sever is installet, but settings are not saved!")
    bar.update(5)

    # Agree the the Eula
    if not editEula(serverName, path):
        print("couldn't agree to minecraft eula. https://account.mojang.com/documents/minecraft_eula")
    bar.update(6)
    
    bar.finish()

if __name__ == "__main__":
    main()

#todo: auto sign up for ngork, download java, download java 16
    
