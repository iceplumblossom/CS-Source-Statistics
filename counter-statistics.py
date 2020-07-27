#!/usr/bin/env python3

import re
import sqlite3
import sys
import webbrowser
import os
from tabulate import tabulate

helpstr = '''This script need a txt file as an input. The path of the input file must be given as command line argument.
arguments   :   [path/to/txt] [-b]  
or 
only        :   [-h]
-------
Options
-------
    -b          : If you want the produced html file to be opened in default browser.
    -h, --help  : to see this message
'''

try:
    INPUTFILE = sys.argv[1]
except IndexError:
    print(helpstr)
    exit()
if INPUTFILE in ('--help', '-h'):  #TODO better argument parsing
    print(helpstr)
    exit()
RESULT = list()  # the events will be recorded in this tuple (attacker, attacked, weapon)
while True:
    try:
        handle = open(INPUTFILE)
        print('Text file is opened succesfully')
        break
    except FileNotFoundError:
        print("""
---The file could not be opened---
If you want to try again, be sure that the path is correct and enter the path again,
or press Enter to exit.""")
        INPUTFILE = input()
    if INPUTFILE == '':
        exit()

ham = handle.read()

rounds = re.split(r"(?:Map:\s(\w+))|(?:Neustart)", ham)  # to split the rounds in game
handle.close()
lines1 = list()  # the list of lines of txt file

for sean in rounds:
    if sean is None:
        rounds.remove(sean)  # the empty rounds will be deleted after split

regex = r"(.+)\skilled\s(.+)\swith\s(\w+)."  # regular expression to find the events in which a player killed another
for sean in rounds:  # for every round in game
    a = sean.split('\n')  # rounds splitted in lines
    roundkills = list()
    for line in a:  # for every line in rounds
        if line.find('killed') != -1:  # if line is a report of event in which a killing occurred
            kill = re.search(regex, line)
            y = (kill.group(1).strip(), kill.group(2).strip(),
                 kill.group(3).strip())  # here will be extracted "attacking player", "attacked player",
            # "used weapon" as tuple into y
            roundkills.append(y)  # every event-tuple will be appenden to the list

    if len(roundkills) < 10:  # if the number of events in a round less than 10
        continue  # the round will not be included
    else:
        for element in roundkills:
            RESULT.append(element)  # else will be appended to the end result list

############################################################
# RESULT is the list of all related events
# each event is recorded as a tuple (attacker, attacked, weapon)
############################################################


list_of_players = list()
for i in RESULT:

    if i[0] in list_of_players:  # attackers in events list
        pass
    else:
        list_of_players.append(i[0])
    if i[1] in list_of_players:  # attacked players in events list
        pass
    else:
        list_of_players.append(i[1])

list_of_weapons = list()

for i in RESULT:
    if i[2] in list_of_weapons:
        pass  # gec
    else:
        list_of_weapons.append(i[2])
############################################################
# the list of players and weapons created
############################################################

db = sqlite3.connect('counter-statistic.sqlite3')

d = db.cursor()

create_first_tables = '''
DROP TABLE IF EXISTS Events;

DROP TABLE IF EXISTS Players;

DROP TABLE IF EXISTS Weapons;

CREATE TABLE Events (
id INTEGER PRIMARY KEY,
attacker TEXT,
attacked TEXT,
weapon TEXT
);

CREATE TABLE Players (
id INTEGER PRIMARY KEY,
name Text
);

CREATE TABLE Weapons (
id INTEGER PRIMARY KEY,
weapon Text
);
'''
d.executescript(create_first_tables)

write_events_to_database = '''
INSERT INTO Events (attacker, attacked, weapon) VALUES (?,?,?)
'''
write_players_to_database = '''
INSERT INTO Players (name) VALUES (?)
'''

write_weapons_to_database = '''
INSERT INTO Weapons (weapon) VALUES (?)
'''
for event in RESULT:
    d.execute(write_events_to_database, event)

for player in list_of_players:
    d.execute(write_players_to_database, (player,))

for weapon in list_of_weapons:
    d.execute(write_weapons_to_database, (weapon,))

db.commit()

statics = list()  # number of attack, being attacked and rate between them for each player

for player in list_of_players:
    d.execute('''
    SELECT  COUNT (*) FROM Events WHERE attacker = ?
    ''', (player,))
    vurmasayisi = d.fetchall()[0][0]
    d.execute('''
    SELECT  COUNT (*) FROM Events WHERE attacked = ?
    ''', (player,))
    olmesayisi = d.fetchall()[0][0]
    oran = None
    if olmesayisi == 0:
        oran = vurmasayisi + 0.01
    else:
        oran = vurmasayisi / olmesayisi
    statics.append((player, vurmasayisi, olmesayisi, oran))

if '-f' in sys.argv:  # TODO: argument [-f] will be arranged
    statics = list(filter(lambda x: x[1] + x[2] > 20, statics))  # if any player has smaller number of events
    # than given, it will be filtered out

who_whom = dict()
for player in list_of_players:
    player_attacked = list()

    for other_player in list_of_players:
        d.execute('''
        SELECT  COUNT (*) FROM Events WHERE attacker= ? AND attacked= ?''', (player, other_player))
        of = d.fetchall()[0][0]
        if of:
            player_attacked.append((other_player, of))

    who_whom.update({player: tuple(player_attacked)})

weapens_of_players = dict()

for player in list_of_players:
    used_weapon = list()

    for weapon in list_of_weapons:
        d.execute('''
        SELECT  COUNT (*) FROM Events WHERE attacker= ? AND weapon= ?''', (player, weapon))
        uf = d.fetchall()[0][0]
        if uf:
            used_weapon.append((weapon, uf))

    weapens_of_players.update({player: tuple(used_weapon)})

db.close()

if os.path.exists("counter-statistic.sqlite3"):
    os.remove("counter-statistic.sqlite3")
else:
    print("Database file does not exist")

f = list()

for yeni in sorted(statics, key=lambda k: k[3], reverse=True):  # to rank the players according to score
    f.append(yeni[0])

list_of_players = f  # overwrite the actual player list with the sorted player list

html_file_handle = open('result.html', 'w')
# TODO html and css file will be organized
html_file_handle.write('''<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
    <meta charset="utf-8">
    <link rel="stylesheet" href="mainstyle.css">
    <title>CS Source Statistics</title>
</head>
<body>
<header>
<h1>CS Source Statistics</h1>
<p>
This statistics contain the time, during that the player was in any game round of CS Source and 
make the console to be written in a text file. It will calculate all killing events in console log text file, 
no matter when it has occurred.
</p>
</header>
    <main>
''')
html_file_handle.write('<div>')

print(tabulate(sorted(statics, key=lambda j: j[3], reverse=True),
               headers=['Ranking act. Rate', 'attacks to', 'attacked from', './.'], tablefmt="html",
               floatfmt=".2f"), file=html_file_handle)
print(tabulate(sorted(statics, key=lambda h: h[1], reverse=True),
               headers=['Ranking act. killings', 'attacks to', 'attacked from', './.'], tablefmt="html",
               floatfmt=".2f"), file=html_file_handle)

html_file_handle.write('</div>')
html_file_handle.write('<div>')
for player in list_of_players:
    print(tabulate(sorted(who_whom[player], key=lambda m: m[1], reverse=True),
                   headers=[player + ':', 'attacks to'], tablefmt="html"), file=html_file_handle)
html_file_handle.write('</div>')
html_file_handle.write('<div>')
for player in list_of_players:
    print(tabulate(sorted(weapens_of_players[player], key=lambda n: n[1], reverse=True),
                   headers=[player + ':', 'used the weapon'], tablefmt="html"), file=html_file_handle)
html_file_handle.write('</div>')
html_file_handle.write('''    </main>
    </body>
</html>''')
html_file_handle.close()

webbrowser.open('result.html')
print("Done.")
