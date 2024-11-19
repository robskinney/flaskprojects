import sqlite3

def saveActor(date,name):
    conn = sqlite3.connect("ActorGuessr.db")
    sql='INSERT INTO actorhistory (date, actor) values (?,?)'
    cur = conn.cursor()
    cur.execute(sql, (date,name))
    conn.commit()

def getActors():
    con = sqlite3.connect('ActorGuessr.db')
    con.row_factory = sqlite3.Row
    cursorObj = con.cursor()
    actors = {}
    cursorObj.execute('SELECT * FROM actorhistory')
    rows = cursorObj.fetchall()
    for individualRow in rows:
        actors[individualRow[0]] = individualRow[1]
    return actors

def newDate(date):
    conn = sqlite3.connect("ActorGuessr.db")
    sql='INSERT INTO todaydata (date, players, won, tips, guesses, besttips, bestguesses) values (?,?,?,?,?,?,?)'
    cur = conn.cursor()
    cur.execute(sql, (date,0,0,0,0,0,0))
    conn.commit()

def newFeedback(email,rating,description):
    conn = sqlite3.connect("ActorGuessr.db")
    sql='INSERT INTO feedback (email,rating,description) values (?,?,?)'
    cur = conn.cursor()
    cur.execute(sql, (email,rating,description))
    conn.commit()

def updateToday(col, date, amount):
    conn = sqlite3.connect("ActorGuessr.db")
    sql="UPDATE todaydata SET {column} = {column} + ? where date = ?".format(column=col)
    cur = conn.cursor()
    cur.execute(sql, (amount, date))
    conn.commit()

def getToday(date):
    con = sqlite3.connect("ActorGuessr.db")
    with con:
        con.row_factory = sqlite3.Row
        cursorObj = con.cursor()
        cursorObj.execute("select * from todaydata where date = ?", (date,))
        data = cursorObj.fetchone()
        obj = {'date':data[0], 'players': data[1], 'won': data[2], 'tips': data[3], 'guesses': data[4], 'besttips': data[5], 'bestguesses': data[6]}
    con.close()
    return obj

def bestPerformance(guesses,tips,date):
    conn = sqlite3.connect("ActorGuessr.db")
    sql="UPDATE todaydata SET bestguesses = (?), besttips = (?) where date = (?)"
    cur = conn.cursor()
    cur.execute(sql, (guesses,tips,date))
    conn.commit()
