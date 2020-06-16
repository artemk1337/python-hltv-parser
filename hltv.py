import requests
import urllib
import datetime
from bs4 import BeautifulSoup
from re import sub
import re
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from datetime import datetime
import time
from requests.auth import HTTPProxyAuth
import random


PREFIX = 'https://www.hltv.org'
proxyDict = None
proxyAuth = None


def get_parsed_page(url, proxy_=None, auth_=None):
    TIMESLEEP = random.uniform(0.25, 0.3)
    time.sleep(TIMESLEEP)
    got_req = requests.get(url, proxies=proxy_, auth=auth_).text
    return BeautifulSoup(got_req)


# download all urls matches
def get_results_url(filename=None, pages_with_results=[0]):
    all_matches = []
    for i in pages_with_results:
        if i == 0:
            results = get_parsed_page('http://www.hltv.org/results', proxyDict, proxyAuth)
        else:
            results = get_parsed_page(f'http://www.hltv.org/results?offset={i}00', proxyDict, proxyAuth)
        # list of matches
        all_matches += [url_.find('a', {"class": "a-reset"})['href'] for url_ in
                        results.find('div',
                                     {"class": "results-all", 'data-zonedgrouping-group-classes': "results-sublist"}).
                        find_all('div', {"class": "result-con"})]
    all_matches = np.array(all_matches)
    data = pd.DataFrame(all_matches, columns=['match_url'])
    data.index.name = 'id'
    if filename is None:
        return data
    else:
        data.to_csv(f'{filename}.csv')
        return data


    class MatchPageParams:
    def __init__(self, df, start_index=None, finish_index=None):
        self.df = df
        self.MATCH_PAGE = None
        self.MATCH_ID = None
        self.match = None
        self.start_index = start_index
        self.finish_index = finish_index

    def add_all_params(self):
        time_start = time.time()
        for match in self.df['match_url'][self.start_index:self.finish_index]:
            self.MATCH_ID = list(self.df['match_url']).index(match)
            print(PREFIX + match)
            print('match id -', self.MATCH_ID, '; time spent -', time.time() - time_start)
            self.match = match
            self.add_url_teams()
            self.add_url_event()
            self.add_10_urls_players()
            self.add_total_maps()
            self.add_maps()
            self.add_date()
            self.add_scores()
            self.add_history()
            self.add_ranks()
            self.add_5last_urls_opponents()
            self.add_5last_scores_and_types()
            self.MATCH_PAGE = None
    
    def parse_page(self):
        if self.MATCH_PAGE is None:
            self.MATCH_PAGE = get_parsed_page(PREFIX + self.match, proxyDict, proxyAuth)

    def _get_score_(self):
        self.parse_page()
        score = self.MATCH_PAGE.find('div', {'class': 'match-page'}).\
                find('div', {'class': 'teamsBox'}).\
                find_all('div', {'class': 'team'})
        for i in range(len(score)):
            score[i] = score[i].find('div', {'class': f'team{i + 1}-gradient'}).\
                                find_all('div')[-1].text
            self.df[f'score{i + 1}'][self.MATCH_ID] = score[i]

    def add_scores(self):
        # add columns
        if 'score1' not in self.df.columns:
            self.df['score1'] = ""
        if 'score2' not in self.df.columns:
            self.df['score2'] = ""
        if self.df['score1'][self.MATCH_ID] == "" or self.df['score2'][self.MATCH_ID] == "":
            self._get_score_()

    def _get_total_maps_(self):
        self.parse_page()
        try:
            table = self.MATCH_PAGE.find('div', {'class': 'flexbox-column'}).\
                    find_all('div', {'class': 'mapholder'})
            self.df['total_maps'][self.MATCH_ID] = len(table)
            self.df['maps_played'][self.MATCH_ID] = 0
            for i in table:
                played = i.find('div', {'class': 'results'}).find('div', {'class': 'results-center'})
                if played.text:
                    self.df['maps_played'][self.MATCH_ID] += 1
        except:
            self.df['total_maps'][self.MATCH_ID] = 0
            self.df['maps_played'][self.MATCH_ID] = 0
            

    def add_total_maps(self):
        # add columns
        if 'total_maps' not in self.df:
            self.df['total_maps'] = ""
        if 'maps_played' not in self.df:
            self.df['maps_played'] = ""
        if self.df['total_maps'][self.MATCH_ID] == "" or self.df['maps_played'][self.MATCH_ID] == "":
            self._get_total_maps_()

    def _get_ranks_(self):
        self.parse_page()
        ranks = self.MATCH_PAGE.find('div', {'class': 'lineups'}).\
                find_all('div', {'class': 'box-headline'})
        for i in range(len(ranks)):
            ranks[i] = ranks[i].find('div', {'class': 'teamRanking'}).text
            self.df[f'rank{i + 1}'][self.MATCH_ID] = ranks[i]
            
    def add_ranks(self):
        # add columns
        if 'rank1' not in self.df:
            self.df['rank1'] = ""
        if 'rank2' not in self.df:
            self.df['rank2'] = ""
        if self.df['rank1'][self.MATCH_ID] == "" or self.df['rank2'][self.MATCH_ID] == "":
            self._get_ranks_()
    
    def _get_date_(self):
        self.parse_page()
        self.df['date'][self.MATCH_ID] = datetime.utcfromtimestamp(int(
                self.MATCH_PAGE.find('div', {'class': 'timeAndEvent'}).
                find('div', {'class': 'time'})['data-unix'][:-3])).strftime('%Y-%m-%d')
    
    def add_date(self):
        if 'date' not in self.df:
            self.df['date'] = ""
        if self.df['date'][self.MATCH_ID] == "":
            self._get_date_()

    def _get_history_(self):
        self.parse_page()
        h2h = self.MATCH_PAGE.find('div', {'class': 'head-to-head'}).\
                find_all('div', {'class': 'flexbox-column'})
        self.df['h2h_wins1'][self.MATCH_ID] = h2h[0].find('div', {'class': 'bold'}).text
        self.df['h2h_wins2'][self.MATCH_ID] = h2h[-1].find('div', {'class': 'bold'}).text

    def add_history(self):
        if 'h2h_wins1' not in self.df:
            self.df['h2h_wins1'] = ""
        if 'h2h_wins2' not in self.df:
            self.df['h2h_wins2'] = ""
        if self.df['h2h_wins1'][self.MATCH_ID] == "" or self.df['h2h_wins2'][self.MATCH_ID] == "":
            self._get_history_()

    def _get_5last_score_type_(self, team_id, match_id):
        self.parse_page()
        try:
            tmp = self.MATCH_PAGE.find('div', {'class': 'past-matches'}).\
                    find_all('div', {'class': 'half-width'})[team_id].find('table', {'class': 'matches'}).\
                    find_all('tr', {'class': 'table'})[match_id]
            total = tmp.find('a', {'data-link-tracking-page': 'Matchpage'}).text
            self.df[f'5last_match{match_id + 1}_total_maps{team_id + 1}'][self.MATCH_ID] = total
            score = tmp.find('td', {'class': 'result'}).text.split(' - ')
            if int(score[0]) > int(score[1]):
                score = [1, 0]
            else:
                score = [0, 1]
            self.df[f'5last_match{match_id + 1}_score{team_id + 1}'][self.MATCH_ID] = score[0]
            self.df[f'5last_match{match_id + 1}_opponent_score{team_id + 1}'][self.MATCH_ID] = score[1]
        except:
            self.df[f'5last_match{match_id + 1}_total_maps{team_id + 1}'][self.MATCH_ID] = 0
            self.df[f'5last_match{match_id + 1}_score{team_id + 1}'][self.MATCH_ID] = 0
            self.df[f'5last_match{match_id + 1}_opponent_score{team_id + 1}'][self.MATCH_ID] = 0
        
    
    def add_5last_scores_and_types(self):
        for team_id in range(2):
            for match_id in range(5):
                if f'5last_match{match_id + 1}_total_maps{team_id + 1}' not in self.df:
                    self.df[f'5last_match{match_id + 1}_total_maps{team_id + 1}'] = ""
                if f'5last_match{match_id + 1}_score{team_id + 1}' not in self.df:
                    self.df[f'5last_match{match_id + 1}_score{team_id + 1}'] = ""
                if f'5last_match{match_id + 1}_opponent_score{team_id + 1}' not in self.df:
                    self.df[f'5last_match{match_id + 1}_opponent_score{team_id + 1}'] = ""
                if self.df[f'5last_match{match_id + 1}_total_maps{team_id + 1}'][self.MATCH_ID] == "" or\
                    self.df[f'5last_match{match_id + 1}_score{team_id + 1}'][self.MATCH_ID] == "" or\
                    self.df[f'5last_match{match_id + 1}_opponent_score{team_id + 1}'][self.MATCH_ID] == "":
                    self._get_5last_score_type_(team_id, match_id)

    def _get_5last_opponents_(self, team_id):
        self.parse_page()
        arr = []
        tmp = self.MATCH_PAGE.find('div', {'class': 'past-matches'}).\
                find_all('div', {'class': 'half-width'})[team_id].find('table', {'class': 'matches'}).\
                find_all('tr', {'class': 'table'})
        for i in tmp:
            arr += [i.find('td', {'class': 'opponent'}).find('a')['href']]
        self.df[f'opponents_url_history_team{team_id + 1}'][self.MATCH_ID] = arr
        
    
    def add_5last_urls_opponents(self):
        for team_id in range(2):
            if f'opponents_url_history_team{team_id + 1}' not in self.df:
                self.df[f'opponents_url_history_team{team_id + 1}'] = ""
            if self.df[f'opponents_url_history_team{team_id + 1}'][self.MATCH_ID] == "":
                self._get_5last_opponents_(team_id)

    def _get_players_url__(self, team_id):
        self.parse_page()
        arr = []
        tmp = self.MATCH_PAGE.find('div', {'class': 'lineups'}).\
                find_all('div', {'class': 'lineup'})[team_id].find('div', {'class': 'players'}).\
                find_all('td', {'class': 'player'})
        for i in tmp:
            try:
                arr += [i.find('a')['href']]
            except:
                arr += [""]
        self.df[f'players_url_{team_id + 1}'][self.MATCH_ID] = arr[:5]
        #print(arr)

    def add_10_urls_players(self):
        for team_id in range(2):
            if f'players_url_{team_id + 1}' not in self.df:
                self.df[f'players_url_{team_id + 1}'] = ""
            if self.df[f'players_url_{team_id + 1}'][self.MATCH_ID] == "":
                self._get_players_url__(team_id)

    def _get_event_url_(self):
        self.parse_page()
        self.df['event_url'][self.MATCH_ID] = self.MATCH_PAGE.find('div', {'class': 'timeAndEvent'}).\
                find('div', {'class': 'event'}).find('a')['href']
    
    def add_url_event(self):
        if 'event_url' not in self.df:
            self.df['event_url'] = ""
        if self.df['event_url'][self.MATCH_ID] == "":
            self._get_event_url_()
    
    def _get_maps_(self):
        self.parse_page()
        arr = []
        map_name = []
        score_maps1 = []
        score_maps2 = []
        picks = []
        try:
            tmp = self.MATCH_PAGE.find('div', {'class': 'flexbox-column'}).\
                    find_all('div', {'class': 'mapholder'})
            for i in tmp:
                played = i.find('div', {'class': 'results'}).find('div', {'class': 'results-center'})
                if played.text:
                    arr += [played.find('a')['href']]
                    map_name += [i.find('div', {'class': 'map-name-holder'}).find('div', {'class': 'mapname'}).text]
                    table = i.find('div', {'class': 'results-left'})
                    if self.df['total_maps'][self.MATCH_ID] > 1:
                        if table['class'][-1] == 'pick':
                            picks += [1]
                    score_maps1 += [table.find('div', {'class': 'results-team-score'}).text]
                    table = i.find('span', {'class': 'results-right'})
                    if self.df['total_maps'][self.MATCH_ID] > 1:
                        if table['class'][-1] == 'pick':
                            picks += [-1]
                    score_maps2 += [table.find('div', {'class': 'results-team-score'}).text]
            self.df['maps_url'][self.MATCH_ID] = arr
            self.df['maps_name'][self.MATCH_ID] = map_name
            self.df['score1_maps'][self.MATCH_ID] = score_maps1
            self.df['score2_maps'][self.MATCH_ID] = score_maps2
            if not picks:
                self.df['picks'][self.MATCH_ID] = "None"
            else:
                self.df['picks'][self.MATCH_ID] = picks
        except Exception as e:
            print(e)
            self.df['maps_url'][self.MATCH_ID] = "None"
            self.df['maps_name'][self.MATCH_ID] = "None"
            self.df['score1_maps'][self.MATCH_ID] = "None"
            self.df['score2_maps'][self.MATCH_ID] = "None"
            self.df['picks'][self.MATCH_ID] = "None"
    
    def add_maps(self):
        if 'maps_url' not in self.df:
            self.df['maps_url'] = ""
        if 'maps_name' not in self.df:
            self.df['maps_name'] = ""
        if 'score1_maps' not in self.df:
            self.df['score1_maps'] = ""
        if 'score2_maps' not in self.df:
            self.df['score2_maps'] = ""
        if 'picks' not in self.df:
            self.df['picks'] = ""
        if self.df['maps_url'][self.MATCH_ID] == "" or self.df['maps_name'][self.MATCH_ID] == "" or\
                self.df['score1_maps'][self.MATCH_ID] == "" or self.df['score2_maps'][self.MATCH_ID] == "" or\
                self.df['picks'][self.MATCH_ID] == "":
            self._get_maps_()
    
    def _get_url_teams_(self):
        self.parse_page()
        tmp = self.MATCH_PAGE.find('div', {'class': 'teamsBox'}).\
                find_all('div', {'class': 'team'})
        self.df['url_team1'][self.MATCH_ID] = tmp[0].find('a')['href']
        self.df['url_team2'][self.MATCH_ID] = tmp[1].find('a')['href']
    
    def add_url_teams(self):
        if 'url_team1' not in self.df:
            self.df['url_team1'] = ""
        if 'url_team2' not in self.df:
            self.df['url_team2'] = ""
        if self.df['url_team1'][self.MATCH_ID] == "" or self.df['url_team2'][self.MATCH_ID] == "":
            self._get_url_teams_()


TEAM_STAT = 'http://www.hltv.org/stats/teams/matches'


class LastMaps:
    def __init__(self, df, last_maps=20, months=3, start_index=0, finish_index=None):
        self.df = df
        self.TEAM_PAGE = None
        self.MATCH_ID = None
        self.start_index = start_index
        self.finish_index = finish_index
        self.start_date = None
        self.finish_date = None
        self.last_maps = last_maps
        self.months = months

    def add_all_params(self):
        time_start = time.time()
        for date, t1, t2, index in zip(df['date'][self.start_index:self.finish_index],
                                       df['url_team1'][self.start_index:self.finish_index],
                                       df['url_team2'][self.start_index:self.finish_index],
                                       range(len(df['date'][self.start_index:self.finish_index]))):
            self.MATCH_ID = index + self.start_index
            print('match id -', self.MATCH_ID, '; time spent -', time.time() - time_start)
            self.start_date = (datetime.strptime(date, '%Y-%m-%d') - relativedelta(months=self.months)).strftime("%Y-%m-%d")
            self.finish_date = (datetime.strptime(date, '%Y-%m-%d') - relativedelta(days=1)).strftime("%Y-%m-%d")
            self.TEAM_PAGE = get_parsed_page(TEAM_STAT +
                                             t1.split('/team')[-1] +
                                             f'?startDate={self.start_date}&endDate={self.finish_date}',
                                             proxyDict, proxyAuth)
            self.add_last_scores_and_ranks('_team1')
            self.TEAM_PAGE = get_parsed_page(TEAM_STAT +
                                             t2.split('/team')[-1] +
                                             f'?startDate={self.start_date}&endDate={self.finish_date}',
                                             proxyDict, proxyAuth)
            self.add_last_scores_and_ranks('_team2')
            


    def _get_last_score_(self, team_id, match_id):
        try:
            tmp = self.TEAM_PAGE.find('table', {'class': 'stats-table'}).\
                    find('tbody').find_all('tr')[match_id].find('span', {'class': 'statsDetail'}).text.split(' - ')
            self.df[f'last_maps{match_id + 1}_score{team_id}'][self.MATCH_ID] = tmp[0]
            self.df[f'last_maps{match_id + 1}_opponent_score{team_id}'][self.MATCH_ID] = tmp[1]
        except:
            self.df[f'last_maps{match_id + 1}_score{team_id}'][self.MATCH_ID] = 0
            self.df[f'last_maps{match_id + 1}_opponent_score{team_id}'][self.MATCH_ID] = 0

    def add_last_scores_and_ranks(self, team_id):
        for match_id in range(self.last_maps):
            if f'last_maps{match_id + 1}_score{team_id}' not in self.df:
                self.df[f'last_maps{match_id + 1}_score{team_id}'] = ""
            if f'last_maps{match_id + 1}_opponent_score{team_id}' not in self.df:
                self.df[f'last_maps{match_id + 1}_opponent_score{team_id}'] = ""
            if self.df[f'last_maps{match_id + 1}_score{team_id}'][self.MATCH_ID] == "" or\
                self.df[f'last_maps{match_id + 1}_opponent_score{team_id}'][self.MATCH_ID] == "":
                self._get_last_score_(team_id, match_id)


class Tour:
    def __init__(self, df, start_index=0, finish_index=None):
        self.df = df
        self.EVENT_PAGE = None
        self.MATCH_ID = None
        self.start_index = start_index
        self.finish_index = finish_index
        self.event = None
    
    def add_all_params(self):
        time_start = time.time()
        for event, index in zip(self.df['event_url'][self.start_index:self.finish_index],
                         range(len(df['event_url'][self.start_index:self.finish_index]))):
            self.MATCH_ID = index + self.start_index
            print(PREFIX + event)
            print('match id -', self.MATCH_ID, '; time spent -', time.time() - time_start)
            self.event = event
            self.add_event()
        self.processing_prizepool(self.df)
        self.processing_eventteams(self.df)
        self.processing_eventtype(self.df)

    def processing_prizepool(self, df):
        for i in range(len(df['prize_pool'])):
            if str(df['prize_pool'][i]).split(' ')[0][0] == '$':
                df['prize_pool'][i] = re.sub(r'[^\d.]', '', df['prize_pool'][i].split(' ')[0])
            else:
                df['prize_pool'][i] = 0

    def processing_eventteams(self, df):
        for i in range(len(df)):
            if df['event_teams'][i] != '':
                df['event_teams'][i] = re.sub(r'[^\d]', '', df['event_teams'][i])
            else:
                df['event_teams'][i] = 0

    def processing_eventtype(self, df):
        for i in range(len(df)):
            if re.findall(r'(Online)', df['event_type'][i]):
                df['event_type'][i] = 'Online'
            else:
                df['event_type'][i] = 'Lan'

    def _get_event_(self):
        self.EVENT_PAGE = get_parsed_page(PREFIX + self.event, proxyDict, proxyAuth)
        tmp = self.EVENT_PAGE.find('table', {'class': 'info'}).find('tbody')
        self.df['prize_pool'][self.MATCH_ID] = tmp.find('td', {'class': 'prizepool'}).text
        self.df['event_teams'][self.MATCH_ID] = tmp.find('td', {'class': 'teamsNumber'}).text
        self.df['event_type'][self.MATCH_ID] = tmp.find('td', {'class': 'location'}).\
                find('span', {'class': 'text-ellipsis'}).text
        
    
    def add_event(self):
        if 'prize_pool' not in self.df:
            self.df['prize_pool'] = ""
        if 'event_teams' not in self.df:
            self.df['event_teams'] = ""
        if 'event_type' not in self.df:
            self.df['event_type'] = ""
        if self.df['event_type'][self.MATCH_ID] == "" or\
            self.df['event_teams'][self.MATCH_ID] == "" or\
            self.df['prize_pool'][self.MATCH_ID] == "":
            self._get_event_()

            
PL_STAT = 'https://www.hltv.org'


class PlStatInTeam:
    def __init__(self, df, start_index=0, finish_index=None):
        self.df = df
        self.PL_PAGE = None
        self.MATCH_ID = None
        self.start_index = start_index
        self.finish_index = finish_index
        self.period = None

    def add_all_params(self):
        time_start = time.time()
        for date, index in zip(df['date'][self.start_index:self.finish_index],
                               range(len(df.iloc[self.start_index:self.finish_index]))):
            self.MATCH_ID = index + self.start_index
            print('match id -', self.MATCH_ID, '; time spent -', time.time() - time_start)
            self.period = (datetime.now() - datetime.strptime(date, '%Y-%m-%d')).days
            self.add_5_players(1)
            self.add_5_players(2)
    
    def _get_player_stat_(self, team_id, player):
        print(team_id, player)
        try:
            player_url = (df[f'players_url_{team_id}'][self.MATCH_ID])[player]
        except:
            player_url = (eval(df[f'players_url_{team_id}'][self.MATCH_ID])[player])
        if player_url:
            self.PL_PAGE = get_parsed_page(PL_STAT + player_url + '#tab-teamsBox')  #, proxyDict, proxyAuth)
            tmp = [i.find('div', {'class': 'stat'}).text for i in
                   self.PL_PAGE.find('div', {'class': 'tab-content', 'id': 'teamsBox'}).\
                   find_all('div', {'class': 'highlighted-stat'})]
            tmp = [0 if i == '-' else int(i) for i in tmp]
            self.df[f'player{player + 1}_teams_all_team{team_id}'][self.MATCH_ID] = tmp[0]
            self.df[f'player{player + 1}_days_in_current_team{team_id}'][self.MATCH_ID] = max(tmp[1] - self.period, 0)
            self.df[f'player{player + 1}_days_in_all_team{team_id}'][self.MATCH_ID] = max(tmp[2] - self.period, 0)
        else:
            self.df[f'player{player + 1}_teams_all_team{team_id}'][self.MATCH_ID] = 0
            self.df[f'player{player + 1}_days_in_current_team{team_id}'][self.MATCH_ID] = 0
            self.df[f'player{player + 1}_days_in_all_team{team_id}'][self.MATCH_ID] = 0

    def add_5_players(self, team_id):
        for player in range(5):
            if f'player{player + 1}_teams_all_team{team_id}' not in self.df:
                self.df[f'player{player + 1}_teams_all_team{team_id}'] = ""
            if f'player{player + 1}_days_in_current_team{team_id}' not in self.df:
                self.df[f'player{player + 1}_days_in_current_team{team_id}'] = ""
            if f'player{player + 1}_days_in_all_team{team_id}' not in self.df:
                self.df[f'player{player + 1}_days_in_all_team{team_id}'] = ""
            if self.df[f'player{player + 1}_days_in_current_team{team_id}'][self.MATCH_ID] == "" or\
                self.df[f'player{player + 1}_days_in_all_team{team_id}'][self.MATCH_ID] == "" or\
                self.df[f'player{player + 1}_teams_all_team{team_id}'][self.MATCH_ID] == "":
                self._get_player_stat_(team_id, player)
            

PL_STAT_ALL = 'https://www.hltv.org/stats/players'

class PlStatAll:
    def __init__(self, df, months=3, start_index=0, finish_index=None):
        self.df = df
        self.PL_PAGE = None
        self.MATCH_ID = None
        self.start_index = start_index
        self.finish_index = finish_index
        self.start_date = None
        self.finish_date = None
        self.months = months
        self.params_1 = ['Total kills', 'Headshot %', 'Total deaths', 'K/D Ratio',
            'Damage / Round', 'Grenade dmg / Round', 'Maps played', 'Rounds played',
            'Kills / round', 'Assists / round', 'Deaths / round',
            'Saved by teammate / round', 'Saved teammates / round', 'Rating 2.0']
        self.params_2 = ['vs top 5 opponents', 'vs top 10 opponents', 'vs top 20 opponents',
            'vs top 30 opponents', 'vs top 50 opponents']

    def add_all_params(self):
        time_start = time.time()
        for date, index in zip(df['date'][self.start_index:self.finish_index],
                               range(len(df.iloc[self.start_index:self.finish_index]))):
            self.MATCH_ID = index + self.start_index
            print('match id -', self.MATCH_ID, '; time spent -', time.time() - time_start)
            self.start_date = (datetime.strptime(date, '%Y-%m-%d') - relativedelta(months=self.months)).strftime("%Y-%m-%d")
            self.finish_date = (datetime.strptime(date, '%Y-%m-%d') - relativedelta(days=1)).strftime("%Y-%m-%d")
            self.add_5_players_stat(1)
            self.add_5_players_stat(2)
        self.processing_age(self.df)
        self.processing_maps(self.df)
        self.processing_procent(self.df)


    def processing_age(self, df):
        for i in range(len(df)):
            for team_id in range(1, 3):
                for player_id in range(5):
                    if df[f'age_player{player_id + 1}_team{team_id}'][i] == '':
                        df[f'age_player{player_id + 1}_team{team_id}'][i] = 0
                    df[f'age_player{player_id + 1}_team{team_id}'][i] =\
                            re.sub(r'[^\d]', '', str(df[f'age_player{player_id + 1}_team{team_id}'][i]))


    def processing_maps(self, df):
        for i in range(len(df)):
            for team_id in range(1, 3):
                for player_id in range(5):
                    for param in self.params_2:
                        if str(df[f'{param}_maps_player{player_id + 1}_team{team_id}'][i])[0] == '(':
                            df[f'{param}_maps_player{player_id + 1}_team{team_id}'][i] =\
                                    df[f'{param}_maps_player{player_id + 1}_team{team_id}'][i].\
                                    split('(')[1].split(' maps')[0]


    def processing_procent(self, df):
        for i in range(len(df)):
            for team_id in range(1, 3):
                for player_id in range(5):
                    for param in self.params_1:  # Headshot %_player1_team1
                        if str(df[f'{param}_player{player_id + 1}_team{team_id}'][i])[-1] == '%':
                            df[f'{param}_player{player_id + 1}_team{team_id}'][i] =\
                                float(str(df[f'{param}_player{player_id + 1}_team{team_id}'][i])[:-1]) / 100


    def _get_player_stat_(self, team_id, player_id, params_1, params_2):
        def find_row1(stats_row, param):
            for i in stats_row:
                if i.find('span').text == param:
                    return i.find_all('span')[-1].text
            return 0
        
        def find_row2(col_custom, param):
            for i in col_custom:
                if i.find('div', {'class': 'rating-description'}).text == param:
                    tmp = [i.find('div', {'class': 'rating-value'}).text, i.find('div', {'class': 'rating-maps'}).text]
                    return [k if k != '-' else 0 for k in tmp]
            return 0, 0
        
        print(team_id, player_id)
        player_url = (df[f'players_url_{team_id}'][self.MATCH_ID])[player_id]
        if player_url:
            self.PL_PAGE = get_parsed_page(PL_STAT_ALL + player_url.split('/player')[-1] +
                                           f'?startDate={self.start_date}&endDate={self.finish_date}',
                                           proxyDict, proxyAuth)
            # age
            self.df[f'age_player{player_id + 1}_team{team_id}'][self.MATCH_ID] = self.PL_PAGE.\
                    find('div', {'class': 'playerSummaryStatBox'}).\
                    find('div', {'class': 'summaryPlayerAge'}).text
            # stat params1
            stat1 = self.PL_PAGE.find('div', {'class': 'statistics'}).find_all('div', {'class': 'stats-row'})
            for param in params_1:
                self.df[f'{param}_player{player_id + 1}_team{team_id}'][self.MATCH_ID] = find_row1(stat1, param)
            # stat params2
            stat2 = self.PL_PAGE.find('div', {'class': 'featured-ratings-container'}).\
                    find_all('div', {'class': 'col-custom'})
            for param in params_2:
                (self.df[f'{param}_player{player_id + 1}_team{team_id}'][self.MATCH_ID],
                self.df[f'{param}_maps_player{player_id + 1}_team{team_id}'][self.MATCH_ID]) = \
                find_row2(stat2, param)
        else:
            for param in params_1:
                self.df[f'{param}_player{player_id + 1}_team{team_id}'][self.MATCH_ID] = 0
            for param in params_2:
                self.df[f'{param}_player{player_id + 1}_team{team_id}'][self.MATCH_ID] = 0
                self.df[f'{param}_maps_player{player_id + 1}_team{team_id}'][self.MATCH_ID] = 0
            self.df[f'age_player{player_id + 1}_team{team_id}'][self.MATCH_ID] = 0
            

    def add_5_players_stat(self, team_id):
        def check_null_in_line(player_id, params_1, params_2):
            for param in params_1:
                if self.df[f'{param}_player{player_id + 1}_team{team_id}'][self.MATCH_ID] == "":
                    return 1
            for param in params_2:
                if self.df[f'{param}_player{player_id + 1}_team{team_id}'][self.MATCH_ID] == "" or \
                    self.df[f'{param}_maps_player{player_id + 1}_team{team_id}'][self.MATCH_ID] == "":
                    return 1
            if self.df[f'age_player{player_id + 1}_team{team_id}'][self.MATCH_ID] == "":
                return 1
            return 0

        for player in range(5):
            for param in self.params_1:
                if f'{param}_player{player + 1}_team{team_id}' not in self.df:
                    self.df[f'{param}_player{player + 1}_team{team_id}'] = ""
            for param in self.params_2:
                if f'{param}_player{player + 1}_team{team_id}' not in self.df:
                    self.df[f'{param}_player{player + 1}_team{team_id}'] = ""
                if f'{param}_maps_player{player + 1}_team{team_id}' not in self.df:
                    self.df[f'{param}_maps_player{player + 1}_team{team_id}'] = ""
            if f'age_player{player + 1}_team{team_id}' not in self.df:
                self.df[f'age_player{player + 1}_team{team_id}'] = ""
            if check_null_in_line(player, self.params_1, self.params_2):
                self._get_player_stat_(team_id, player, self.params_1, self.params_2)


MAP_STAT_PR = 'https://www.hltv.org/stats/teams/map/'
id_maps = {
'Dust2': 31,
'Inferno': 33,
'Mirage': 32,
'Nuke': 34,
'Overpass': 40,
'Train': 35,
'Vertigo': 46,
}

def preprocess_allmapsstat(df):
    columns = ['Times played', 'Total rounds played', 'Rounds won', 'Win percent',
                               'Pistol rounds', 'Pistol rounds won', 'Pistol round win percent',
                               'CT round win percent', 'T round win percent']
    columns1 = ['Round win percent after getting first kill',
                                'Round win percent after receiving first death']
    for i in columns:
        for k in list(df.filter(regex=i, axis=1).columns):
            for idx in range(len(df)):
                if str(df[k][idx])[-1] == '%':
                    df[k][idx] = float(str(df[k][idx])[:-1]) / 100
    for i in columns1:
        for k in list(df.filter(regex=i, axis=1).columns):
            for idx in range(len(df)):
                if str(df[k][idx])[-1] == '%':
                    df[k][idx] = float(str(df[k][idx])[:-1]) / 100

class AllMapsStat:
    def __init__(self, df, last_maps=20, months=3, start_index=0, finish_index=None):
        self.df = df
        self.STAT_PAGE = None
        self.idx = None
        self.start_index = start_index
        self.finish_index = finish_index
        self.start_date = None
        self.finish_date = None
        self.last_maps = last_maps
        self.months = months

    def add_all_params(self):
        time_start = time.time()
        for date, index in zip(self.df['date'][self.start_index:self.finish_index],
                       range(len(self.df.iloc[self.start_index:self.finish_index]))):
            self.idx = index + self.start_index
            print('match id -', self.idx, '; time spent -', time.time() - time_start)
            self.start_date = (datetime.strptime(date, '%Y-%m-%d') - relativedelta(months=self.months)).strftime("%Y-%m-%d")
            self.finish_date = (datetime.strptime(date, '%Y-%m-%d') - relativedelta(days=1)).strftime("%Y-%m-%d")
            self.add_map_in_df([i for i in id_maps])
        preprocess_allmapsstat(self.df)
    
    
    
    def _get_stat_(self, team_id, params, params1, params2, map_name):
        def _get_params_(team_id, param, table):
            for i in table:
                if i.find('span').text == param:
                    return i.find_all('span')[-1].text
            print('Not find')
            return 0

        def _get_params1_(team_id, param, table):
            for i in table:
                if i.find_all('div')[1].text == param:
                    return i.find('div').text
            print('Not find')
            return 0
    
        def _get_params2_(team_id, param, table):
            score = table.find('td', {'class': 'statsTeamMapResult'}).text
            score = score.split(' - ')
            return score
            
        tmp = self.STAT_PAGE.find_all('div', {'class': 'columns'})
        table = tmp[0].find('div', {'class': 'stats-rows'}).\
                find_all('div', {'class': 'stats-row'})
        for param in params:
            self.df[param + map_name + f'_team{team_id}'][self.idx] = _get_params_(team_id, param, table)
        table = tmp[1].find_all('div', {'class': 'big-padding'})
        for param in params1:
            self.df[param + map_name + f'_team{team_id}'][self.idx] = _get_params1_(team_id, param, table)
        table = self.STAT_PAGE.find('table', {'class': 'stats-table'}).\
                find('tbody').find_all('tr')
        for pos in range(len(params2)):
            param = params2[pos]
            if pos < len(table):
                [self.df[param + map_name + f'_team{team_id}'][self.idx],
                 self.df[param + map_name + '_opponent' + f'_team{team_id}'][self.idx]] = _get_params2_(team_id, param, table[pos])
            else:
                self.df[param + map_name + f'_team{team_id}'][self.idx] = 0
                self.df[param + map_name + '_opponent' + f'_team{team_id}'][self.idx] = 0

    
    def add_map_in_df(self, maps_name):
        def check_null_in_line(team_id, params, params1, params2):
            for param in params:
                if self.df[param + map_name + f'_team{team_id}'][self.idx] == "":
                    return 1
            for param in params1:
                if self.df[param + map_name + f'_team{team_id}'][self.idx] == "":
                    return 1
            for param in params2:
                if self.df[param + map_name + f'_team{team_id}'][self.idx] == "" or\
                        self.df[param + map_name + '_opponent' + f'_team{team_id}'][self.idx] == "":
                    return 1
            return 0
        
        for map_name in maps_name:
            # print(map_name)
            if map_name:
                columns = ['Times played', 'Total rounds played', 'Rounds won', 'Win percent',
                           'Pistol rounds', 'Pistol rounds won', 'Pistol round win percent',
                           'CT round win percent', 'T round win percent']
                columns1 = ['Round win percent after getting first kill',
                            'Round win percent after receiving first death']
                columns2 = [f'map_played{k + 1}'
                            for k in range(self.last_maps)]
                for team_id in range(1, 3):
                    for i in columns:
                        if i + map_name + f'_team{team_id}' not in df:
                            self.df[i + map_name + f'_team{team_id}'] = ""
                    for i in columns1:
                        if i + map_name + f'_team{team_id}' not in df:
                            self.df[i + map_name + f'_team{team_id}'] = ""
                    for i in columns2:
                        if i + map_name + f'_team{team_id}' not in df:
                            self.df[i + map_name + f'_team{team_id}'] = ""
                            self.df[i + map_name + '_opponent' + f'_team{team_id}'] = ""
                # print(self.idx)
                for team_id in range(1, 3):
                    if check_null_in_line(team_id, columns, columns1, columns2):
                        url = MAP_STAT_PR + str(id_maps[map_name]) + '/' +\
                              (df[f'url_team{team_id}'][self.idx]).split('/team/')[-1] +\
                              f'?startDate={self.start_date}&endDate={self.finish_date}'
                        print(url)
                        self.STAT_PAGE = get_parsed_page(url, proxyDict, proxyAuth)
                        self._get_stat_(team_id, columns, columns1, columns2, map_name)


MAP_STAT_PR = 'https://www.hltv.org/stats/teams/map/'


class MapsStatTeamFull:
    def __init__(self, df, last_maps=20, months=3, start_index=0, finish_index=None):
        self.df = df
        self.dfNew = None
        self.STAT_PAGE = None
        self.MATCH_ID = None
        self.idx = 0
        self.start_index = start_index
        self.finish_index = finish_index
        self.start_date = None
        self.finish_date = None
        self.last_maps = last_maps
        self.months = months

    def add_all_params(self):
        time_start = time.time()
        for maps_url, maps_name, date, score1_maps, score2_maps, picks, index\
            in zip(self.df['maps_url'][self.start_index:self.finish_index],
                       self.df['maps_name'][self.start_index:self.finish_index],
                       self.df['date'][self.start_index:self.finish_index],
                       self.df['score1_maps'][self.start_index:self.finish_index],
                       self.df['score2_maps'][self.start_index:self.finish_index],
                       self.df['picks'][self.start_index:self.finish_index],
                       range(len(self.df.iloc[self.start_index:self.finish_index]))):
            #print(index)
            self.MATCH_ID = index + self.start_index
            print('match id -', self.MATCH_ID, '; time spent -', time.time() - time_start)
            #print(maps_name)
            #print(df['url_team1'][self.MATCH_ID])
            self.start_date = (datetime.strptime(date, '%Y-%m-%d') - relativedelta(months=self.months)).strftime("%Y-%m-%d")
            self.finish_date = (datetime.strptime(date, '%Y-%m-%d') - relativedelta(days=1)).strftime("%Y-%m-%d")
            if maps_name != 'None':
                self.add_map_in_df(maps_url, maps_name,
                                   score1_maps, score2_maps, picks)
        return self.dfNew
    
    
    
    def _get_stat_(self, team_id, params, params1, params2, score1_map, score2_map, counter, picks):
        def _get_params_(team_id, param, table):
            for i in table:
                if i.find('span').text == param:
                    return i.find_all('span')[-1].text
            print('Not find')
            return 0

        def _get_params1_(team_id, param, table):
            for i in table:
                if i.find_all('div')[1].text == param:
                    return i.find('div').text
            print('Not find')
            return 0
    
        def _get_params2_(team_id, param, table):
            score = table.find('td', {'class': 'statsTeamMapResult'}).text
            score = score.split(' - ')
            return score
            
        tmp = self.STAT_PAGE.find_all('div', {'class': 'columns'})
        table = tmp[0].find('div', {'class': 'stats-rows'}).\
                find_all('div', {'class': 'stats-row'})
        for param in params:
            self.dfNew[param + f'_team{team_id}'][self.idx] = _get_params_(team_id, param, table)
        table = tmp[1].find_all('div', {'class': 'big-padding'})
        for param in params1:
            self.dfNew[param + f'_team{team_id}'][self.idx] = _get_params1_(team_id, param, table)
        table = self.STAT_PAGE.find('table', {'class': 'stats-table'}).\
                find('tbody').find_all('tr')
        for pos in range(len(params2)):
            param = params2[pos]
            if pos < len(table):
                [self.dfNew[param + f'_team{team_id}'][self.idx],
                self.dfNew[param + '_opponent' + f'_team{team_id}'][self.idx]] = _get_params2_(team_id, param, table[pos])
            else:
                self.dfNew[param + f'_team{team_id}'][self.idx] = 0
                self.dfNew[param + '_opponent' + f'_team{team_id}'][self.idx] = 0
        self.dfNew['map_score1'][self.idx] = score1_map
        self.dfNew['map_score2'][self.idx] = score2_map
        if picks and counter < len(picks):
            if picks[counter] == 1:
                self.dfNew['pick1'][self.idx] = 1
                self.dfNew['pick2'][self.idx] = 0
            elif picks[counter] == -1:
                self.dfNew['pick2'][self.idx] = 1
                self.dfNew['pick1'][self.idx] = 0
        else:
            self.dfNew['pick1'][self.idx] = 0
            self.dfNew['pick2'][self.idx] = 0

    
    def add_map_in_df(self, maps_url, maps_name, score1_maps, score2_maps, picks):
        def check_null_in_line(team_id, params, params1, params2):
            for param in params:
                if self.dfNew[param + f'_team{team_id}'][self.idx] == "":
                    return 1
            for param in params1:
                if self.dfNew[param + f'_team{team_id}'][self.idx] == "":
                    return 1
            for param in params2:
                if self.dfNew[param + f'_team{team_id}'][self.idx] == "" or\
                        self.dfNew[param + '_opponent' + f'_team{team_id}'][self.idx] == "":
                    return 1
            for param in ['map_score1', 'map_score2', 'pick1', 'pick2']:
                if self.dfNew[param][self.idx] == "":
                    return 1
            return 0
        
        for map_url, map_name, score1_map, score2_map, counter \
                in zip(maps_url, maps_name, score1_maps, score2_maps, range(len(maps_name))):
            # print(map_name)
            if map_name:
                columns = ['Times played', 'Total rounds played', 'Rounds won', 'Win percent',
                           'Pistol rounds', 'Pistol rounds won', 'Pistol round win percent',
                           'CT round win percent', 'T round win percent']
                columns1 = ['Round win percent after getting first kill',
                            'Round win percent after receiving first death']
                columns2 = [f'current_map_played_{k + 1}'
                            for k in range(self.last_maps)]
                if self.dfNew is None:
                    self.dfNew = self.df.iloc[self.MATCH_ID:self.MATCH_ID + 1].copy()
                    self.idx = 0
                    for team_id in range(1, 3):
                        for i in ['map_score1', 'map_score2', 'pick1', 'pick2']:
                            self.dfNew[i] = ""
                        for i in columns:
                            self.dfNew[i + f'_team{team_id}'] = ""
                        for i in columns1:
                            self.dfNew[i + f'_team{team_id}'] = ""
                        for i in columns2:
                            self.dfNew[i + f'_team{team_id}'] = ""
                            self.dfNew[i + '_opponent' + f'_team{team_id}'] = ""
                else:
                    self.dfNew = self.dfNew.append(self.df.iloc[self.MATCH_ID:self.MATCH_ID + 1].copy(), ignore_index=True)
                    self.idx += 1
                # print(self.idx)
                for team_id in range(1, 3):
                    #if check_null_in_line(team_id, columns, columns1, columns2):
                    url = MAP_STAT_PR + str(id_maps[map_name]) + '/' +\
                          (df[f'url_team{team_id}'][self.MATCH_ID]).split('/team/')[-1] +\
                          f'?startDate={self.start_date}&endDate={self.finish_date}'
                    print(url)
                    self.STAT_PAGE = get_parsed_page(url, proxyDict, proxyAuth)
                    self._get_stat_(team_id, columns, columns1, columns2,
                                    score1_map, score2_map, counter, picks)



