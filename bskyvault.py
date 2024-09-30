from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def post_to_bsky(file_path, account_id, password):
    # Set up the WebDriver (update the path if necessary)
    driver = webdriver.Chrome()  # or webdriver.Firefox(), etc.

    try:
        # Open the Bluesky login page
        driver.get("https://bsky.social/")

        # Wait for the page to load
        time.sleep(2)

        # Locate the login fields and submit the credentials
        driver.find_element(By.NAME, "Sinstokill").send_keys(account_id)
        driver.find_element(By.NAME, "Zer@8114").send_keys(password)
        driver.find_element(By.NAME, "Zer@8114").send_keys(Keys.RETURN)

        # Wait for login to complete
        time.sleep(5)

        # Read content from the text file
        with open(file_path, 'r') as file:
            content = file.read()

        # Locate the post box and input the content
        post_box = driver.find_element(By.XPATH, "//textarea")  # Adjust the selector as needed
        post_box.send_keys(content)

        # Submit the post
        post_box.send_keys(Keys.RETURN)

        print("Post successful!")

    finally:
        # Close the driver
        time.sleep(5)  # Give some time to see the result
        driver.quit()

# Usage
post_to_bsky("C:\\Users\\msgok\\OneDrive\\Desktop\\sql dbms tables.txt", "Sinstokill", "Zer@8114")
