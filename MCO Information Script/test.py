import requests
from bs4 import BeautifulSoup

# Define the URL of the category page
url = "https://minecraftonline.com/wiki/Category:Former_staff"

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
    
    user_list.sort()

    # Write the list of user names to a text file
    with open("former_staff_names.txt", "w") as file:
        for user in user_list:
            file.write(user + "\n")

    print("Names of former staff members have been saved to former_staff_names.txt.")
else:
    print("Failed to fetch the page. Status code:", response.status_code)