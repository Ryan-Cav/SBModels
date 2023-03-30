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
driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div[2]/div[2]/div[1]/div/div[2]/select').click()
time.sleep(1)
driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div[2]/div[2]/div[1]/div/div[2]/select/option[4]').click()

while (date != '2023-03-25'):
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
    #try:
    df=pd.read_html(driver.find_element(By.CLASS_NAME, "css-1uek3nh").get_attribute('outerHTML'))[0]
    
    df = df[['Scheduled', 'Open', 'Best Odds']]
    
    o = df['Open']
    bo = df['Best Odds']
    df = df.iloc[::4]
    df = df.reset_index(drop=True)
    sch = df['Scheduled']
    print(o)
    # Team name and Goals
    visitor = []
    visitorG = []
    home = []
    homeG = []

    # Visitor Odds
    vSpread = []
    vSpreadOpen = []
    vSpreadBest = []
    vSpreadOpenOdds = []
    vSpreadBestOdds = []
    vMLOpen = []
    vMLBest = []

    # Home Odds
    hSpread = []
    hSpreadOpen = []
    hSpreadBest = []
    hSpreadOpenOdds = []
    hSpreadBestOdds = []
    hMLOpen = []
    hMLBest = []

    # Over/Under
    OverOpen = []
    UnderOpen = []
    OverBest = []
    UnderBest = []
    OverOpenOdds = []
    OverBestOdds = []
    UnderOpenOdds = []
    UnderBestOdds = []

    # Date col
    dateCol = []

    index = 0

    for scheduled in sch:
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
        
        openSpread = o[index]
        bestSpread = bo[index]
        index += 1
        openOverUnder = o[index]
        bestOverUnder = bo[index]
        index += 1
        openML = o[index]
        bestML = bo[index]
        index += 2


        # Spread
        vOpenTemp = openSpread[:8]
        hOpenTemp = openSpread[8:]
        vBestTemp = bestSpread[:8]
        hBestTemp = bestSpread[8:]

        vSpreadOpen.append(vOpenTemp[:4])
        hSpreadOpen.append(hOpenTemp[:4])
        vSpreadBest.append(vBestTemp[:4])
        hSpreadBest.append(hBestTemp[:4])
        vSpreadOpenOdds.append(vOpenTemp[4:])
        vSpreadBestOdds.append(hOpenTemp[4:])
        hSpreadOpenOdds.append(vBestTemp[4:])
        hSpreadBestOdds.append(hBestTemp[4:])

        # O/U
        OverOpenTemp = openOverUnder[:openOverUnder.index('u')]
        UnderOpenTemp = openOverUnder[openOverUnder.index('u'):]
        OverBestTemp = bestOverUnder[:openOverUnder.index('u')]
        UnderBestTemp = bestOverUnder[openOverUnder.index('u'):]
        
        OverOpen.append(OverOpenTemp[:4])
        UnderOpen.append(UnderOpenTemp[:4])
        OverBest.append(OverBestTemp[:4])
        UnderBest.append(UnderBestTemp[:4])
        OverOpenOdds.append(OverOpenTemp[4:])
        OverBestOdds.append(OverBestTemp[4:])
        UnderOpenOdds.append(UnderOpenTemp[4:])
        UnderBestOdds.append(UnderBestTemp[4:])

        # ML
        vMLOpen.append(openML[:4])
        vMLBest.append(bestML[:4])
        hMLOpen.append(openML[4:])
        hMLBest.append(bestML[4:])

        dateCol.append(date)
    
    df['Date'] = dateCol
    df['Visitor'] = visitor
    df['Visitor G'] = visitorG
    df['Home'] = home
    df['Home G'] = homeG

    df['V Spread Open'] = vSpreadOpen
    df['V Spread Best'] = vSpreadBest
    df['V Spread Open Odds'] = vSpreadOpenOdds
    df['V Spread Best Odds'] = vSpreadBestOdds
    df['H Spread Open'] = hSpreadOpen
    df['H Spread Best'] = hSpreadBest
    df['H Spread Open Odds'] = hSpreadOpenOdds
    df['H Spread Best Odds'] = hSpreadBestOdds

    df['Over Open'] = OverOpen
    df['Over Best'] = OverBest
    df['Under Open'] = UnderOpen
    df['Under Best'] = UnderBest
    df['Over Open Odds'] = OverOpenOdds
    df['Over Best Odds'] = OverBestOdds
    df['Under Open Odds'] = UnderOpenOdds
    df['Under Best Odds'] = UnderBestOdds

    df['Visitor Open'] = vMLOpen
    df['Visitor Best'] = vMLBest
    df['Home Open'] = hMLOpen
    df['Home Best'] = hMLBest



    # for index, row in df.iterrows():
    #     scheduled = row['Scheduled']
    #     open = row['Open']
    #     best = row['Best Odds']
    #     indexT1 = -1
    #     team1 = ''
    #     indexT2 = -1
    #     team2 = ''
        
    #     fullTeamI1 = 0
    #     fullTeamI2 = 0

    #     # Get team Names
    #     for idx, team in enumerate(teams):
    #         if(scheduled.find(team) > -1):
    #             if(indexT1 < 0):
    #                 indexT1 = scheduled.find(team)
    #                 team1 = team
    #                 fullTeamI1 = idx
    #             else:
    #                 indexT2 = scheduled.find(team)
    #                 team2 = team
    #                 fullTeamI2 = idx

    #     # Append to lists and get team Goals

    #     if(indexT1 < indexT2):
    #         vis = scheduled[:indexT2]
    #         h = scheduled[indexT2:]

    #         visitor.append(fullTeams[fullTeamI1])
    #         home.append(fullTeams[fullTeamI2])
    #         visitorG.append(vis[len(vis)-1])
    #         homeG.append(h[len(h)-1])
    #     else:
    #         vis = scheduled[:indexT1]
    #         h = scheduled[indexT1:]
    #         visitor.append(fullTeams[fullTeamI2])
    #         home.append(fullTeams[fullTeamI1])
    #         visitorG.append(vis[len(vis)-1])
    #         homeG.append(h[len(h)-1])
    #     visitorOpen.append(open[:4])
    #     homeOpen.append(open[4:])
    #     visitorBest.append(best[:4])
    #     homeBest.append(best[4:])
        
    #     dateCol.append(date)
        
    
    # df['Visitor Open'] = visitorOpen
    # df['Visitor Best'] = visitorBest
    # df['Home Open'] = homeOpen
    # df['Home Best'] = homeBest
    df = df.drop(columns=['Scheduled', 'Open', 'Best Odds'])
    masterDF = pd.concat([df, masterDF])
    # except:
    #     continue

driver.close()
print(masterDF)
#masterDF.to_csv('oddsData.csv')