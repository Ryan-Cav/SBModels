from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

driver = webdriver.Chrome('C:/Users/RyanC/Downloads/chromedriver_win32/chromedriver.exe')


driver.get("https://www.nhl.com/info/teams")
driver.implicitly_wait(5)
teamElements = driver.find_elements(By.CSS_SELECTOR, 'a > span.team-name')
teamElements.append(driver.find_element(By.XPATH, '//*[@id="token-D830792472F4E73748482"]/a/span[2]'))
teams = []
for element in teamElements:
    teams.append(element.text)

driver.get("https://www.actionnetwork.com/nhl/odds")


# click for previous date
# driver.find_element(By.CSS_SELECTOR, "[aria-label=Previous Date]").click()

df=pd.read_html(driver.find_element(By.CLASS_NAME, "css-1uek3nh").get_attribute('outerHTML'))[0]
df = df[['Scheduled', 'Open', 'Best Odds']]
df = df.iloc[::2]
df = df.reset_index(drop=True)
print(df)


# driver.close()