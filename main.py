import requests
import creds
import pandas as pd

def myGames():
    my_steamid = '76561198070917858'

    my_owned_games = requests.get(f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={creds.api_key}&steamid={my_steamid}&format=json').json()

    data = my_owned_games['response']['games']

    rows = {
        'appid': [],
        'playtime_forever': [],
        'rtime_last_played': []
    }

    for app in data:
        rows['appid'].append(app['appid'])
        rows['playtime_forever'].append(app['playtime_forever'])
        rows['rtime_last_played'].append(app['rtime_last_played'])

    df = pd.DataFrame(rows)
    df['appid'] = df['appid'].astype(str)
    return df

def gameDetails():
    games = myGames()['appid']

    details_rows = {
        'appid': [],
        'name': [],
        'header_image': [],
        'metacritic_score': []
        }

    for app in games:
        url = f'http://store.steampowered.com/api/appdetails?appids={app}'
        response = requests.get(url)
        json = response.json()

        details_rows['appid'].append(app)

        try:
            name_row = json[app]['data']['name']
            details_rows['name'].append(name_row)
        except KeyError:
            details_rows['name'].append(None)

        try:
            if 'header_image' in json[app]['data']:
                header_image_row = json[app]['data']['header_image']
                details_rows['header_image'].append(header_image_row)
            else:
                details_rows['header_image'].append(None)
        except KeyError:
            details_rows['header_image'].append(None)

        try:
            if 'metacritic' in json[app]['data']:
                metacritic_row = json[app]['data']['metacritic']['score']
                details_rows['metacritic_score'].append(metacritic_row)
            else:
                details_rows['metacritic_score'].append(None)
        except KeyError:
            details_rows['metacritic_score'].append(None)

    details_df = pd.DataFrame(details_rows)

    return details_df

def merge():
    right_df = gameDetails()
    left_df = myGames()

    merged_df = left_df.merge(right_df, on='appid', how='left')

    return merged_df

def load():
    final_df = merge()

    final_df.to_csv('steam_game_details.csv', header=True)

if __name__ == '__main__':
    load()