
from parser import Parser


def get_schedule(*league_ids):
    games = Parser.get_upcoming_matches()
    live = []
    upcoming = []
    reply = ''
    for game in games:
        if int(game['timediff']) < 0:
            live.append(game)
        else:
            upcoming.append(game)
    # dt1 = datetime.datetime.fromtimestamp(int(time.time()))
    # dt2 = dt1 = datetime.datetime.fromtimestamp(int(games['starttime_unix']))
    # rd = dateutil.relativedelta.relativedelta(dt2, dt1)

    if live:
        reply = "Live games: \n"
        for game in live:
            reply += "{0} - **{1}** vs **{2}** (Bo{3}) \n".format(
                game['league']['name'],
                game['team1']['team_name'],
                game['team2']['team_name'],
                game['series_type'],
                )
    reply += "Upcoming: \n"
    for game in upcoming:
        h, m = divmod(int(game['timediff']), 3600)
        reply += "{0} - Bo({3}) **{1}** vs **{2}** ({4}hr{5}min from now) \n".format(
            game['league']['name'],
            game['team1']['team_name'],
            game['team2']['team_name'],
            game['series_type'],
            h,
            int(m/60)
            )
    return reply


print(get_schedule())