# Discord bot

You need an updated version of Pafy. The newest release on https://pypi.org/project/pafy/ doesn't tackle the change in dislike data on Youtube. All you need to do is make this change https://github.com/mps-youtube/pafy/commit/110bf7c01dcf57ec4e6e327e0c7907a4099d6933 in the Pafy source code or download Pafy straight from here https://github.com/mps-youtube/pafy.

bot.py - a discord music bot based on Youtube made for private use.
  A short description of functionalities:
  1) get_greetings - gets paths to audio files used as greetings, because .env files store strings exclusively.
  2) on_message - interacts with text messages. It is also used for reading numbers of songs chosen with the search command.
  3) join - tells the bot to join the voice channel of the author of the message.
  4) leave - tells the bot to leave the voice channel it is connected to.
  5) convert_timestamp_to_seconds - an auxiliary function for primitive timestamp to seconds conversion. 
  6) play - a command for playing songs or videos. It either searches the rest of the message in Youtube or plays the given url. A message is sent after the song has been added to the        queue.
  7) pause - pauses the currently played song.
  8) resume - resumes the song that is currently paused.
  9) force_skip - skips the currently played song or the currently paused song.
  10) search - searches Youtube for top NUMBER_OF_SEARCHES videos. Sends the list of found videos and waits for TIME_TO_AWAIT_SONG_CHOICE seconds for a choice. After a message with just       the number of the song is sent the bot plays the appropriate song.
  11) on_voice_state_update - handles two events. After somebody joins the voice channel the bot joins it and greets the person with a random greeting from the loaded greeting pool. The       second functionality of that function is disconnecting the bot from the voice channel after ALLOWED_INACTIVITY_PERIOD of being inactive.
