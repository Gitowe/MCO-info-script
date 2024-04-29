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



#######################################
# Functions for api calling functions #
#######################################



def remove_brackets(input_string):
    lines = input_string
    cleaned_lines = [line[2:-2] if line.startswith("['") and line.endswith("']") else line for line in lines]
    
    cleaned_string = "\n".join(cleaned_lines)
    return cleaned_string

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

def get_player_info_from_api(username):
    url = f"https://minecraftonline.com/cgi-bin/getplayerinfo?{username}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.strip().split("\n")
    else:
        return None
    
def get_player_head_from_api(username):
    url = f"https://minecraftonline.com/cgi-bin/getplayerhead.sh?{username}&64.png"
    response = requests.get(url)
    if response.status_code == 200:
        image = Image.open(io.BytesIO(response.content))
        return image
    else:
        return None
    
def get_player_head_from_api_small(username):
    url = f"https://minecraftonline.com/cgi-bin/getplayerhead.sh?{username}&16.png"
    response = requests.get(url)
    if response.status_code == 200:
        image = Image.open(io.BytesIO(response.content))
        return image
    else:
        return 

# Gets information from the MCO wiki (specifically from the userpage)
def get_player_info_from_wiki(username):
    user_info = {}
    user_page_url = f"https://minecraftonline.com/wiki/User:{username}"
    
    try:
        response = requests.get(user_page_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the user infobox
            infobox = soup.find("table", class_="infobox")
            if infobox:
                rows = infobox.find_all("tr")
                for row in rows:
                    # Extracting key-value pairs from the infobox
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

def get_ban_count_from_api():
    url = f"https://minecraftonline.com/cgi-bin/getbancount.sh"
    response = requests.get(url)
    if response.status_code == 200:
        cleaned_response = response.text.strip().split("\n")
        result = remove_brackets(cleaned_response)
        return result
    else:
        return None
    
def get_unique_visitors_from_api():
    url = f"https://minecraftonline.com/cgi-bin/getuniquevisitors.py"
    response = requests.get(url)
    if response.status_code == 200:
        cleaned_response = response.text.strip().split("\n")
        result = remove_brackets(cleaned_response)
        return result
    else:
        return None
    
def get_yesterday_visitors_from_api():
    url = f"https://minecraftonline.com/cgi-bin/getuniqueyesterday.py"
    response = requests.get(url)
    if response.status_code == 200:
        cleaned_response = response.text.strip().split("\n")
        result = remove_brackets(cleaned_response)
        return result
    else:
        return None
    
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



mod_file = "modlist.txt"
modlist = []
admin_file = "adminlist.txt"
adminlist = []
formerstaff_file = "formerstaff.txt"
formerstaff = []

def get_staff_list_from_api(url, global_list, file_path):
    
    if os.path.exists(file_path):
        # Read from the existing file
        with open(file_path, "r") as file:
            global_list.extend(file.read().strip().split("\n"))
    else:
        response = requests.get(url)
        if response.status_code == 200:
            names = response.text.strip().split("\n")
            global_list.extend(names)
            # Write the data into the file
            with open(file_path, "w") as file:
                file.write("\n".join(names))
        else:
            print("Failed to retrieve names from the website.")

get_staff_list_from_api("https://minecraftonline.com/cgi-bin/getadminlist.sh", adminlist, admin_file)
get_staff_list_from_api("https://minecraftonline.com/cgi-bin/getmodlist.sh", modlist, mod_file)

url = "https://minecraftonline.com/wiki/Category:Former_staff"

# Send a GET request to the URL
response = requests.get(url)

def get_former_staff_list_from_wiki(url, global_list, file_path):
    response = requests.get(url)
    
    if response.status_code == 200:

        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all("a")

        user_links = [link.get("href")[11:] for link in links if link.get("href") and link.get("href").startswith("/wiki/User:")]
        user_list = list(set(user_links))
        user_list.sort()

        with open(file_path, "w") as file:
            for user in user_list:
                file.write(user + "\n")

def get_former_staff_list_from_wiki(url, global_list, file_path):
    
    if os.path.exists(file_path):
        # Read from the existing file
        with open(file_path, "r") as file:
            global_list.extend(file.read().strip().split("\n"))
    else:
        response = requests.get(url)
        if response.status_code == 200:
            names = response.text.strip().split("\n")
            global_list.extend(names)
            # Write the data into the file
            with open(file_path, "w") as file:
                file.write("\n".join(names))
        else:
            print("Failed to retrieve names from the website.")

def get_player_list_from_wiki(url):
    return

def is_user_former_staff(username, file_path):
    # Check if former staff list file exists, if not create one
    
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            pass  # Create an empty file

    # Check if the user is listed in the former staff list file
    with open(file_path, "r") as file:
        if username in file.read().split("\n"):
            return True  # User is a former staff

    user_page_url = f"https://minecraftonline.com/wiki/User:{username}"

    try:
        response = requests.get(user_page_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Search for the categories section
            categories_section = soup.find("div", class_="mw-normal-catlinks")
            if categories_section:
                # Check if "Former staff" category is present
                categories = categories_section.find_all("a")
                for category in categories:
                    if "Former_staff" in category.get("href", ""):
                        # Add the user to the former staff list file
                        with open(file_path, "a") as file:
                            file.write(username + "\n")
                        return True  # User is a former staff

        else:
            print(f"Failed to retrieve user information. Error code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    return False



############################
# God list functions/setup #
############################