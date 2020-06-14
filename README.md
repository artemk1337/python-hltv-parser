<p align="right">
<a href="https://github.com/artemkush1/hltv_parser/blob/master/LICENSE"><img alt="GitHub license" src="https://img.shields.io/github/license/artemkush1/hltv_parser"></a>
<a href="https://github.com/artemkush1/hltv_parser/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/artemkush1/hltv_parser"></a>
<a href="https://github.com/artemkush1/hltv_parser/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/artemkush1/hltv_parser"></a>
</p> 

# The unofficial HLTV Python API

## INSTALLATION

```
>>> pip3 install -r requirements.txt
```
OR
```
>>> pip3 install requests urllib3 datetime bs4 numpy pandas
```

## USAGE

### Parse matches

```
>>> get_results_url(filename=None, pages_with_results=[0])
```
> ___type: func___ <br />
> Params:
> - *filename* - for saving pandas frame <br />
> - *pages_with_results* - array with numbers of pages with results <br />
>
> Return pandas DataFrame with columns:
> - match_url <br />

---
### Add main common info from match page

```
>>> MatchPageParams(df, start_index=None, finish_index=None)
```
> ___type: class___ <br />
> Params:
> - *df* - pandas frame with match urls
> - *start_index* - start index 
> - *finish_index* - last index

```
>>> MatchPageParams.add_all_params()
```
> ___type: func___ <br />
> Modify pandas frame, add columns:
> - *match_url* - link to the match
> - *event_url* - link to the tournament
> - *players_url_1* - links to players of the 1st team
> - *players_url_2* - links to players of the second team
> - *maps_url* - links to statistics of played maps
> - *maps_name* - map names
> - *score1_maps* - score on each map of team 1
> - *score2_maps* - score on each map of team 2
> - *picks* - peaks of teams; 1 - the first team, -1 - the second team; if the array is None, then the maps are [2
> - *date* - match date
> - *total_maps* - in total it was planned to play cards (usually 1, 3 or 5)
> - *maps_played* - how many cards were played as a result
> - *score1* - score of the 1st team
> - *score2* - score of the 2nd team
> - *h2h_wins1* - history of victories of the 1st team over the 2nd
> - *h2h_wins2* - the history of victories of the 2nd team over the 1st
> - *rank1* - rank of the 1st team
> - *rank2* - rank of the 2nd team
> - *5last_match[match_id]_total_maps[team_id]* - the last 5 matches of the [team_id] (1 or 2); [match_id] - serial number of the match; total maps played
> - *5last_match[match_id]_score[team_id]* - the last 5 matches of the [team_id] (1 or 2); [match_id] - serial number of the match; score [team_id] in this match
> - *5last_match[match_id]_opponent_score[team_id]* - the last 5 matches of the [team_id] (1 or 2); [match_id] - serial number of the match; opponent score in this match

---
### Add last played maps each team

```
>>> LastMaps(df, last_maps=20, months=3, start_index=None, finish_index=None)
```
> ___type: class___ <br />
> Params:
> - *df* - pandas frame from previous step
> - *last_maps* - last X played maps
> - *months* - time period
> - *start_index* - start index 
> - *finish_index* - last index

```
>>> LastMaps.add_all_params()
```
> ___type: func___ <br />
> Modify pandas frame, add columns:
> - *last_maps [id] _score [team_id]* - team*s score; id - map number, team_id - team number (team1 or team2)
> - *last_maps [id] _opponent_score [team_id]* - opponent’s score; id - map number, team_id - team number (team1 or team2)

---
### Add info about tournament

```
>>> Tour(df, start_index=None, finish_index=None)
```
> ___type: class___ <br />
> Params:
> - *df* - pandas frame from previous step
> - *start_index* - start index 
> - *finish_index* - last index

```
>>> Tour.add_all_params()
```
> ___type: func___ <br />
> Modify pandas frame, add columns:
> - *event_type* - type of tournament (Lan or Online)
> - *event_teams* - the number of teams in the tournament
> - *prize_pool* - prize pool of the tournament

---
### Add played time in teams each player

```
>>> PlStatInTeam(df, start_index=None, finish_index=None)
```
> ___type: class___ <br />
> Params:
> - *df* - pandas frame from previous step
> - *start_index* - start index 
> - *finish_index* - last index

```
>>> PlStatInTeam.add_all_params()
```
> ___type: func___ <br />
> Modify pandas frame, add columns: <br />
> playerID - player number (from 1 to 5); team_id - team number (1 or 2)
> - *player [playerID]_days_in_current_team[team_id]* - days how long player is in the team (0 or more)
> - *player[playerID]_days_in_all_team[team_id]* - days how long player is in all teams (0 or more)
> - *player[playerID]_teams_all_team[team_id]* - the number of teams the player was in (0 or more)

---
### Add all stats each player

```
>>> PlStatAll(df, months=3, start_index=None, finish_index=None)
```
> ___type: class___ <br />
> Params:
> - *df* - pandas frame from previous step
> - *months* - time period
> - *start_index* - start index 
> - *finish_index* - last index

```
>>> LastMaps.add_all_params()
```
> ___type: func___ <br />
> Modify pandas frame, add columns: <br />
> - *[param] _player [player] _team [team_id]* - player statistics
> - *[param] _maps_player [player_id] _team {team_id}* - played maps for calculating statistics (only some parameters)
> - *age_player [player_id] _team [team_id]* - player age

---
### Add stats on all maps each team

```
>>> AllMapsStat(df, last_maps=20, months=3, start_index=None, finish_index=None)
```
> ___type: class___ <br />
> Params:
> - *df* - pandas frame from previous step
> - *last_maps* - last X played maps on map
> - *months* - time period
> - *start_index* - start index 
> - *finish_index* - last index

```
>>> LastMaps.add_all_params()
```
> ___type: func___ <br />
> Modify pandas frame, add columns: <br />
> - *[param][map]_team[team_id]*
> - *map_played[id]_team[team_id]* - score; [id] - serial number of played map
> - *map_played[id]_opponent_team[team_id]* - opponent score; [id] - serial number of played map

---
### Split DataFrame on maps and save stats on played map each team

```
>>> MapsStatTeamFull(df, last_maps=20, months=3, start_index=None, finish_index=None)
```
> ___type: class___ <br />
> Params:
> - *df* - pandas frame from previous step
> - *last_maps* - last X played maps on map
> - *months* - time period
> - *start_index* - start index 
> - *finish_index* - last index

```
>>> MapsStatTeamFull.add_all_params()
```
> ___type: func___ <br />
> Modify pandas frame, add columns: <br />
> - *[param]_team[team_id]*
> - *current_map_played_[id]_team[team_id]* - score; [id] - serial number of played map
> - *current_map_played_[id]_opponent_team[team_id]* - opponent score; [id] - serial number of played map
>
> Return new pandas DataFrame with all columns









