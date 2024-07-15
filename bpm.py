from constants import *
import pandas as pd
import numpy as np
from constants import *

pd.set_option('mode.chained_assignment', None)
pd.set_option('display.max_columns', None)

def calculate_bpm(team_stats, roster):
    # roster = pd.read_csv('stats2.csv', index_col=0)

    for stat in ['PTS', 'FGA', 'FTA', 'TRB', 'STL', 'PF', 'AST', 'BLK', 'MP']:
        team_stats[stat] = roster[stat].sum()

    team_stats['FTA/FGA'] = bpm_coefficients['Pos 1']['FTA']/bpm_coefficients['Pos 1']['FGA']
    team_stats['Pts/TSA'] = team_stats['PTS']/(team_stats['FGA']+team_stats['FTA']*team_stats['FTA/FGA'])

    # adjust for team shooting context
    roster['Possessions'] = roster['MP']*(team_stats['Pace']/48)
    roster['TSA'] = roster['FGA']+roster['FTA']*team_stats['FTA/FGA']
    roster['Pt/TSA'] = roster['PTS']/roster['TSA']
    roster['AdjPTS'] = ((roster['Pt/TSA']-team_stats['Pts/TSA'])+1)*roster['TSA']
    roster['ThreshPts'] = roster['TSA']*(roster['Pt/TSA'] - (team_stats['Pts/TSA'] + off_role_coefficients['PtThresh']))

    team_stats['ThreshPts'] = roster['ThreshPts'].sum()

    # calculated stats per 100 poss
    roster['AdjPt'] = roster['AdjPTS']/roster['Possessions']*100
    for stat in ['FGA', 'FTA', '3P', 'AST', 
                'TOV', 'ORB', 'DRB', 'TRB', 'STL', 'BLK', 'PF']:
        roster[f'Adj{stat}'] = roster[stat]/roster['Possessions']*100

    # % stats
    roster['%Min'] = roster['MP']/(team_stats['MP']/5)
    for stat in ['TRB', 'STL', 'PF', 'AST', 'BLK', 'ThreshPts']:
        roster[f'%{stat}'] = roster[stat]/team_stats[stat]/roster['%Min']
        roster[f'%{stat}'].fillna(0, inplace=True)


    roster['PosNum'] = roster['Pos'].map({'PG': 1, 'SG': 2, 'SF': 3, 'PF': 4, 'C': 5,
                                        'G': 1.5, 'G-F': 3, 'F-G': 3, 'F': 3.5, 'F-C': 4.5, 'C-F': 4.5})

    # Estimate true positions
    stats = ['%TRB', '%STL', '%PF', '%AST', '%BLK']
    pos_est = pos_coefficients['INT'] + roster[stats].dot([pos_coefficients[f'{st}'] for st in stats])

    # some wnba rosters are poorly filled...
    df = pd.DataFrame(roster['PosNum'])
    df['fill'] = pos_est
    roster['PosNum'] = df.fillna(method='bfill', axis=1).round(1)['PosNum']


    # adjust for minutes
    MINUTE_FLOOR = 50
    pos_est = (pos_est*roster['MP']+roster['PosNum']*MINUTE_FLOOR)/(roster['MP']+MINUTE_FLOOR)
    trim = pos_est.clip(lower=1, upper=5)
    team_avg = trim.dot(roster['MP'])/team_stats['MP']

    while team_avg > 3.005:
        pos_est = pos_est - (team_avg-3)
        trim = pos_est.clip(lower=1, upper=5)
        team_avg = trim.dot(roster['MP'])/team_stats['MP']


    roster['EstPos'] = trim.round(1)

    # estimate offensive role
    DEFAULT_OFF_POS = 4

    off_role_est = off_role_coefficients['INT'] + off_role_coefficients['%AST']*roster['%AST'] + off_role_coefficients['%Thresh']*roster['%ThreshPts']
    # adjust for minutes
    off_role_est = (off_role_est*roster['MP']+DEFAULT_OFF_POS*MINUTE_FLOOR)/(roster['MP']+MINUTE_FLOOR)
    trim = off_role_est.clip(1,5)
    team_avg = trim.dot(roster['MP'])/team_stats['MP']

    while team_avg > 3.005:
        off_role_est = off_role_est - (team_avg-3)
        trim = off_role_est.clip(lower=1, upper=5)
        team_avg = trim.dot(roster['MP'])/team_stats['MP'] 
        # print(team_avg)

    roster['OffRole'] = trim

    raw_bpm = roster[['Name', 'EstPos', 'OffRole']]

    for stat in bpm_coefficients['Pos 1'].keys():
        if stat in ['FGA', 'FTA']:
            pos_df = raw_bpm['OffRole']
        else:
            pos_df = raw_bpm['EstPos']
        raw_bpm[stat] = ((5-pos_df)*bpm_coefficients['Pos 1'][stat] + (pos_df-1)*bpm_coefficients['Pos 5'][stat])/4
        raw_bpm[stat] = raw_bpm[stat]

    # Raw BPM calculation

    raw_bpm['Scoring'] = pd.Series(np.sum(roster[['AdjPt', 'AdjFGA', 'AdjFTA', 'Adj3P']].values * raw_bpm[['AdjPt', 'FGA', 'FTA', '3P']].values
                                            , axis=1), 
                                    index=range(1,len(raw_bpm)+1)).fillna(0)
    raw_bpm['Ballhandling'] = pd.Series(np.sum(roster[['AdjAST', 'AdjTOV']].values * raw_bpm[['AST', 'TO']].values
                                            , axis=1), 
                                    index=range(1,len(raw_bpm)+1)).fillna(0)
    raw_bpm['Rebounding'] = pd.Series(np.sum(roster[['AdjORB', 'AdjDRB', 'AdjTRB']].values * raw_bpm[['ORB', 'DRB', 'TRB']].values
                                            , axis=1), 
                                    index=range(1,len(raw_bpm)+1)).fillna(0)
    raw_bpm['Defense'] = pd.Series(np.sum(roster[['AdjSTL', 'AdjBLK', 'AdjPF']].values * raw_bpm[['STL', 'BLK', 'PF']].values
                                            , axis=1), 
                                    index=range(1,len(raw_bpm)+1)).fillna(0)
    raw_bpm['Pos Const'] = (raw_bpm['OffRole']-3)*pos_constants['Slope'] + np.where(raw_bpm['EstPos'] < 3,
                                    (raw_bpm['EstPos']-1)/2*pos_constants['Pos 3']+(3-raw_bpm['EstPos'])/2*pos_constants['Pos 1'],
                                    (raw_bpm['EstPos']-1)/2*pos_constants['Pos 5']+(5-raw_bpm['EstPos'])/2*pos_constants['Pos 3'])

    raw_bpm['Raw BPM'] = pd.Series(np.sum(raw_bpm[['Scoring', 'Ballhandling', 'Rebounding', 'Defense', 'Pos Const']], axis=1))

    # Raw OBPM calculation
    raw_obpm = roster[['Name', 'EstPos', 'OffRole']]

    for stat in bpm_coefficients['Pos 1'].keys():
        if stat in ['FGA', 'FTA']:
            pos_df = raw_obpm['OffRole']
        else:
            pos_df = raw_obpm['EstPos']
        raw_obpm[stat] = ((5-pos_df)*obpm_coeffiecients['Pos 1'][stat] + (pos_df-1)*obpm_coeffiecients['Pos 5'][stat])/4
        raw_obpm[stat] = raw_obpm[stat].round(3)


    raw_obpm['Scoring'] = pd.Series(np.sum(roster[['AdjPt', 'AdjFGA', 'AdjFTA', 'Adj3P']].values * raw_obpm[['AdjPt', 'FGA', 'FTA', '3P']].values
                                            , axis=1), 
                                    index=range(1,len(raw_obpm)+1)).fillna(0)
    raw_obpm['Ballhandling'] = pd.Series(np.sum(roster[['AdjAST', 'AdjTOV']].values * raw_obpm[['AST', 'TO']].values
                                            , axis=1), 
                                    index=range(1,len(raw_obpm)+1)).fillna(0)
    raw_obpm['Rebounding'] = pd.Series(np.sum(roster[['AdjORB', 'AdjDRB', 'AdjTRB']].values * raw_obpm[['ORB', 'DRB', 'TRB']].values
                                            , axis=1), 
                                    index=range(1,len(raw_obpm)+1)).fillna(0)
    raw_obpm['Defense'] = pd.Series(np.sum(roster[['AdjSTL', 'AdjBLK', 'AdjPF']].values * raw_obpm[['STL', 'BLK', 'PF']].values
                                            , axis=1), 
                                    index=range(1,len(raw_bpm)+1)).fillna(0)
    raw_obpm['Pos Const'] = (raw_obpm['OffRole']-3)*off_pos_constants['Slope'] + np.where(raw_obpm['EstPos'] < 3,
                                    (raw_obpm['EstPos']-1)/2*off_pos_constants['Pos 3']+(3-raw_obpm['EstPos'])/2*off_pos_constants['Pos 1'],
                                    (raw_obpm['EstPos']-1)/2*off_pos_constants['Pos 5']+(5-raw_obpm['EstPos'])/2*off_pos_constants['Pos 3'])

    raw_obpm['Raw OBPM'] = pd.Series(np.sum(raw_obpm[['Scoring', 'Ballhandling', 'Rebounding', 'Defense', 'Pos Const']], axis=1))


    avg_lead = team_stats['NRtg/A']*team_stats['Pace']/100/2
    lead_bonus = 0.35/2*avg_lead
    adj_team_lead = team_stats['NRtg/A']+lead_bonus
    adj_ortg = team_stats['ORtg/A'] + lead_bonus / 2

    # adjust for player contribution
    raw_team_adj = (adj_team_lead - np.sum(raw_bpm['Raw BPM'] * roster['%Min'])) / 5 
    off_team_adj = (adj_ortg - np.sum(raw_obpm['Raw OBPM'] * roster['%Min'])) / 5


    final_bpm = roster[['Name', 'EstPos', 'OffRole', 'MP']]
    final_bpm['MPG'] = (roster['MP']/roster['G']).round(1)
    final_bpm['BPM'] = (raw_bpm['Raw BPM'] + raw_team_adj).round(1)
    final_bpm['OBPM'] = (raw_obpm['Raw OBPM'] + off_team_adj).round(1)
    final_bpm['DBPM'] = final_bpm['BPM']-final_bpm['OBPM']
    final_bpm['Contribution'] = (final_bpm['BPM']*roster['%Min']).round(1)
    final_bpm['VORP'] = ((final_bpm['BPM']-REPLACEMENT_PLAYER)*roster['%Min'] * team_stats['G']/40).round(2)

    final_bpm['OffRole'] = final_bpm['OffRole'].round(1)
    final_bpm.rename(columns={"OffRole": "Off. Role", "EstPos": "Pos", "MP": "Minutes"}, inplace=True)

    return final_bpm

