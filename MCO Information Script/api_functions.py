
# This file contains functions that call from MCO's API and the MCO wiki.
# The functions are used to fetch player information, player heads, ban count, unique visitors, etc.

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

from global_variables import *

# Removes the brackets from the input string (used for the API responses)
def remove_brackets(input_string):
    lines = input_string
    cleaned_lines = [line[2:-2] if line.startswith("['") and line.endswith("']") else line for line in lines]
    
    cleaned_string = "\n".join(cleaned_lines)
    return cleaned_string

# Function to retry a function with exponential backoff
# Needed for the API calls as the API will restrict the number of requests if too many are made in a short period of time
def exponential_backoff_retry(func, *args, max_retries=5, initial_delay=4, backoff_factor=2, **kwargs):
    retries = 0
    delay = initial_delay
    while retries < max_retries:
        try:
            return func(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            print(f"Error occurred: {e}. Retrying in {delay} seconds.")
            time.sleep(delay)
            delay *= backoff_factor
            retries += 1
    raise RuntimeError("Max retries exceeded. Unable to fetch data.")



#######################################
# Functions for api calling functions #
#######################################

# Gets the real player name from the MCO API
# Will correct capitalization and fill in the remaining username if it is partially given
def get_real_player_name(username):
    url = f"https://minecraftonline.com/cgi-bin/getcorrectname?{username}"
    response = requests.get(url)
    if response.status_code == 200:
        if response.text.strip() == "NOTFOUND":
            return "NOTFOUND"
        elif response.text.strip() == "INVALID":
            return "INVALID"
        cleaned_response = response.text.strip().split("\n")
        result = remove_brackets(cleaned_response)
        return result
    else:
        return None

# Gets the player's last login time from the MCO API
def get_player_info_from_api(username):
    url = f"https://minecraftonline.com/cgi-bin/getplayerinfo?{username}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.strip().split("\n")
    else:
        return None

# Gets the player's head in 64x64 pixels from the MCO API
def get_player_head_from_api(username):
    url = f"https://minecraftonline.com/cgi-bin/getplayerhead.sh?{username}&64.png"
    response = requests.get(url)
    if response.status_code == 200:
        image = Image.open(io.BytesIO(response.content))
        return image
    else:
        return None

# Gets the player's head in 16x16 pixels from the MCO API
def get_player_head_from_api_small(username):
    url = f"https://minecraftonline.com/cgi-bin/getplayerhead.sh?{username}&16.png"
    response = requests.get(url)
    if response.status_code == 200:
        image = Image.open(io.BytesIO(response.content))
        return image
    else:
        return 

# Gets the player's information from the MCO wiki, speficically from that player's user page
def get_player_info_from_wiki(username):
    user_info = {}
    user_page_url = f"https://minecraftonline.com/wiki/User:{username}"
    
    try:
        response = requests.get(user_page_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            infobox = soup.find("table", class_="infobox")
            if infobox:
                rows = infobox.find_all("tr")
                for row in rows:
                    cells = row.find_all(["th", "td"])
                    if len(cells) == 2:
                        key = cells[0].text.strip()
                        value = cells[1].text.strip()
                        user_info[key] = value
            
            return user_info
        
        else:
            print(f"Failed to retrieve user information. Error code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    return None

# Gets the server's ban count from the MCO API
def get_ban_count_from_api():
    url = f"https://minecraftonline.com/cgi-bin/getbancount.sh"
    response = requests.get(url)
    if response.status_code == 200:
        cleaned_response = response.text.strip().split("\n")
        result = remove_brackets(cleaned_response)
        return result
    else:
        return None

# Gets the server's unique visitors count from the MCO API
def get_unique_visitors_from_api():
    url = f"https://minecraftonline.com/cgi-bin/getuniquevisitors.py"
    response = requests.get(url)
    if response.status_code == 200:
        cleaned_response = response.text.strip().split("\n")
        result = remove_brackets(cleaned_response)
        return result
    else:
        return None

# Gets the server's unique visitors count from the MCO API for the previous day
# This function is seemingly not accurate, seemingly giving the unique visitors count for the past few hours (if not less)
def get_yesterday_visitors_from_api():
    url = f"https://minecraftonline.com/cgi-bin/getuniqueyesterday.py"
    response = requests.get(url)
    if response.status_code == 200:
        cleaned_response = response.text.strip().split("\n")
        result = remove_brackets(cleaned_response)
        return result
    else:
        return None

# Gets the server's players that are currently online from the MCO API
def get_player_list_from_api(player_list):
    url = f"https://minecraftonline.com/cgi-bin/getplayerlist.sh"
    response = requests.get(url)
    if response.status_code == 200:
        request_list = response.text
        names = request_list.strip().split(", ")
        player_list.extend(names)
        return player_list
    else:
        return None



##############################
# Staff list functions/setup #
##############################

# Checks if the user is a former staff member
# Does this by checking the user's wiki page for the "Former staff" category
# This may not be accurate as the user may have been a staff member but not listed in the category
def is_user_former_staff(username, file_path):
    
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            pass 

    with open(file_path, "r") as file:
        if username in file.read().split("\n"):
            return True

    user_page_url = f"https://minecraftonline.com/wiki/User:{username}"

    try:
        response = requests.get(user_page_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            categories_section = soup.find("div", class_="mw-normal-catlinks")
            if categories_section:
                categories = categories_section.find_all("a")
                for category in categories:
                    if "Former_staff" in category.get("href", ""):
                        with open(file_path, "a") as file:
                            file.write(username + "\n")
                        return True

        else:
            print(f"Failed to retrieve user information. Error code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    return False



########################
# Player list functions#
########################

# Prints the player list in the GUI
def print_player_list(combined_player_list, frame):
    row = 0
    column = 0
    
    global adminlist  
    global modlist
    
    for username in combined_player_list:
        print_player_head(username, frame, row, column)
        
        if username in adminlist:
            fg_color = admin_color
        elif username in modlist:
            fg_color = mod_color
        else:
            fg_color = '#E1E1E1'

        username_label = tk.Label(frame, text=f"{username}", font=tkFont.Font(size=9), fg=fg_color, bg='#383838')
        username_label.grid(row=row, column=column + 1, padx=5, pady=2, sticky="w")
        row += 1
        
        if row >= 15:  # Change this value to adjust vertical distance
            row = 0
            column += 2

# Prints the player head in the GUI
def print_player_head(username, frame, row, column):
    time.sleep(4.0)
    image = get_player_head_from_api_small(username)
    if image:
        photo = ImageTk.PhotoImage(image)
                
        player_head_label = tk.Label(frame, image=photo, bg='#383838')
        player_head_label.image = photo
        player_head_label.grid(row=row, column=column, padx=5, pady=5)  # Place the image label in the frame
        print(username + " found and loaded")
    else:
        print("Error loading player head")