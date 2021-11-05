#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  1 15:17:25 2021
@brief scripts to work with exports from GRU website for registration Data (player info)
@author: alec
"""

import pandas as pd
import numpy as np
import datetime

col_names = ['id', 'start_date', 'start_time', 'end_date', 'end_time', 'home_team',
       'away_team', 'home_score', 'away_score', 'reported_at', 'division',
       'stage', 'field', 'field_number']

class Schedule(pd.DataFrame):
    
    @property
    def _constructor(self):
        return Schedule
    @property
    def _constructor_sliced(self):
        return pd.Series
    
    def get_dates(self):
        return np.unique(self['start_date'])
    def get_times(self):
        return np.unique(self['start_time'])
    
    def verify(self,verbose=True):
        '''
        @brief verify our schedule. This currently verifies the following
            - No field is scheduled twice for the same time/date
            - All teams are scheduled for each date/time
            - All teams play each team almost (within 1 game) the same number of times during the season
            - No teams play the same team twice on a single date
        '''
        if verbose: print("--- VERIFICATION ---")
        exceptions = []
        ver_funs = [self._verify_field_use,
                    self._verify_team_games,
                    self._verify_versus_count,
                    self._verify_max_versus]
        for ver in ver_funs:
            try:
                ver(verbose=verbose)
            except Exception as e:
                exceptions.append(e)
                print('-- {}'.format(e))
        # now check exceptions
        if len(exceptions):
            raise Exception('Error in verification')
                    
    def _verify_field_use(self,verbose=True):
        '''@brief make sure each field is used only once per date/time'''
        dates = self.get_dates()
        times = self.get_times()
        if verbose:print("{:15s}".format("FIELD USE: "),end='')
        for d in dates:
            date_vals = self[self['start_date']==d]
            for t in times:
                games = date_vals[date_vals['start_time']==t]
                # make sure we dont reuse fields
                if not len(np.unique(games['field_number']))==len(games):
                    if verbose: print("FAIL")
                    raise Exception("Error with field numbers on {} at {}".format(d,t))
        if verbose: print("SUCCESS")
        
    def _verify_team_games(self,verbose=True):
        '''@brief ensure all teams are playing at each date/time'''
        dates = np.unique(self['start_date'])
        times = np.unique(self['start_time'])
        if verbose:print("{:15s}".format("TEAM GAMES: "),end='')
        for d in dates:
            date_vals = self[self['start_date']==d]
            for t in times:
                games = date_vals[date_vals['start_time']==t]
                # make sure we dont reuse fields
                if not len(np.unique(list(games['away_team'])+list(games['home_team'])))==nteams:
                    if verbose: print("FAIL")
                    raise Exception("Error with teams playing on {} at {}".format(d,t))
        if verbose: print("SUCCESS")
        
    def _verify_versus_count(self,verbose=True):
        '''@brief verify we play all teams within 1 game of others over the whole season'''
        if verbose:print("{:15s}".format("VERSUS COUNT: "),end='')
        versus_count = self.get_versus_count()
        mean_plays = {k:np.mean(list(v.values())) for k,v in versus_count.items()}
        for t in mean_plays.keys():
            play_diff = np.abs(mean_plays[t]-np.asarray(list(versus_count[t].values())))
            if np.any(play_diff>1):
                if verbose: print("FAIL");print(versus_count[t])
                raise Exception("Error in How many times each team plays one another.")
        if verbose: print("SUCCESS")
        
    def _verify_max_versus(self,max_plays=1,verbose=True):
        '''@brief verify we dont play a team more than once per day'''
        if verbose:print("{:15s}".format("MAX VERSUS: "),end='')
        dates = self.get_dates()
        for d in dates:
            dsched = self[self['start_date']==d]
            vcount = dsched.get_versus_count()
            for k,v in vcount.items():
                vc = np.asarray(list(v.values())) # get the count
                if any(vc>max_plays):
                    if verbose: print("FAIL");
                    raise Exception(f"Error: {k} repeats a matchup on {d}")
        if verbose: print("SUCCESS")
        
    def get_versus_count(self):
        '''@brief get count of how many times each team plays others'''
        teams = np.unique(sched['home_team'])
        play_count = {t:{} for t in teams}
        for t in teams:
            team_games = self[np.logical_or(self['home_team']==t,self['away_team']==t)]
            for ot in teams:
                if ot==t:continue
                play_count[t][ot] = np.shape(team_games[np.logical_or(team_games['home_team']==ot,team_games['away_team']==ot)])[0]
        return play_count
            
        
    @classmethod 
    def from_csv(cls,path,**kwargs):
        return cls(pd.read_csv(path,**kwargs))
        
    
    
if __name__=='__main__':
    
    fpath = '/data/downloads/2021-fall-broomfield-league_games_2021-09-07_10_11.csv'
    fpath = '/data/downloads/2021-fall-broomfield-league_games_2021-10-07_13_54.csv'
    fpath = '/data/downloads/2021-fall-broomfield-league_games_2021-10-13_10_31.csv'

    nteams = 6
    #team_name = ['Team 0{}'.format(i+1) for i in range(nteams)]
    #game_start = [datetime.datetime(1,1,1,10,00,0),datetime.datetime(1,1,1,11,30,0)]
    #game_end = [datetime.datetime(1,1,1,11,20,0),datetime.datetime(1,1,1,13,00,0)]
    #date_start = datetime.datetime(2021,9,12)
    #field_name = 'Broomfield Commons Red Pod'
    #field_number = [1,2,3,4]
    
    sched = Schedule.from_csv(fpath)
    sched[:-3].verify()
    print(sched.get_versus_count())