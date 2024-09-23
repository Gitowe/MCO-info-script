
# This file contains global variables and lists that are used in the main script and other functions.
# The lists are used to store player names of different types such as former staff, god donors, admins, and moderators.

import requests
import datetime
import time
import pytz
import io
import os
from tkinter import *
import tkinter as tk
import tkinter.font as tkFont
import ctypes
import pyperclip
import openpyxl
from bs4 import BeautifulSoup
from PIL import Image, ImageTk

entry = None

banned_color = '#ab3838'
mod_color = '#55FFFF'
admin_color = '#FF5555'
donor_color = '#00AA00'

# Function to get and store the player names of different types in the players.txt file
def fetch_and_store_players(url, player_type, source="wiki"):

    if source == "wiki":
        
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all("a")
            user_links = [link.get("href")[11:] for link in links if link.get("href") and link.get("href").startswith("/wiki/User:")]
            user_list = list(set(user_links))
            user_list.sort()
        else:
            print("Failed to fetch the wiki page. Status code:", response.status_code)
            return

    elif source == "api":
        
        response = requests.get(url)
        if response.status_code == 200:
            user_list = response.text.strip().split("\n")
        else:
            print("Failed to retrieve names from the api.Status code:", response.status_code)
            return
        
    else:
        print("Invalid source type.")
        return

    if not os.path.exists("players.txt"):
        with open("players.txt", "w") as file:
            file.write(f"-[{player_type}]-\n")
            for user in user_list:
                file.write(user + "\n")
            file.write("\n")
        print(f"Created players.txt and saved names of {player_type}.")
        return

    with open("players.txt", "r") as file:
        lines = file.readlines()

    header_index = None
    for i, line in enumerate(lines):
        if line.strip() == f"-[{player_type}]-":
            header_index = i
            break

    new_content = f"-[{player_type}]-\n"
    for user in user_list:
        new_content += user + "\n"
    new_content += "\n"

    if header_index is not None:
        lines[header_index+1:] = new_content.splitlines(True)[1:]
    else:
        lines.append(new_content)

    with open("players.txt", "w") as file:
        file.writelines(lines)

    print(f"Names of {player_type} have been saved/updated in players.txt.")
    
# Function to read player names based on their type from the players.txt file
def read_players(player_type):
    
    player_names = []
    player_type_found = False
    with open("players.txt", "r") as file:
        lines = file.readlines()

    for line in lines:
        if line.strip() == f"-[{player_type}]-":
            player_type_found = True
        elif player_type_found:
            if line.strip() == "":
                break
            player_names.append(line.strip())

    return player_names

# Initializes the players.txt file and stores the names of different types of players in global lists
if not os.path.exists("players.txt"):
    fetch_and_store_players("https://minecraftonline.com/wiki/Category:Former_staff", "Former Staff", "wiki")
    fetch_and_store_players("https://minecraftonline.com/wiki/Category:God_donor", "God Donor", "wiki")
    fetch_and_store_players("https://minecraftonline.com/cgi-bin/getadminlist.sh", "Admins", "api")
    fetch_and_store_players("https://minecraftonline.com/cgi-bin/getmodlist.sh", "Moderators", "api")

formerstafflist = read_players("Former Staff")
godlist = read_players("God Donor")
adminlist = read_players("Admins")
modlist = read_players("Moderators")