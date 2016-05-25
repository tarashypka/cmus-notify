#! /usr/bin/python

# User-specific settings
APIKEY    = "apikey"
SECRETKEY = "secretkey"
user = "username"
playlist = "/home/" + user + "/Music/Playlists/favorites.pls"
socket = "/home/" + user + "/.cmus/socket"
seskeyp = "/home/" + user + "/tmp/cmus/seskey"
timeout = 10

URL = "http://ws.audioscrobbler.com/2.0/"
AUTHURL = "http://www.last.fm/api/auth/"

from subprocess import call, check_output
from sys import exit
from gtk import main, main_quit
from gobject import timeout_add
from os import path, listdir
from re import match, compile

import urllib2
import json
import hashlib
import requests
import pynotify
import webbrowser
import time

cmus = ["cmus-remote", "-C"]

def cmuscall(arg):
    if call(cmus + ["status"]) != 0:
        exit(1)
    return check_output(cmus + [arg])

def grep(lines, patt):
    for line in lines.splitlines():
        if patt in line:
            return line

def gettoken():
    tokenrequrl = URL \
                + "?method=auth.getToken" \
                + "&api_key=" + APIKEY \
                + "&format=json"
    response = urllib2.urlopen(tokenrequrl)
    jsondata = json.load(response)
    token = jsondata["token"]

    # Request authorization from the user
    authurl = AUTHURL \
            + "?api_key=" + APIKEY \
            + "&token=" + token
    webbrowser.open_new_tab(authurl)
    time.sleep(30)

    return token

def getapisig(token):
    sig = "api_key" + APIKEY \
        + "method" + "auth.getSession" \
        + "token" + token \
        + SECRETKEY
    h = hashlib.new('md5')
    h.update(sig)
    return h.hexdigest()

def getseskey():
    if path.isfile(seskeyp):
        print "Already have a session key"
        seskeyf = open(seskeyp, 'r')
        seskey = seskeyf.read()
    else:
        print "Generate new session key"
        token = gettoken()
        apisig = getapisig(token)
        sesrequrl = URL \
                  + "?method=auth.getSession" \
                  + "&api_key=" + APIKEY \
                  + "&api_sig=" + apisig \
                  + "&token=" + token \
                  + "&format=json"
        response = urllib2.urlopen(sesrequrl)
        jsondata = json.load(response)
        seskey = jsondata["session"]["key"]
        seskeyf = open(seskeyp, 'w')
        seskeyf.write(seskey)
    seskeyf.close()
    return seskey

def exists(favorite):
    favorites = [ line.strip('\n') for line in open(playlist) ]
    if favorite in favorites:
        return True
    return False

def favorite(n, action):
    assert action == "favorite"
    if not n.show():
        exit(1)
    fav = grep(cmuscall("status"), "file ")[5:]
    if exists(fav):
        return
    cmuscall("view 3")
    cmuscall("load " + playlist)
    cmuscall("view 1")
    cmuscall("win-sel-cur")
    cmuscall("win-add-p")
    cmuscall("view 3")
    cmuscall("save " + playlist)

def sendlove(n, action):
    assert action == "sendlove"
    if not n.show():
	exit(1)
    seskey = getseskey()
    cmusresp = cmuscall("status")
    artist = grep(cmusresp, "tag artist ")[11:]
    title = grep(cmusresp, "tag title ")[10:]
    data = { "api_key": APIKEY, \
             "artist": artist, \
             "method": "track.love", \
             "sk": seskey, \
             "track": title }
    res = requests.post(URL, data)

if not pynotify.init("Cmus Notification"):
    n.close()
    exit(1)

if __name__ == '__main__':
    cmusresp = cmuscall("status")
    title = grep(cmusresp, "tag title ")[10:]
    album = grep(cmusresp, "tag album ")[10:]
    artist = grep(cmusresp, "tag artist ")[11:]
    file_path = grep(cmusresp, "file ")[5:]
    file_path = file_path.rsplit('/', 1)[0]
    icon_path = file_path + "/"
    for file in listdir(file_path):
        if compile(".*\.jpe?g").match(file):
            icon_path += file
    icon_uri = "file://" + icon_path
    n = pynotify.Notification(title, artist + "\n" + album, icon_uri)
    n.add_action("favorite", "Add to favorites", favorite)
    n.add_action("sendlove", "Send Last.fm love", sendlove)
    n.set_timeout(timeout * 1000)

    if not n.show():
        exit(1)

    timeout_add(2 * timeout * 1000, main_quit)
    main()
