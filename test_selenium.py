from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

opts = Options()
# No headless mode
service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service, options=opts)
driver.get("https://www.google.com")

print("Browser opened successfully!")
driver.quit()
