from flask import Flask, render_template, request, redirect, url_for, jsonify, g, make_response
import sqlite3
from flask import session
from collections import defaultdict, deque
import datetime
from urllib.parse import quote, unquote
import math

app = Flask(__name__)
app.secret_key = '12345'


@app.route('/')
def index():
    #add daily list, retrieve day, depending on the day give the correct list item. then set up session and cookies and path for start with the daily start/end
    session['bacon']= 0
    session['daily']= False
    daily = retrieve_daily()
    start_daily = daily[0]
    end_daily = daily[1]
    return render_template("index.html", start_daily=start_daily, end_daily=end_daily)

@app.route('/mode')
def mode():
    session['daily']= False
    return render_template('mode.html')

@app.route('/test')
def test():
    # connect to database
    cursor = get_db()
    # Select two random players
    start, end, start_id, end_id = player_picker(cursor)
    start = "Cristiano Ronaldo"
    start_id = 8198
    end = "Casemiro"
    end_id = 16306
    steps = 0
    # Store end_id in session
    route = [start]
    session['route'] = route
    session['start'] = start
    session['end'] = end
    session['end_id'] = end_id
    session['steps'] = steps
    # Select team + year where player_id = start
    teams = retrieve_teams(start_id, cursor)
    help = last_team(end_id, cursor)[0]
    help = f"{help[0]} {help[1]}-{help[1]+1}"
    session['help'] = help
    return render_template('start.html', start=start, end=end, teams=teams, help=help)

@app.route('/balanced')
def balanced():
    # connect to database
    cursor = get_db()
    # Select two random players
    start, start_id = player_picker_balanced(cursor)
    end, end_id = player_picker_balanced(cursor)
    return redirect(url_for('setup', start=start, end=end, start_id=start_id, end_id=end_id))

@app.route('/start')
def start():
    # connect to database
    cursor = get_db()
    # Select two random players
    start, end, start_id, end_id = player_picker(cursor)
    return redirect(url_for("setup", start=start, end=end, start_id=start_id, end_id=end_id))

@app.route('/daily', methods=['GET'])
def daily():
    session['daily'] = True
    daily = retrieve_daily()
    start = daily[0]
    end = daily[1]
    start_id = daily[2]
    end_id = daily[3]
    if request.cookies.get('solved'):
        route_raw = request.cookies.get('route')
        route_raw = unquote(route_raw)
        route = route_raw.split(',')
        steps = math.floor((len(route) - 2)/2)
        #retrieve save cookie and send it in the template
        saved = request.cookies.get('saved')
        return render_template('success.html', steps=steps, route=route, daily=True, saved=saved)
    return redirect(url_for("setup", start=start, end=end, start_id=start_id, end_id=end_id))
    
@app.route('/solve', methods=['GET'])
def solve():
    steps = request.args.get('steps')
    route = request.args.getlist('route')
    resp = make_response(render_template("success.html", steps=steps, route=route, daily=True))
    # Calculate time until next midnight
    now = datetime.datetime.now()
    midnight = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1)
    expires = midnight - now
    resp.set_cookie('solved', 'true', max_age=expires.seconds)
    # Convert the list into a string and encode it
    route_str = quote(','.join(route))
    # Set the cookie
    resp.set_cookie('route', route_str, max_age=expires.seconds)
    return resp

@app.route('/save', methods=['GET', 'POST'])
def save():
    route_raw = request.cookies.get('route')
    route = unquote(route_raw)
    route_steps = route.split(',')
    steps = math.floor((len(route_steps) - 2)/2)
    username = request.form.get('username')
    leaderboard_update(route, steps, username)
    resp = make_response(redirect(url_for("leaderboard")))
    # Calculate time until next midnight
    now = datetime.datetime.now()
    midnight = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1)
    expires = midnight - now
    resp.set_cookie('saved', 'true', max_age=expires.seconds)
    return resp

@app.route('/leaderboard')
def leaderboard():
    scores = retrieve_leaderboard()
    return render_template('leaderboard.html', scores=scores)


@app.route('/setup', methods=['GET'])
def setup():
    # Store end_id in session
    start = request.args.get('start')
    end = request.args.get('end')
    start_id = request.args.get('start_id')
    end_id = request.args.get('end_id')
    cursor = get_db()
    steps = 0
    route = [start]
    session['route'] = route
    session['start'] = start
    session['end'] = end
    session['end_id'] = end_id
    session['steps'] = steps
    # Select team + year where player_id = start
    teams = retrieve_teams(start_id, cursor)
    help = last_team(end_id, cursor)[0]
    help = f"{help[0]} {help[1]}-{help[1]+1}"
    session['help'] = help
    return render_template('start.html', start=start, end=end, teams=teams, help=help)

@app.route('/team', methods=['POST'])
def team():
    team_year = request.form.get('team')
    team_year = team_year.rsplit(' ', 1)
    team = team_year[0]
    year = team_year[1].split("-")[0]
    year = int(year)
    cursor = get_db()
    players = retrieve_players(team, year, cursor)
    steps = session.get('steps')
    steps += 1
    session['steps'] = steps
    start = session.get('start')
    end = session.get('end')
    help = session.get('help')
    route = session.get('route')
    route.append(team)
    session['route'] = route
    return render_template('team.html', players=players, start=start, end=end, help=help)


@app.route('/player', methods=['POST'])
def player():
    # get player from form
    player_id = request.form.get('player_id')
    # Retrieve end_id from session
    end_id = session.get('end_id')
    cursor = get_db()
    route = session.get('route')
    player = retrieve_players(player_id, 0, cursor)[0][0]
    route.append(player)
    session['route'] = route
    # check if id = end otherwise restart
    if int(player_id) == int(end_id):
        steps = session.get('steps')-1
        route = session.get('route')
        if route[-1] == route[-2]:
            route.pop()
        if session.get("daily"):
            return redirect(url_for('solve', steps=steps, route=route))
        return render_template('success.html', steps=steps, route=route)
    else:
        teams = retrieve_teams(player_id, cursor)
        start = session.get('start')
        end = session.get('end')
        help = session.get('help')
        return render_template('start.html', start=start, end=end, teams=teams, help=help)


@app.route('/custom')
def custom():
    if  session.get("custom_player") == "target":
        custom_player_state = session.get("custom_player")
    else:
        session["custom_player"] = "starting"
        custom_player_state = session.get("custom_player")
    return render_template("custom.html", custom_player_state = custom_player_state)


@app.route('/select', methods=['POST'])
def select():
    cursor = get_db()
    player = request.form.get('player_choice')
    result = search(player, cursor)
    if  session.get("custom_player") == "target":
        custom_player_state = session.get("custom_player")
    else:
        session["custom_player"] = "starting"
        custom_player_state = session.get("custom_player")
    return render_template("select.html", result = result, custom_player_state = custom_player_state)

@app.route("/player_select", methods=['POST'])
def player_select():
    if session.get("custom_player") == "starting":
        player_1= request.form.get('player_id')
        session['player_1'] = player_1
        cursor= get_db()
        start = retrieve_players(player_1, 0, cursor)
        session['player_1_name'] = start
        session['custom_player'] = "target"
        return redirect(url_for('custom'))
    start_id = session.get('player_1')
    end_id = request.form.get('player_id')
    start = session.get('player_1_name')[0]
    cursor= get_db()
    end = retrieve_players(end_id, 0, cursor)[0]
    session["custom_player"] = "starting"
    bacon = session.get('bacon')
    if bacon == 1:
        return redirect(url_for("oracle_result", start=start, end=end, start_id=start_id, end_id=end_id))
    return redirect(url_for("setup", start=start, end=end, start_id=start_id, end_id=end_id))

@app.route('/oracle')
def oracle():
    session['bacon']=1
    return redirect(url_for("custom"))

@app.route('/oracle_result')
def oracle_result():
    cursor = get_db()
    bacon = session.get('bacon')
    if bacon == 1:
        player1 = request.args.get('start')
        player2 = request.args.get('end')
        player1_id = request.args.get('start_id')
        player2_id = request.args.get('end_id')
    else:
        player1, player2, player1_id, player2_id = player_picker(cursor)
    graph = create_graph()
    shortest_path = bfs(graph, int(player1_id), int(player2_id))
    path=[]
    for pair in shortest_path:
        if pair[1]:
            path.append(cursor.execute("SELECT name FROM clubs WHERE id = ?", (pair[1],)).fetchall()[0])
        path.append(cursor.execute("SELECT name FROM players WHERE id = ?", (pair[0],)).fetchall()[0])
    return render_template('oracle_result.html', path=path, player1=player1, player2=player2)


def player_picker(cursor):
    start, end = cursor.execute(
        "SELECT id,name FROM 'players' ORDER BY RANDOM() LIMIT 2").fetchall()
    while(start == end):
        start, end = cursor.execute(
        "SELECT id,name FROM 'players' ORDER BY RANDOM() LIMIT 2").fetchall()
    start_id = start[0]
    end_id = end[0]
    start = start[1]
    end = end[1]
    return start, end, start_id, end_id


def retrieve_teams(player, cursor):
    return cursor.execute(f"SELECT clubs.name, rosters.year FROM rosters JOIN clubs ON clubs.id = rosters.club_id WHERE player_id = ? ORDER BY rosters.year", (player,)).fetchall()


def retrieve_players(team, year, cursor):
    if year == 0:
        return cursor.execute(f"SELECT players.name FROM players JOIN rosters ON rosters.player_id = players.id WHERE player_id = ?", (team, )).fetchall()
    return cursor.execute(f"SELECT players.id, position, players.name, dob, nationality FROM players JOIN rosters ON rosters.player_id = players.id WHERE club_id = (SELECT id FROM clubs WHERE name = ?) AND rosters.year = ?", (team, year, )).fetchall()


def last_team(player, cursor):
    team=cursor.execute(f"SELECT clubs.name, rosters.year FROM rosters JOIN clubs ON clubs.id = rosters.club_id WHERE rosters.player_id = ? ORDER BY rosters.year DESC LIMIT 1", (player, )).fetchall()
    return team

def create_graph():
    conn = sqlite3.connect('football.db')
    cursor = conn.cursor()

    # Query to get pairs of players who have been in the same club in the same year
    query = """
    SELECT r1.player_id, r2.player_id, r1.club_id
    FROM rosters r1
    JOIN rosters r2 ON r1.year = r2.year AND r1.club_id = r2.club_id
    WHERE r1.player_id != r2.player_id
    """

    cursor.execute(query)
    pairs = cursor.fetchall()

    graph = defaultdict(list)
    for player1, player2, club in pairs:
        graph[player1].append((player2, club))
        graph[player2].append((player1, club))

    return graph

def bfs(graph, start, end):
    queue = deque([(start, [(start, None)])])
    while queue:
        node, path = queue.popleft()
        for next_node, club in graph[node]:
            if next_node == end:
                return path + [(next_node, club)]
            else:
                queue.append((next_node, path + [(next_node, club)]))

def player_picker_balanced(cursor):
    query = "SELECT id,name FROM players WHERE id IN(SELECT player_id FROM rosters WHERE player_values > 10000000) ORDER BY RANDOM() LIMIT 1;"
    end = cursor.execute(query).fetchall()
    end_id = end[0][0]
    end = end[0][1]
    return end, end_id

def search(player, cursor):
    if player == "":
        return cursor.execute("SELECT id, position, name, dob, nationality FROM players ORDER BY RANDOM() LIMIT 15")
    player = '"{}"'.format(player)
    result = cursor.execute("SELECT id, position, name, dob, nationality FROM players WHERE id IN (SELECT rowid FROM rosters_fts WHERE name MATCH ? LIMIT 15)", (player,)).fetchall()
    return result

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect("football.db")
        g.cursor = g.db.cursor()
    return g.cursor


def retrieve_daily():
    cursor = get_db()
    day = datetime.datetime.now().strftime("%Y-%m-%d")
    return cursor.execute("SELECT start_name, end_name, start_id, end_id FROM daily WHERE day = ?", (day, )).fetchall()[0]

def leaderboard_update(route, steps, username):
    connection = sqlite3.connect('football.db')
    cursor = connection.cursor()
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO leaderboard (username, steps, route, day) VALUES (?, ?, ?, ?)", (username, steps, route, date))
    connection.commit()

def retrieve_leaderboard():
    cursor = get_db()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    return cursor.execute("SELECT username, steps, route, day FROM leaderboard WHERE day = ? ORDER BY steps LIMIT 200", (today,))   

@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


if __name__ == "__main__":
    app.run(debug=True)
