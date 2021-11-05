#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  1 15:17:25 2021
@brief scripts to work with exports from GRU website for registration Data (player info)
@author: alec
"""

import pandas as pd
import re

class Players(pd.DataFrame):
    '''@brief class to handle gru player data downloaded from gru site'''
    
    SUB_LIST_FIELDS = ['first_name','last_name','gender',
                       'email_address','primary_phone_number',
                       'HighestLevel5', 'Throws', 'Ath','Pos']
    
    @property
    def _constructor(self):
        return Players
    @property
    def _constructor_sliced(self):
        return pd.Series
    
    def __init__(self,*args,**kwargs):
        '''@brief constructor'''
        super().__init__(*args,**kwargs)
        if 'first_name' in self.columns and 'middle_name' not in self.columns:
            self._clean_names() # split names with a space in them if not done yet
        #self.set_index_as_names(inplace=True) # use names as index
        
    def _clean_names(self,set_middle=False):
        '''@brief split complex first names to first/middle names'''
        fnames = self['first_name']
        fn,mn = self.split_complex_names(fnames)
        self['first_name'] = fn
        mn_loc = list(self.columns).index('first_name')+1
        self.insert(mn_loc,'middle_name',mn_loc)
    
    def set_index_as_names(self,**kwargs):
        '''@brief set the index as the player first_name last_name'''
        name_idx = pd.Index(self['first_name']+' '+self['last_name'],name='name')
        return self.set_index(name_idx,**kwargs)
    
    def get_vector(self,**kwargs):
        '''@brief get the vector from the data provided. return a Series'''
        vector_keys = ['HighestLevel5','Throws','Ath']
        pass
    
    def get_accepted(self):
        '''@brief get players accepted to the league'''
        return self[self['status']=='accepted']
    
    def get_sub_list(self):
        '''@brief get a list of possible subs (i.e. pull the watilist with contact info)'''
        contact_keys = ['email_address','primary_phone_number']
        info_keys = ['gender']
        waitlisted = players[players['status']=='waitlisted']
        return waitlisted
        
    @classmethod 
    def from_csv(cls,path,**kwargs):
        return cls(pd.read_csv(path,**kwargs))
    
    @staticmethod
    def split_complex_names(names):
        '''@brief split any complex (e.g. have a space in them) first names into first/middle'''
        split_names = [v.strip().split(' ',1) for v in names]
        # set first names
        fn = [sn[0] for sn in split_names]
        # now set 'middle' name
        mn = [sn[1] if len(sn)>1 else '' for sn in split_names]
        return fn,mn
    
    def write_csv(self,path,fields=None,**kwargs):
        '''
        @brief wrapper to write out data for given fields to a csv
        @param[in] fields - list of fields to print (e.g. self.SUB_LIST_FIELDS)
        '''
        default_kwargs = {'index':False}
        for k,v in default_kwargs.items():
            if not k in kwargs.keys(): # set defaults if not provided
                kwargs[k]=v
        # set the data to work on
        out_data = self;
        if fields is not None: # select fields if desired
            out_data = self[fields]
        # now write
        out_data.to_csv(path,**kwargs)
        
    def find_by_name(self,first_name=None,last_name=None):
        '''@brief find closest player names based on input names'''
        #first look for first name
        fnmatch = None; lnmatch = None;
        if first_name is not None:
            fnmatch = self[self['first_name'].apply(str.lower)==first_name.lower()]
        if last_name is not None:
            lnmatch = self[self['last_name'].apply(str.lower)==last_name.lower()]
        return pd.concat([fnmatch,lnmatch])
    
    def add_column_by_name(self,names,vals,col_name):
        '''@brief given a list of names and values, add a column with col_name'''
        pass
        
    
    
if __name__=='__main__':
    
    path = '/data/downloads/2021-Fall-Broomfield-League_2021-11-04-17_47.csv'
    players = Players.from_csv(path)
    possible_subs = players.get_sub_list()
    #possible_subs.write_csv('~/tmp/broomfield-league-2021_subs.csv',fields=possible_subs.SUB_LIST_FIELDS,index=False)
    possible_sub_emails = possible_subs['email_address']
    print(players)
    # names of subs who responded yes
    sub_names = """
    Ian Lipton, Nate Hopp, Raj Joshi, Jake Beckner, Brandon Protas, Graham Buhse
    Scott Nordstrom, Alex Villacorta, Matt Ferreri
    Mike Shettel, Finn Lundy, Alex Python, Venkatesh Santharam, Matt Whitlock
    Stanley Ly, Drew Eisenberg, Dalton Chaffee, reed antonich, Sarang Mittal,
    Lucas Corsiglia, James Shanahan
    """
    
    # split and clean the names
    sub_names_split = re.split(',\n|,|\n',sub_names)
    sub_names_split = [s.strip() for s in sub_names_split if s.strip()]
    sub_first_names = [sn.split(' ')[0] for sn in sub_names_split]
    sub_last_names  = [sn.split(' ')[-1] for sn in sub_names_split]
    
    #for those with more complicated names
    #manual_first_names = ['Lucas Giaco','James "Marty"']
    #manual_last_names  = ['Corsiglia','Shanahan']
    #sub_first_names += manual_first_names
    #sub_last_names += manual_last_names
    
    # get locations of names
    name_locs = []
    for sfn,sln in zip(sub_first_names,sub_last_names):
        idx = possible_subs[(possible_subs['first_name']==sfn)&
                            (possible_subs['last_name']==sln)].index[0]
        name_locs.append(idx)
    sub_list = possible_subs.loc[name_locs]
    
    sub_list.write_csv('~/tmp/broomfield-league-2021_subs.csv',fields=possible_subs.SUB_LIST_FIELDS,index=False)
    
    
    
    
    