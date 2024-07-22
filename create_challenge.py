import sqlite3
import datetime

def main(): 
    #connect database
    connect = sqlite3.connect("football.db")
    cursor = connect.cursor()

    while True:
    #input start and end
        start = input("Start player: ")
        end = input("Target player: ")
        day = date(cursor)       
        #update table with names and ids + time
        players_start = []
        players_end = []
        players_start.append(cursor.execute("SELECT rowid, name FROM rosters_fts WHERE name MATCH ?", (start, )).fetchall())
        players_end.append(cursor.execute("SELECT rowid, name FROM rosters_fts WHERE name MATCH ?", (end, )).fetchall())    
        if len(players_start[0]) == 1 and len(players_end[0]) == 1:
            start_id = [i[0] for i in players_start[0]][0]
            start_name = [i[1] for i in players_start[0]][0]
            end_id = [i[0] for i in players_end[0]][0]
            end_name = [i[1] for i in players_end[0]][0]
            cursor.execute("INSERT INTO daily (day, start_name, end_name, start_id, end_id) VALUES (?,?,?,?,?)", (day, start_name, end_name, start_id, end_id))
            connect.commit()
        #if more than one name matches, give the option in the terminal to choose
        else:
            if len(players_start[0]) != 1 and players_start:
                for i in range(len(players_start[0])):
                    print(i,players_start[0][i])
                choice = int(input("Pick: "))
                start = players_start[0][choice]
                start_name = start[1]
                start_id = start[0]
            else:
                start_id = [i[0] for i in players_start[0]][0]
                start_name = [i[1] for i in players_start[0]][0]

            if len(players_end[0]) != 1 and players_end:
                for i in range(len(players_end[0])):
                    print(i,players_end[0][i])
                choice = int(input("Pick: "))
                end = players_end[0][choice]
                end_name = end[1]
                end_id = end[0]   
            else:
                end_id = [i[0] for i in players_end[0]][0]
                end_name = [i[1] for i in players_end[0]][0]

            cursor.execute("INSERT INTO daily (day, start_name, end_name, start_id, end_id) VALUES (?,?,?,?,?)", (day, start_name, end_name, start_id, end_id))
            connect.commit()

def date(cursor):
    day = cursor.execute("SELECT MAX(day) FROM daily").fetchall()
    day = day[0][0]
    format = "%Y-%m-%d"
    day =  datetime.datetime.strptime(day, format).date()
    day = day + datetime.timedelta(days=1)
    return day

if __name__ == "__main__":
    main()