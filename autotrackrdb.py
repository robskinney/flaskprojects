import sqlite3

import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

#this function accesses the database and acquires every event, putting them in a list of dictionaries
def get_events():
    con = sqlite3.connect(os.path.join(APP_ROOT,'Events.db'))
    with con:
        con.row_factory = sqlite3.Row
        cursorObj = con.cursor()
        cursorObj.execute("select * from events order by date,name")
        events = cursorObj.fetchall()
    con.close()
    return events

#this will take the user's input and add another event to the events table
def add_event(name,date,host,description):
    con = sqlite3.connect(os.path.join(APP_ROOT,'Events.db'))
    with con:
        con.row_factory = sqlite3.Row
        cursorObj = con.cursor()
        cursorObj.execute("insert into events (name,date,host,description) values (?, ?, ?, ?)", (name,date,host,description))
        con.commit()
    con.close()

#very similar to the get_events function, this one just gets all the info from one event based on the event_id
def get_event(event_id):
    con = sqlite3.connect(os.path.join(APP_ROOT,'Events.db'))
    with con:
        con.row_factory = sqlite3.Row
        cursorObj = con.cursor()
        cursorObj.execute("select * from events where id = ?", event_id)
        event = cursorObj.fetchone()
    con.close()
    return event

#this function will allow the user to edit every value in a particular event
def edit_event(event_id,name,date,host,description):
    con = sqlite3.connect(os.path.join(APP_ROOT,'Events.db'))
    with con:
        con.row_factory = sqlite3.Row
        cursorObj = con.cursor()
        cursorObj.execute("UPDATE events SET name = ?, date = ?, host = ?, description = ? WHERE id= ?", (name,date,host,description,event_id))
        con.commit()
    con.close()

#this allows us to delete a particular event from the database
def delete_event(event_id):
    con = sqlite3.connect(os.path.join(APP_ROOT,'Events.db'))
    with con:
        con.row_factory = sqlite3.Row
        cursorObj = con.cursor()
        cursorObj.execute("delete from attendees where event_id = ?", (event_id))
        cursorObj.execute("delete from events where id = ?", (event_id))
        con.commit()
    con.close()

#these next several are very similar to the events respective functions
def get_attendees(event_id):
    con = sqlite3.connect(os.path.join(APP_ROOT,'Events.db'))
    with con:
        con.row_factory = sqlite3.Row
        cursorObj = con.cursor()
        cursorObj.execute("SELECT * FROM attendees WHERE event_id = ? ORDER BY name", (event_id))
        attendees = cursorObj.fetchall()
    con.close()
    return attendees

def get_attendee(attendee_id):
    con = sqlite3.connect(os.path.join(APP_ROOT,'Events.db'))
    with con:
        con.row_factory = sqlite3.Row
        cursorObj = con.cursor()
        cursorObj.execute("select * from attendees where id = ?", (attendee_id))
        attendee = cursorObj.fetchone()
    con.close()
    return attendee

def add_attendee_db(event_id,name,email,comment):
    con = sqlite3.connect(os.path.join(APP_ROOT,'Events.db'))
    with con:
        con.row_factory = sqlite3.Row
        cursorObj = con.cursor()
        cursorObj.execute("insert into attendees(event_id,name,email,comment) values (?,?,?,?)", (event_id,name,email,comment))
        con.commit()
    con.close()

def edit_attendee_db(id,event_id,name,email,comment):
    con = sqlite3.connect(os.path.join(APP_ROOT,'Events.db'))
    with con:
        con.row_factory = sqlite3.Row
        cursorObj = con.cursor()
        cursorObj.execute("update attendees set name = ?, email = ?, comment = ? where id = ? and event_id= ?", (name,email,comment,id,event_id))
        con.commit()
    con.close()

def del_attendee_db(attendee_id,event_id):
    con = sqlite3.connect(os.path.join(APP_ROOT,'Events.db'))
    with con:
        con.row_factory = sqlite3.Row
        cursorObj = con.cursor()
        cursorObj.execute("delete from attendees where id = ? and event_id = ?", (attendee_id, event_id))
        con.commit()
    con.close()




