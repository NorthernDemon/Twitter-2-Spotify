def get_tweets():
    """uses tweepy (twitter streaming API library for python) to get tweets of a user,
        -pass consumer key, consumer secret, access_token and access_token_secret to access the Twitter API using tweepy with OAuth.
        -initiate the API instance
        -get tweets for a user specified by the required screen_name parameter
        -remove junks(urls, utf-8, and other unwanted characters)
        -pop up error message in case of invalid user, or if user is not connected
        -return tweets
    """


def followed_acc():
    """uses tweepy (twitter streaming API library for python) to get tweets of a user,
        -pass consumer key, consumer secret, access_token and access_token_secret to access the Twitter API using tweepy with OAuth.
        -initiate the API instance
        -get ids of followed accounts by a user specified in the required screen_name parameter
        -get user screen names for each id
        -return accounts the user is following
    """


def create_playlist():
    """Build profile and create playlist using spotipy (Spotify API library for python)
        -get the fine-tuned tweets from the getTweets function
        -request user permission on spotify to modify private playlist and get access token
        -initiate a spotify session
        -identify tweets related to music and get suspected artist names and music titles out of it (using delimitants '-', ':' and 'by')
        -get the accounts followed by the user and append it on  the suspected artist names list
        -use the spotify music database to verify the artist name and music title lists
        -if the artist name search returns any much, take the 1st artist in the list, and top 3 tracks with it
        -if the music title search returns any much, take the 1st track in the list
        -collect all the track ids in list
        -create a playlist and post all the tracks in to it
        -prompt the user to try again in case of error (spotify api limit exceed)
        -print list of tweets, suspected artist names & music titles, artist names & music times after verified by spotify music database (Just for demo .. to show the work flow
    """


def message(title, content):
    """
        -pop up messages(given header and message content)
        :param title: message title
        :param content: message content
    """


def quit():
    """
        -quit and close the app
    """


def enter(event):
    """
        -accept keyboard input from user (Enter)
    """
