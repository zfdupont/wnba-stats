import pandas as pd
import numpy as np
from urllib.request import urlopen
from bs4 import BeautifulSoup
from collections import defaultdict

name_to_abv = {
    'New York Liberty': 'NYL',
    'Connecticut Sun': 'CON',
    'Minnesota Lynx': 'MIN',
    'Seattle Storm': 'SEA',
    'Las Vegas Aces': 'LVA',
    'Phoenix Mercury': 'PHO',
    'Indiana Fever': 'IND',
    'Chicago Sky': 'CHI',
    'Atlanta Dream': 'ATL',
    'Washington Mystics': 'WAS',
    'Los Angeles Sparks': 'LAS',
    'Dallas Wings': 'DAL'
}

def get_rookies(team_name):
    from urllib.request import urlopen
    from bs4 import BeautifulSoup
    html = urlopen(f'https://www.basketball-reference.com/wnba/teams/{name_to_abv[team_name]}/2024.html')
            
    # create beautiful soup object from HTML#roster > thead > tr > th.poptip.sort_default_asc.center.sort_col.sorttable_sorted
    soup = BeautifulSoup(html, features="lxml")

    roster_table = soup.select_one('table#roster')
    cols = [th.getText() for th in roster_table.select('thead > tr > th')][1:]
    table_data = [th.getText() for th in roster_table.select('tbody > tr > td')]

    df = pd.DataFrame([table_data[i:i+len(cols)] for i in range(0, len(table_data), len(cols))], columns=cols)
    return list(df[df['Exp'] == 'R']['Player'].values)

def get_team_roster(team_name):
    
    # collect HTML data
    html = urlopen(f'https://www.basketball-reference.com/wnba/teams/{name_to_abv[team_name]}/2024.html')
            
    # create beautiful soup object from HTML#roster > thead > tr > th.poptip.sort_default_asc.center.sort_col.sorttable_sorted
    soup = BeautifulSoup(html, features="lxml")

    roster_table = soup.select_one('table#roster')
    ncols = len([th.getText() for th in roster_table.select('thead > tr > th')][1:])
    table_data = [th.getText() for th in roster_table.select('tbody > tr > td')]

    positions = defaultdict(lambda: '?') | {name: pos for name, pos in [table_data[i:i+2] for i in range(0, len(table_data), ncols)]}

    totals_table = soup.select_one('table#totals')
    cols = [th.getText() for th in totals_table.select('thead > tr > th')][1:]
    table_data = [th.getText() for th in totals_table.select('tbody > tr > td')]
    totals_df = pd.DataFrame([table_data[i:i+len(cols)] for i in range(0, len(table_data), len(cols))], columns=cols)
    totals_df['Pos'] = totals_df['Player'].map(lambda x: positions[x])
    totals_df.index += 1
    return totals_df.rename(columns={'Player': 'Name'})


    
