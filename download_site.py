# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import os
# import time


# url = "https://gtconsulting.bitrix24.ru/company/personal/user/228/tasks/"
# cookies_file_path = r'C:\Users\134\downloaded_page\cookies.txt'

# # Set up Chrome options
# chrome_options = Options()
# # Remove the headless mode option to see the browser window
# # chrome_options.add_argument("--headless")  # This line is commented out

# # Initialize the WebDriver
# service = Service()
# driver = webdriver.Chrome(service=service, options=chrome_options)

# # Open the URL to set cookies
# driver.get(url)

# # Load cookies from the file
# if os.path.exists(cookies_file_path):
#     with open(cookies_file_path, 'r', encoding='utf-8') as file:
#         for line in file:
#             # Strip whitespace and skip empty lines
#             line = line.strip()
#             if line and '=' in line:
#                 try:
#                     name, value = line.split('=', 1)
#                     driver.add_cookie({'name': name, 'value': value})
#                 except ValueError:
#                     print(f"Skipping malformed cookie line: {line}")
# else:
#     print(f"Cookies file not found: {cookies_file_path}")

# # Refresh the page to apply the cookies
# driver.get(url)

# # Wait for the login field to be present and fill it with "my_login"
# try:
#     login_field = WebDriverWait(driver, 15).until(
#         EC.presence_of_element_located((By.ID, "login"))
#     )
#     login_field.clear()  # Clear any existing text
#     login_field.send_keys("m_smirnov@yahoo.com")
# except Exception as e:
#     print(f"Error finding or interacting with login field: {e}")

# # Locate and click the submit button
# try:
#     submit_button = WebDriverWait(driver, 15).until(
#         EC.element_to_be_clickable((By.XPATH, "//button[@data-action='submit']"))
#     )
#     submit_button.click()
# except Exception as e:
#     print(f"Error finding or clicking submit button: {e}")

# # Wait for the password page to load and verify that it has changed
# try:
#     WebDriverWait(driver, 15).until(
#         EC.url_changes(url)
#     )
# except Exception as e:
#     print(f"Error waiting for URL change: {e}")
    
# # Give some time to process the form submission
# time.sleep(5)  # Adjust sleep time as needed
    

# # Wait for the password field to be present and interactable
# try:
#     password_field = WebDriverWait(driver, 15).until(
#         EC.visibility_of_element_located((By.ID, "password"))
#     )
#     password_field.clear()  # Clear any existing text
#     password_field.send_keys("Qazqwe11")
# except Exception as e:
#     print(f"Error finding or interacting with password field: {e}")

# # Locate and click the submit button
# try:
#     submit_button = driver.find_element(By.XPATH, "//button[@data-action='submit']")
#     submit_button.click()
# except Exception as e:
#     print(f"Error finding or clicking submit button: {e}")

# time.sleep(15)  # Adjust sleep time as needed

# # Save the page source (if needed)
# page_source = driver.page_source

# # Specify the file path where you want to save the HTML content
# file_path = r'C:\Users\134\downloaded_page\saved_page.html'

# # Write the page source to a file
# with open(file_path, 'w', encoding='utf-8') as file:
#     file.write(page_source)

# print(f"Webpage saved as {file_path}")

# # Close the browser
# driver.quit()
import pyautogui
import time

# Give the user some time to focus on the Chrome window
time.sleep(5)  # Adjust this as needed to switch to the Chrome window

# Simulate Ctrl+T to open a new tab
pyautogui.hotkey('ctrl', 't')

# Wait for the new tab to open
time.sleep(1)

# Type the URL
pyautogui.write("https://gtconsulting.bitrix24.ru/company/personal/user/228/tasks/")

# Press Enter to navigate to the URL
pyautogui.press('enter')

# Wait for the page to load
time.sleep(5)  # Adjust this depending on the speed of the website and your internet connection

# Simulate Ctrl+S to open the Save As dialog
pyautogui.hotkey('ctrl', 's')

# Wait for the Save As dialog to open
time.sleep(2)

# Type the filename (you may need to adjust the filename and path as needed)
pyautogui.write(r'C:\Users\134\downloaded_page\saved_page.html')

# Press Enter to save the file
pyautogui.press('enter')

# Optional: Wait a bit to ensure the file is saved
time.sleep(50)
