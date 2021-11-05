#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@date Thu Nov  4 17:48:53 2021
@brief Create pre-tournament info for captains to fill with subs so nobody
    cant argue on the day of... 
@author: alec
"""
from GruTools.Players import Players
import pandas as pd
import numpy as np

path = '/data/downloads/2021-Fall-Broomfield-League_2021-11-04-17_47.csv'
players = Players.from_csv(path).get_accepted()
# now sort by team

# now load in vector data
vector_data = Players.from_csv(r'/data/downloads/2021-Fall-Broomfield-League-Vector-Adjustments - 2021-Fall-Broomfield-League (1).csv')
fn,ln,vecs = vector_data['first_name'],vector_data['last_name'],vector_data['final_vector']
players.insert(len(players.columns),'vector',np.zeros(len(players['first_name']),dtype=int))
for f,l,v in zip(fn,ln,vecs):
    players.loc[np.logical_and(players['first_name']==f,players['last_name']==l),'vector'] = v
# and add
out_keys = ['first_name','last_name','team_name','vector']

team_players = players.sort_values('team_name')

team_data = team_players.loc[:,out_keys]
team_data.to_excel('./tmp/team_data.xlsx',index=False)