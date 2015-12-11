import Tkinter
import tkMessageBox
import unicodedata
from Tkinter import *

import spotipy
import tweepy

import spotify_login


# get the twitter authenticated
def get_twitter():
    # Spotify Premium Account Needed here
    # luckily, these are not my credentials ;)
    access_token = "92798976-4NYAIarwv3CIh7XsppuLEycvypwpRsRQxXwUXpZ9g"
    access_token_secret = "VnwZ1t3oiZtZxR29vuLB9ODULQQGvr99YfLd5zZXf3j59"
    consumer_key = "dFaMS8tY7G5OdPl6dXJnGlL09"
    consumer_secret = "ivTJbbwpXo8YZv2TBqzWRGNxaaYldIr5bM73nvkha2qdKC1p7S"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)


# uses tweepy api to get tweets of a user, extract junks (urls, utf-8, ...)
def get_tweets(client):
    delete_list = ['"', '\'', '[', ']', 'RT ', '!', 'via', '#', '$', '%', '&', '*', '/', '|', ',', '.', '<', '>', '}',
                   ';', '=', '+', ')', '(', ')', '{', '~', '`', '_', '?']

    if playListEntry.get() != "":  # check the user has not forgotten to type in playlist name
        try:
            tweets = []
            user = client.get_user(screen_name=(userNameEntry.get()))
            for tweet in user.timeline():
                for word in tweet.text.split():
                    if re.search(r'\S*http\S*', word) or re.search(r'\S*@\S*', word):
                        tweet.text = tweet.text.replace(word, "")
                for word in delete_list:
                    tweet.text = tweet.text.replace(word, "")
                text = unicodedata.normalize('NFKD', tweet.text).encode('ascii', 'ignore')
                tweets.append(" ".join(text.split()))
            return tweets
        except tweepy.TweepError:  # pop up error message in case of invalid user, or no internet connection
            message("Error", "Cannot reach the user")
    else:
        message("Error", "Give your play list a name")


# uses tweepy api to get accounts followed by the user
# that method has limitation for account with over 100 followers (Twitter limits GET up to 100)
def followed_accounts(client):
    ids = []
    pages = tweepy.Cursor(client.friends_ids, screen_name=(userNameEntry.get())).pages()
    while len(ids) < 100:
        try:
            ids.extend(pages.next())
        except:
            break
    if ids:
        return [user.screen_name for user in client.lookup_users(user_ids=ids)]
    else:
        return []


# build profile and create playlist
def create_playlist():
    client = get_twitter()
    tweets = get_tweets(client)  # get authenticated on spotify, after getting the tweets
    if tweets:
        sp = spotipy.Spotify(spotify_login.prompt('playlist-modify-private', '7e6e5c11bb82461c9b12578a301e1cec',
                                                  'http://127.0.0.1:43019/redirect'))
        if sp:
            all_tracks = {}  # dictionary to collect all our tracks
            music_title = []  # list to collect music titles in building profile
            artist_name = []  # list to collect artist names in building profile
            artists = []  # list to collect suspected music titles in building profile(before filtering it with the spotify music database)
            musics = []  # list to collect suspected artist names in building profile(before filtering it with the spotify music database)

            # Here we have googled some research papers on how to extract music related tweets,
            # Extracting Listening Behaviour from Twitter by Eva Zangerle, Martin Pichl, Wolfgang Gassler, Gusnther Specht,
            # University of Innsbruck, Austria

            # Extract tweets which might be related to music (using delimitants '-', ':' and 'by'),
            # and split those tweets to get a list of suspected artist names and music titles
            for tweet in tweets:
                for word in ['-', ':', 'by']:
                    split = []
                    if word in tweet:
                        split.append(tweet.split(word))
                    for line in split:
                        artists.append(line[0])
                        musics.append(line[1])

            for tweet in tweets:
                split = []
                if "by" in tweet:
                    split.append(tweet.split("by"))
                for line in split:
                    artists.append(line[1])
                    musics.append(line[0])

            # Append all followed accounts to the list of suspected artist names
            artists.extend(followed_accounts(client))

            # Search for an artist match in the spotify music database
            for artist in artists:
                results = sp.search(q='artist:' + artist, type='artist')
                items = results['artists']['items']

                # if the search returns any much, take the 1st artist in the list, and take top 5 tracks
                if len(items) > 0:
                    artist = items[0]  # take the first in the list of matched artist names
                    tracks = sp.artist_top_tracks('spotify:artist:' + artist['id'])
                    for track in tracks['tracks'][:3]:
                        if track['name'] not in all_tracks:
                            all_tracks[track['name']] = track['id']  # append the track id's in to the all_tracks dict
                    if artist['name'] not in artist_name:  # make a profile (list of artist names)
                        artist_name.append(artist['name'])

            # Search for a track name match in the spotify music database
            for music in musics:
                tracks = sp.search(music + ' ', 1)
                items = tracks['tracks']
                for track in items['items']:
                    if track['name'] not in all_tracks:
                        all_tracks[track['name']] = track[
                            'id']  # make sure not to collect similar tracks and append track ID
                        music_title.append(track['name'])  # make a profile (list of music titles)

            print "-----------: " + userNameEntry.get() + " :-----------"
            print "Tweets"
            for tweet in tweets:
                print "  ", tweet
            print "Artists"
            for artist in artists:
                print "  ", artist
            print "Music Titles"
            for music in musics:
                print "  ", music
            print "Artists"
            for artists in artist_name:
                print "  ", artists
            print "Music Titles"
            for music in music_title:
                print "  ", music

            # Create a playlist and add all the track in the all_tracks dict to the playlist
            try:  # some times it takes too long for spotify to load tracks and it raise an exception error .. so we need to ask the user to try again
                user = sp.me()['id']
                playlist = playListEntry.get()
                playListEntry.delete(0, END)
                userNameEntry.delete(0, END)
                new_playlist = sp.user_playlist_create(user, playlist, False)
                sp.user_playlist_add_tracks(user, new_playlist['id'], all_tracks.values())
                message("Congrats!!", "Playlist \"" + playlist + "\" created!!, " + str(len(all_tracks)) + " tracks")
            except:
                message("Please Try Again", "Looks like its taking too long for spotify to load your tracks")
        else:
            message("Error", "No can login to Spotify")


def message(title, content):
    tkMessageBox.showinfo(title, content)


def quit():
    app.destroy()


def enter(event):
    create_playlist()


# GUI
app = Tk()
app.title("Twitter 2 Spotify")

panel1 = Tkinter.Label(app, text="Name your playlist:", bd=0, fg="#81b71a", font=("Times", 16))
panel1.pack()
panel1.place(x=28, y=72)

panel2 = Tkinter.Label(app, text="Twitter username:", bd=0, fg="#81b71a", font=("Times", 16))
panel2.pack()
panel2.place(x=41, y=22)

userNameEntry = Entry(app, width=27, font=("Times", 16), fg="#81b71a")
userNameEntry.pack()
userNameEntry.place(x=225, y=22)
userNameEntry.focus_set()

playListEntry = Entry(app, width=27, font=("Times", 16), fg="#81b71a")
playListEntry.pack()
playListEntry.place(x=225, y=72)

enterButton = Tkinter.Button(app, text="Enter", width=7, bg="#81b71a", fg="#ffffff", command=create_playlist,
                             font=("Times", 16))
enterButton.pack()
enterButton.place(x=30, y=130)

quitButton = Tkinter.Button(app, text="Quit", width=6, bg="#81b71a", fg="#ffffff", command=quit, font=("Times", 16))
quitButton.pack()
quitButton.place(x=420, y=130)

app.geometry('550x180+490+122')
app.resizable(width=FALSE, height=FALSE)
app.bind('<Return>', enter)
app.mainloop()
