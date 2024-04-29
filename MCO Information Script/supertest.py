import os
import requests
from bs4 import BeautifulSoup

def fetch_and_store_players(url, player_type):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all the links within the category page
        links = soup.find_all("a")

        # Filter out the links that represent user pages (start with /wiki/User:)
        user_links = [link.get("href")[11:] for link in links if link.get("href") and link.get("href").startswith("/wiki/User:")]

        # Remove duplicates by converting to a set and then back to a list
        user_list = list(set(user_links))

        # Sort the list alphabetically
        user_list.sort()

        # Read existing content from the text file
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

        # Check if the player type header exists in the file
        header_index = None
        for i, line in enumerate(lines):
            if line.strip() == f"-[{player_type}]-":
                header_index = i
                break

        # Prepare the content to be written to the file
        new_content = f"-[{player_type}]-\n"
        for user in user_list:
            new_content += user + "\n"
        new_content += "\n"

        # Update the content in the file based on whether the header exists or not
        if header_index is not None:
            # Replace the existing content under the player type header
            lines[header_index+1:] = new_content.splitlines(True)[1:]
        else:
            # Add the new player type header and content at the end of the file
            lines.append(new_content)

        # Write the updated content back to the file
        with open("players.txt", "w") as file:
            file.writelines(lines)

        print(f"Names of {player_type} have been saved/updated in players.txt.")
    else:
        print("Failed to fetch the page. Status code:", response.status_code)


def read_players(player_type):
    # Read content from the text file
    with open("players.txt", "r") as file:
        lines = file.readlines()

    # Initialize a list to store player names
    player_names = []

    # Flag to check if the current line belongs to the specified player type
    player_type_found = False

    # Iterate through the lines in the file
    for line in lines:
        if line.strip() == f"-[{player_type}]-":
            player_type_found = True
        elif player_type_found:
            # If player type header is found, add subsequent names until next header is encountered
            if line.strip() == "":
                break
            player_names.append(line.strip())

    return player_names


# Example usage:
fetch_and_store_players("https://minecraftonline.com/wiki/Category:Former_staff", "Former Staff")
fetch_and_store_players("https://minecraftonline.com/wiki/Category:God_donor", "God Donor")

print("Names of Former Staff:", read_players("Former Staff"))
print("\nNames of God Donors:", read_players("God Donor"))