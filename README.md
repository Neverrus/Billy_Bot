Billy_Bot - Music Bot for Discord
====
Billy_Bot is the Discord music bot written for Python 3.8+, using the youtube_dl and spotipy libraries.
It plays requested songs from YouTube and other services into a Discord server (or multiple servers).
The bot features a permission system allowing owners to restrict commands to certain people.
As well as playing songs, Billy_Bot is capable of streaming live media into a voice channel.
The commands to control the bot are listed below. The project is deployed on the heroku platform.

## Commands guide
### .join

Joins a voice channel.

### .summon

Summons the bot to a voice channel.
If no channel was specified, it joins your channel.
### .leave

Clears the queue and leaves the voice channel.

### .play [youtube or spotify Url] or .play [song or video to search for]

Will begin playing the audio of the video/song provided.
Checks if song is on spotify and then searches.

### .volume

Sets the volume of the player.

### .now 

Displays the currently playing song.

### .pause

Pauses the currently playing song.

### .resume

Resumes a currently paused song.

### .stop

Stops playing song and clears the queue.

### .skip

Skip current song.

### .queue

Shows the player's queue.
You can optionally specify the page to show. Each page contains 10 elements.

### .shuffle

Shuffles the queue.

### .remove

Removes a song from the queue at a given index.

### .loop

Loops the currently playing song.
Invoke this command again to unloop the song.

About
-----

Author: Nikita Neverovich <neverrushs@gmail.com>

Requirements:

    Python 3.8, FFMpeg, libraries in requirements.txt