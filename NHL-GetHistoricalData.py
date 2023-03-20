from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import datetime
import time 

driver = webdriver.Chrome('C:/Users/RyanC/Downloads/chromedriver_win32/chromedriver.exe')

driver.get("https://www.nhl.com/info/teams")
driver.implicitly_wait(5)
teamCityElements = driver.find_elements(By.CSS_SELECTOR, 'a > span.team-city')
teamNameElements = driver.find_elements(By.CSS_SELECTOR, 'a > span.team-name')

# BECAUSE KRAKEN IS FUCKED UP ON NHL WEBSITE
kraken = driver.find_element(By.CSS_SELECTOR, '#token-E566BFA8BF45ABB169280 > a > span')

teams = []
fullTeams = []
for name, city in zip(teamNameElements, teamCityElements):
    team = city.text + ' ' + name.text
    fullTeams.append(team)
    teams.append(name.text)

fullTeams.append(kraken.text)
teams.append(kraken.text.split()[1])

date = ''
masterDF = pd.DataFrame(columns=['Date', 'Visitor', 'Visitor G', 'Home', 'Home G', 'Visitor Open', 'Visitor Best', 'Home Open', 'Home Best'])

driver.get("https://www.actionnetwork.com/nhl/odds")

while (date != '2022-10-07'):
    driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div[2]/div[2]/div[2]/div[1]/button[1]').click()
    date = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div[2]/div[2]/div[2]/div[1]/span').text
    if ('Oct' in date or 'Nov' in date or 'Dec' in date):
        date = date + ' 2022'
    else:
        date = date + " 2023"

    date = datetime.datetime.strptime(date, '%a %b %d %Y')
    date = datetime.datetime.strftime(date, '%Y-%m-%d')
    print(date)
    time.sleep(3)
    try:
        df=pd.read_html(driver.find_element(By.CLASS_NAME, "css-1uek3nh").get_attribute('outerHTML'))[0]
        df = df[['Scheduled', 'Open', 'Best Odds']]
        df = df.iloc[::2]
        df = df.reset_index(drop=True)


        visitor = []
        visitorG = []
        home = []
        homeG = []
        visitorOpen = []
        visitorBest = []
        homeOpen = []
        homeBest = []
        dateCol = []

        for index, row in df.iterrows():
            scheduled = row['Scheduled']
            open = row['Open']
            best = row['Best Odds']
            indexT1 = -1
            team1 = ''
            indexT2 = -1
            team2 = ''
            
            fullTeamI1 = 0
            fullTeamI2 = 0

            # Get team Names
            for idx, team in enumerate(teams):
                if(scheduled.find(team) > -1):
                    if(indexT1 < 0):
                        indexT1 = scheduled.find(team)
                        team1 = team
                        fullTeamI1 = idx
                    else:
                        indexT2 = scheduled.find(team)
                        team2 = team
                        fullTeamI2 = idx

            # Append to lists and get team Goals

            if(indexT1 < indexT2):
                vis = scheduled[:indexT2]
                h = scheduled[indexT2:]

                visitor.append(fullTeams[fullTeamI1])
                home.append(fullTeams[fullTeamI2])
                visitorG.append(vis[len(vis)-1])
                homeG.append(h[len(h)-1])
            else:
                vis = scheduled[:indexT1]
                h = scheduled[indexT1:]
                visitor.append(fullTeams[fullTeamI2])
                home.append(fullTeams[fullTeamI1])
                visitorG.append(vis[len(vis)-1])
                homeG.append(h[len(h)-1])
            visitorOpen.append(open[:4])
            homeOpen.append(open[4:])
            visitorBest.append(best[:4])
            homeBest.append(best[4:])
            
            dateCol.append(date)
            
        df['Date'] = dateCol
        df['Visitor'] = visitor
        df['Visitor G'] = visitorG
        df['Home'] = home
        df['Home G'] = homeG
        df['Visitor Open'] = visitorOpen
        df['Visitor Best'] = visitorBest
        df['Home Open'] = homeOpen
        df['Home Best'] = homeBest

        df = df[['Date', 'Visitor', 'Visitor G', 'Home', 'Home G', 'Visitor Open', 'Visitor Best', 'Home Open', 'Home Best']]
        masterDF = pd.concat([df, masterDF])
    except:
        continue

driver.close()
masterDF.to_csv('oddsData.csv')