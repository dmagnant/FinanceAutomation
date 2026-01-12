from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time, os

def search_google():
    options = webdriver.ChromeOptions()
    
    # Keep browser open after script ends
    
    # Open in incognito mode
    options.add_argument("start-maximized")
    options.add_experimental_option("detach", True)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    options.add_argument(rf"user-data-dir={os.getenv('LOCALAPPDATA')}\Google\Chrome\User Data")
    # Set up Chrome driver with options
    driver = webdriver.Chrome(options=options)
    
    try:
        # Open Google
        driver.get("https://www.google.com")
        
        
        # Wait for the search box to be present
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        
        # Type the search query with human-like delays
        for char in "selenium automation":
            search_box.send_keys(char)
            time.sleep(0.1)  # Small delay between keystrokes
        
        # Submit the search
        time.sleep(1)  # Pause before submitting
        search_box.send_keys(Keys.RETURN)
        
        # Wait a bit to see the results
        time.sleep(3)
        
        print("Search completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
if __name__ == "__main__":
    search_google()
