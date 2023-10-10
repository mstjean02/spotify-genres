

### --- User dependent variables to be changed ---

# User must create a spotify webapp in order to prompt authorization and
# get the following information. Instructions on how to make a spotify
# web app and get the following info can be found here:
    # https://developer.spotify.com/documentation/web-api


webapp_username      = "xfrz8237f7hnqw5su6fq5vpp0"
webapp_client_id     = "5c19f86a440f49ec9a355f779f3a07df"
webapp_client_secret = "6f8010796d4d4ce5b7cc98395d41e9f7"
webapp_redirect_uri  = "http://localhost:7777/callback"
webapp_scope         = "user-read-recently-played"






### --- Importing packages ---

import json # to read .json files
import spotipy # for access to spotify API
import pandas as pd # for data manipulation
#import time, sys
from IPython.display import clear_output

# to access the spotify files
from os import listdir


        
### --- Reading .json files into a list of dictionaries ---
# Converts a folder of .json files into a list of dictionaries (one per song)
# called data

# first make a list of filepaths to the .json files
files = ["spotify_extended/" + x for x in listdir("spotify_extended")
             if x.split("_")[0] == "endsong"]

# empty list to store dictionaries
data = []

# then iterate over the filepaths, opening them and storing them in a list
for file in files:
    clear_output(wait = True)
    print("Opening", file, sep = " ") # indicator of which file we're at
    with open(file) as json_file:
        data.extend(json.load(json_file)) # add the elements to the list data
    print("Length:", len(data), sep = " ") # check to make sure data was
                                           # updated correctly
    
df_nofeats = pd.DataFrame(data)



### --- Cleaning the resulting dataframe ---

# Renaming columns
df_nofeats = df_nofeats.rename(
    columns={"master_metadata_track_name": "track_name",
             "master_metadata_album_album_name": "album_name",
             "master_metadata_album_artist_name": "artist_name"})


# Removing podcast rows
empty_song_rows = df_nofeats.loc[df_nofeats["track_name"].isna()].index

df_nofeats = df_nofeats.drop(empty_song_rows)

# Dropping podcast columns (all NA)
df_nofeats = df_nofeats.drop(["spotify_episode_uri",
                              "episode_name",
                              "episode_show_name"], axis = 1)

# Parsing dates
df_nofeats["ts"] = pd.to_datetime(df_nofeats["ts"])

# Sorting by date and then resetting index
df_nofeats = df_nofeats.sort_values("ts", 0).reset_index(drop = True)

# This leaves us with a dataframe, one row per proper song,
# sorted chronologically from oldest to newest, and an index that reflects this.



### --- Creating a past year subset ---

# This restricts the listening data to the past year (at the time this file
# was written in order to limit API requests and program run time as a whole
# The program will work with a larger dataset, but may take longer or max out
# the allowed amount of spotify API requests.

past_year_data = df_nofeats[df_nofeats["ts"] > "2022-05-14"].reset_index(drop = True)



### --- Get access to the Spotify API ---

import spotipy.util as util

# information from the spotify web app created
username      = webapp_username
client_id     = webapp_client_id
client_secret = webapp_client_secret
redirect_uri  = webapp_redirect_uri
scope         = webapp_scope

# allows us to prompt the user(ourselves) to allow access
token = util.prompt_for_user_token(username=username, 
                                   scope=scope, 
                                   client_id=client_id,   
                                   client_secret=client_secret,     
                                   redirect_uri=redirect_uri)
      
# Function to call track artist genres from spotify        
def get_track(track_id: str, token: str):
    sp = spotipy.Spotify(auth = token)
    try:
        track_info = sp.track(track_id)
        return track_info
    except:
        print("get track error")
    
def get_artist_genres(track_id: str, token: str):
    sp = spotipy.Spotify(auth = token)
    track_info = get_track(track_id, token)
    try:
        artist_url = track_info["artists"][0]["external_urls"]["spotify"]
        artist_genres = sp.artist(artist_url)["genres"]
        return artist_genres
    except:
        return[]



### --- Make a progress bar ---

def update_progress(progress):
    bar_length = 20
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
    if progress < 0:
        progress = 0
    if progress >= 1:
        progress = 1

    block = int(round(bar_length * progress))
    clear_output(wait = True)
    text = "Progress: [{0}] {1:.1f}%".format( "#" * block + "-" * (bar_length - block),
                                             progress * 100)
    print(text)



### --- Getting list of genres (from the artist) for each song --- 
# First checks if a .json file called "artist_genres_dict.json" exists,
# if so, that gets loaded in as the unique_artists dictionary, otherwise
# the code runs the API request loop to manual fill the dictionary

json_filename = "artist_genres_dict.json"

try:
    with open(json_filename, "r") as json_file:
        unique_artists = json.load(json_file)
    print("Loaded unique_artists from", json_filename)
except FileNotFoundError:
    print(json_filename, "not found. Running API requests ...")
    
    unique_artists = {}  # used to prevent duplicate API requests

    unique_artist_counter = 0
    total_artists = len(past_year_data["artist_name"].unique())
    for i, song in past_year_data.iterrows():
        
        artist_name = song["artist_name"]
        
        if artist_name not in unique_artists and type(song["spotify_track_uri"]) == str:
            
            track_id = song["spotify_track_uri"].split(":")[2]
            track_genre = get_artist_genres(track_id, token)
            unique_artists.update({artist_name:track_genre})
            unique_artist_counter += 1
            update_progress(unique_artist_counter / total_artists)
            
    with open(json_filename, "w") as json_file:
        json.dump(unique_artists, json_file)
        
    print("Saved unique_artists to", json_filename)
    


### --- Using the unique artist genres dictionary to add a genre col ---

past_year_data["genres"] = past_year_data["artist_name"].map(unique_artists)



### --- Figuring out the most common genres

genre_list = [genre for sublist in past_year_data["genres"] for genre in sublist]

from collections import Counter

frequencies = Counter(genre_list)
most_freq_values = frequencies.most_common(30)

## The folowing dictionary is hand-classified based on my listening history
#  and genres, it will most likely need to be adapted to the user. I leave
#  mine in as a starting point and blueprint.

genres_dict = {
    "hip_hop"       :["rap", "hip hop", "trap", "pop rap", "cali rap",
                      "alternative hip hop", "dark trap", "melodic rap",
                      "uk hip hop", "plugg", "pluggnb",
                      "underground hip hop", "indie hip hop",
                      "experimental hip hop", "autralian hip hop",
                      "chicago rap", "east coast hip hop", "australian hip hop",
                      "trap queen", "canadian hip hop", "melodic drill",
                      "southern hip hop", "rage rap", "new jersey rap",
                      "french hip hop", "rap kreyol"],
    "rock"          :["rock", "classic rock", "album rock", "hard rock",
                      "modern rock", "neo-psychedelic", "emo", "alternative emo",
                      "dreamo", "rock-and-roll", "indie rock", "russian rock",
                      "russian post-punk", "classic russian rock",
                      "psychedelic rock", "alternative rock", "punk",
                      "pov: indie", "nwobhm", "soft rock"],
    "pop"           :["pop", "pop rap", "art pop", "bedroom pop", "new wave pop",
                      "belgian pop", "french indie pop", "hyperpop", "dance pop",
                      "indie pop", "europop", "classic city pop"],
    "rnb"           :["r&b", "alternative r&b", "indie r&b", "trap soul",
                      "canadian contemporary r&b"],
    "reggaeton"     :["reggaeton", "trap latino", "urbano latino",
                      "colombian pop", "latin pop"],
    "reggae"        :["reggae", "roots reggae", "reggae fusion", "uk reggae",
                      "rocksteady", "jamaican ska"],
    "country"       :["outlaw country", "country", "country dawn",
                      "country rock"],
    "soul"          :["indie soul", "neo soul", "soul", "afrofuturism",
                      "afrobeats", "afrobeat", "traditional soul"],
    "jazz"          :["jazz", "bossa nova", "uk contemporary jazz",
                      "background jazz", "latin jazz", "danish jazz",
                      "jazz trio", "indie jazz", "jazz saxophone", "jazz funk"],
    "blues"         :["blues"],
    "electro/house" :["g-house", "french indietronica", "edm", "disco",
                      "indietronica"],
    "other"         :["vintage italian soundtrack", "christmas instrumental",
                      "meme rap", "corrido"],
    "oldies"        :["adult standards", "rockabilly"]
    }

genre_dummy_lists = {
    genre: [1 if any(g in subgenres for g in gs) else 0 for gs in past_year_data["genres"]]
    for genre, subgenres in genres_dict.items()
    }

for genre, dummy_list in genre_dummy_lists.items():
    past_year_data[genre] = dummy_list


### --- refining genre dictionaries

## This shoes the most common genres in rows that are not yet classified by
#  the dictionary above. The process for refining the dictionaries is to run
#  the below code, and then add in whatever the most frequent genres are to
#  the dictionary above, and repeat until the most common unclassified genre
#  is sufficiently uncommon.

unclassified_rows = past_year_data[past_year_data[list(genres_dict.keys())].eq(0).all(axis=1)]

genre_list = [genre for sublist in unclassified_rows["genres"] for genre in sublist]

frequencies = Counter(genre_list)
most_common_genres = frequencies.most_common(50)



### --- writing the past_year_data dataframe to a .csv

past_year_data.to_csv("spotify_past_year_wgenres.csv", index = False)






    
