# Spotify Optimiser
Checks if you skip or finish the songs that you listen to.  
If you finish it, the song will be added to a playlist, in order to create an _optimised_ playlist.

**Example**:
```
Connecting to Spotify
Do you want to use the same playlist as last time? [Y/n]n
Started session and created a new playlist
Waiting until playback starts...
Now playing: Paul de Leeuw, Humphrey Campbell - De Mallemolen - Live
   Finished, adding to playlist
Now playing: Sleeping At Last - Rainbow Connection
   Skipped, not adding
Now playing: Marco Borsato - Dromen Zijn Bedrog
   Finished, adding to playlist
Now playing: Simon & Garfunkel - Homeward Bound
   Finished, adding to playlist
Now playing: The 5th Dimension - Let The Sunshine In (Reprise) - Remastered 2000
   Skipped, not adding
```
Which results in:  
![Result](https://i.imgur.com/78J33AY.png)

# Running
Create a file called `secrets.txt` with your client ID on the first line and your client secret on the second  
These can be obtained from the [Spotify developer dashboard](https://developer.spotify.com/dashboard/applications)