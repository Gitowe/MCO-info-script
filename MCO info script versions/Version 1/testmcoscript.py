import requests
import datetime
import pytz
import tkinter as tk
import pyperclip  # Import the pyperclip module
import openpyxl

entry = None
result_text = None
copy_button = None

def get_player_info(username):
    url = f"https://minecraftonline.com/cgi-bin/getplayerinfo?{username}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.strip().split("\n")
    else:
        return ["NOTFOUND"]

def convert_seconds(seconds):
    years = seconds // (365 * 24 * 3600)
    seconds %= 365 * 24 * 3600
    days = seconds // (24 * 3600)
    seconds %= 24 * 3600
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return years, days, hours, minutes, seconds

def convert_unix_timestamp(timestamp):
    cst = pytz.timezone('US/Central')
    converted_time = datetime.datetime.fromtimestamp(timestamp, tz=cst)
    return converted_time.strftime('%B %d, %Y - %I:%M:%S %p')

def convert_to_mm_dd_yyyy(timestamp):
    # Convert the timestamp to MM/DD/YYYY format
    converted_time = datetime.datetime.fromtimestamp(timestamp)
    return converted_time.strftime('%m/%d/%Y')

def clear_ui():
    for widget in window.winfo_children():
        widget.destroy()

def show_menu():
    # Clear the previous UI elements
    clear_ui()

    # Create the menu buttons
    player_info_button = tk.Button(window, text="Player Info", command=show_player_info_screen)
    player_info_button.pack(pady=10)

    update_sheet_button = tk.Button(window, text="Update Sheet", command=update_sheet)  # Define the update_sheet_function
    update_sheet_button.pack(pady=10)
def on_enter(event=None):
    display_player_info()

def show_player_info_screen():
    global entry
    global result_text
    global copy_button
    
    # Clear the previous UI elements
    clear_ui()

    # Create the elements for Player Info screen
    label = tk.Label(window, text="Enter Minecraft username:")
    label.pack(pady=15)

    entry = tk.Entry(window)
    entry.pack(pady=10)
    
    entry.bind("<Return>", on_enter)
    
    spacer = tk.Label(window, text="")
    spacer.pack()

    button = tk.Button(window, text="Get Info", command=display_player_info)
    button.pack(pady=5)
    
    copy_button = tk.Button(window, text="Copy Info", command=copy_player_info)
    copy_button.pack_forget
    
    result_text = tk.StringVar()
    result_label = tk.Label(window, textvariable=result_text)
    result_label.pack()
    
    spacer.pack()

    back_button = tk.Button(window, text="Back", command=show_menu)
    back_button.pack(pady=5)

def update_sheet():
    global entry_filename
    global entry_sheetname
    
    clear_ui()

    label_filename = tk.Label(window, text="Enter Excel file name (with extension):")
    label_filename.pack()

    entry_filename = tk.Entry(window)
    entry_filename.pack()

    label_sheetname = tk.Label(window, text="Enter sheet name:")
    label_sheetname.pack()

    entry_sheetname = tk.Entry(window)
    entry_sheetname.pack()

    button_update_excel = tk.Button(window, text="Update Excel", command=update_excel)
    button_update_excel.pack()

    button_back = tk.Button(window, text="Back", command=show_menu)
    button_back.pack()
    
def update_excel():
    try:
        # Get the Excel file name and sheet name from the user
        excel_file = input("Enter the Excel file name (with extension): ")
        sheet_name = input("Enter the sheet name: ")

        # Load the workbook
        workbook = openpyxl.load_workbook(excel_file)
        sheet = workbook[sheet_name]

        # Find the column index of "Name"
        name_column_index = None
        for cell in sheet[2]:
            if cell.value == "Name":
                name_column_index = cell.column
                break

        if name_column_index is None:
            print("Column 'Name' not found in the specified sheet.")
            return

        # Get all usernames from the "Name" column
        usernames = [cell.value for cell in sheet[name_column_index][2:]]

        # Find the column index to input the first seen date (2 columns to the right of "Name")
        first_seen_column_index = name_column_index + 2

        # Iterate through usernames and update the first seen date column
        for row_index, username in enumerate(usernames, start=3):
            player_info = get_player_info(username)
            if player_info[0] != "NOTFOUND":
                join_date = int(player_info[0])
                formatted_date = convert_unix_timestamp(join_date).split(' - ')[0]  # Extract date only

                # Write the formatted date to the Excel sheet
                sheet.cell(row=row_index, column=first_seen_column_index).value = formatted_date

        # Save the changes to the Excel file
        workbook.save(excel_file)
        print("Update completed successfully.")
    except Exception as e:
        print(f"Error occurred: {e}")

def copy_player_info():
    # Get the player information
    username = entry.get()
    player_info = get_player_info(username)

    try:
        # Extracting player name and first seen date if the info is in the expected format
        join_date = int(player_info[0])

         # Format the information to be copied
        copy_text = f"{username}\n{convert_to_mm_dd_yyyy(join_date)}"

        # Copy the formatted information to the clipboard
        pyperclip.copy(copy_text)
    except IndexError as e:
        print(f"Error: {e}")


def display_player_info():
    global entry
    global result_text
    global copy_button
    
    username = entry.get()
    player_info = get_player_info(username)
    
    if player_info[0] == "NOTFOUND":
        result_text.set("Player not found.")
    else:
        join_date = int(player_info[0])
        last_seen = int(player_info[1])
        time_seconds = int(player_info[2])
        banned_info = player_info[3].split(";") if len(player_info) > 3 else ["NOTBANNED"]

        result = f"Player Information for {username}:\n"
        result += f"Joined: {convert_unix_timestamp(join_date)}\n"
        result += f"Last Seen: {convert_unix_timestamp(last_seen)}\n"

        years, days, hours, minutes, seconds = convert_seconds(time_seconds)
        if years > 0:
            result += f"Time Played: Years: {years}, Days: {days}, Hours: {hours}, Minutes: {minutes}, Seconds: {seconds}\n"
        else:
            result += f"Time Played: Days: {days}, Hours: {hours}, Minutes: {minutes}, Seconds: {seconds}\n"

        result += f"Ban Status: {'BANNED' if banned_info[0] != 'NOTBANNED' else 'NOT BANNED'}\n"

        if banned_info[0] != "NOTBANNED":
            ban_date = int(banned_info[1])
            result += f"Ban Info: Banned by {banned_info[0]} on {convert_unix_timestamp(ban_date)} with the reason: {banned_info[2]}\n"
        
        result += f"\nPlayer Calculations for {username}:\n"
        current_time = datetime.datetime.now().timestamp()
        time_since_joined = int(current_time - join_date)
        years, days, hours, minutes, seconds = convert_seconds(time_since_joined)
        if years > 0:
            result += f"Time Since Joined: Years: {years}, Days: {days}, Hours: {hours}, Minutes: {minutes}, Seconds: {seconds}\n"
        else:
            result += f"Time Since Joined: Days: {days}, Hours: {hours}, Minutes: {minutes}, Seconds: {seconds}\n"

        if banned_info[0] != "NOTBANNED":
            time_since_ban = int(current_time - int(banned_info[1]))
            years, days, hours, minutes, seconds = convert_seconds(time_since_ban)
            if years > 0:
                result += f"Time Since Ban: Years: {years}, Days: {days}, Hours: {hours}, Minutes: {minutes}, Seconds: {seconds}\n"
            else:
                result += f"Time Since Ban: Days: {days}, Hours: {hours}, Minutes: {minutes}, Seconds: {seconds}\n"

        copy_button.pack()
        result_text.set(result)


window = tk.Tk()
window.title("MCO Player Information")

window.geometry("600x500") 

show_menu()

window.mainloop()