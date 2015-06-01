from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from Tkinter import *
import tweepy 
import re
import string
import pickle
import requests
import sys
import unicodedata
import spotipy
import spotify_login
import Tkinter
import tkMessageBox

access_token = "92798976-4NYAIarwv3CIh7XsppuLEycvypwpRsRQxXwUXpZ9g"
access_token_secret = "VnwZ1t3oiZtZxR29vuLB9ODULQQGvr99YfLd5zZXf3j59"
consumer_key = "dFaMS8tY7G5OdPl6dXJnGlL09"
consumer_secret = "ivTJbbwpXo8YZv2TBqzWRGNxaaYldIr5bM73nvkha2qdKC1p7S"

def getTweets(): # uses tweepy api to get tweets of a user, extract junks (urls, utf-8, ...)
	delete_list = ['"', '\'', '[', ']', 'RT ', '!', 'via', '#','$', '%', '&', '*','/', '|', ',', '.', '<', '>', '}', ';','=', '+', ')', '(', ')', '{', '~', '`', '_', '?']

		
	twitterName = userNameEntry.get()
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	client = tweepy.API(auth)
	if not playListEntry.get() == "": # check the user has not forgotten to type in playlist name 
		try:
			user = client.get_user(screen_name=twitterName)
			if user:
				tweets = []
				for tweet in user.timeline():
					for word in tweet.text.split():
       						if re.search(r'\S*http\S*', word) or re.search(r'\S*@\S*', word):
							tweet.text = tweet.text.replace(word, "")
					for word in delete_list:
						tweet.text = tweet.text.replace(word, "")
					text = unicodedata.normalize('NFKD', tweet.text).encode('ascii','ignore')	
					tweets.append(" ".join(text.split()))
				return tweets
		except tweepy.TweepError:#pop up error message in case of invalid user, or no internet connection
	   		message("Error", "cant reach user")
	else:
		message("Error","Give your play list a name")

def followedAcc():# uses tweepy api to get accounts followed by the user
	twitterName = userNameEntry.get()
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	client = tweepy.API(auth)
	ids = []
	following = []
	for page in tweepy.Cursor(client.friends_ids, screen_name=twitterName).pages():
    		ids.extend(page)
	following = [user.screen_name for user in client.lookup_users(user_ids=ids)]
	return following

def creatPlayList():# Build profile and create playlist
	tweets = getTweets()# get authenticated on spotify, after getting the tweets 
	if tweets:
		token = spotify_login.prompt('playlist-modify-private', '7e6e5c11bb82461c9b12578a301e1cec', 'http://127.0.0.1:43019/redirect')
		if token:
			sp = spotipy.Spotify(token) 				
		allTracks = {} # dictionary to collect all our tracks
		musicTitle = [] #list to collect music titles in building profile
		artistName = [] #list to collect artist names in building profile
		artists = [] #list to collect suspected music titles in building profile(before filtering it with the spotify music database)
		musics = [] #list to collect suspected artist names in building profile(before filtering it with the spotify music database)
		
		# Here we have googled some research papers on how to extract music related tweets,
		# Extracting Listening Behaviour from Twitter by Eva Zangerle, Martin Pichl, Wolfgang Gassler, Gusnther Specht,
		# University of Innsbruck, Austria
		
		# Extract tweets which might be related to music (using delimitants '-', ':' and 'by'), 
		# and split those tweets to get a list of suspected artist names and music titles
		splitlist =['-',':','by']
		for tweet in tweets:
			for word in splitlist:
				splitted = []
				if word in tweet: 
					splitted.append(tweet.split(word))
				for line in splitted:
					artists.append(line[0])
					musics.append(line[1])
	
		for tweet in tweets:
			splitted = []
			if "by" in tweet: 
				splitted.append(tweet.split("by"))
			for line in splitted:
				artists.append(line[1])
				musics.append(line[0])
		
		# Append all followed accounts to the list of suspected artist names
		following = followedAcc()
		artists.extend(following)	
		
		# Search for an artist match in the spotify music database
		for artist in artists:
			results = sp.search(q='artist:' + artist, type='artist')
			items = results['artists']['items']

			#if the search returns any much, take the 1st artist in the list, and take top 5 tracks
			if len(items) > 0:
   				artist = items[0] # take the first in the list of matched artist names
				name = 'spotify:artist:' + artist['id']
				#print artist['name']
				tracks = sp.artist_top_tracks(name)
				for track in tracks['tracks'][:3]:
					#print "  ",track['name']
					if (track['name'] not in allTracks):
    						allTracks[track['name']] = track['id'] #append the track id's in to the allTracks dict
				if artist['name'] not in artistName:# make a profile (list of artist names)
					artistName.append(artist['name'])

    		# Search for a track name match in the spotify music database
		for music in musics:
			tracks = sp.search(music + ' ', 1) 
			items = tracks['tracks']
			for track in items['items']:
				if (track['name'] not in allTracks):	
					allTracks[track['name']] = track['id']#make sure not to collect similar tracks and append track ID
			 		musicTitle.append(track['name']) # make a profile (list of music titles)	

		# Uncomment the following to print tweets, profile of artist name and music titles,
		# and the suspected profile (the profile before verified by the spotify music database)	
				
		'''print "Tweets"
		for tweet in tweets:
			print "  ",tweet
	
		print "Artists"
		for artist in artists:
			print "  ", artist
		print "Music Titles"
		for music in musics:
			print "  ", music
		print
		
		print "Artists"
		for artists in artistName:
			print "  ", artists
		print "Music Titles"
		for music in musicTitle:
			print "  ", music'''
		
		#Create a playlist and add all the track in the allTracks dict to the playlist
		try:# some times it takes too long for spotify to load tracks and it raise an exception error .. so we need to ask the user to try again 
			user = sp.me()['id']
			playList = playListEntry.get()
			playListEntry.delete(0,END)
			userNameEntry.delete(0,END)
			new_playlist = sp.user_playlist_create(user, playList, False)
			sp.user_playlist_add_tracks(user, new_playlist['id'], allTracks.values())
			message("Congrats!!", "Playlist \"" + playList + "\" created!!, " + str(len(allTracks)) + " tracks")
		except:
			message("Please Try Again","Looks like its taking too long for spotify to load your tracks")
			
def message(title, content):
	tkMessageBox.showinfo(title, content)
	
def quit():
	app.destroy()

def enter(event):
	creatPlayList()
# GUI
app = Tk()
app.title("twify")

panel1 = Tkinter.Label(app,text = "Name your playlist:", bd =0, fg ="#81b71a", font=("Times", 16))
panel1.pack()
panel1.place (x=28,y = 72)

panel2 = Tkinter.Label(app,text = "Twitter username:", bd =0, fg ="#81b71a", font=("Times", 16))
panel2.pack()
panel2.place (x= 41,y = 22)

userNameEntry = Entry(app, width = 27, font=("Times", 16), fg ="#81b71a")
userNameEntry.pack()
userNameEntry.place (x=225, y=22)
userNameEntry.focus_set()

playListEntry = Entry(app, width = 27, font=("Times", 16), fg ="#81b71a")
playListEntry.pack()
playListEntry.place (x=225, y= 72)

enterButton = Tkinter.Button(app, text ="Enter", width = 7, bg = "#81b71a" , fg = "#ffffff", command =creatPlayList, font=("Times", 16))
enterButton.pack()
enterButton.place(x=30, y=130)

quitButton = Tkinter.Button(app, text ="Quit", width = 6, bg = "#81b71a" , fg = "#ffffff", command = quit, font=("Times", 16))
quitButton.pack()
quitButton.place(x=420, y=130)

app.geometry('550x180+490+122')
#app.configure(background='white')
app.resizable(width=FALSE, height=FALSE)
app.bind('<Return>', enter)
app.mainloop()


