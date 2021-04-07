# Background

[Access me](https://github.com/pomkos/twitch_chat_analysis/blob/main/pillar.ipynb)

__Description__:

Pillar is creating an innovative way to automatically select and splice clips from Twitch videos for streamers. This repo is focusing on the algorithm aspect. Three main algorithms are being tested.

1. Find the best moments in clips based on where the most users participated. Most is defined as the *ratio of unique users* during a 2 min section to unique users for the entire session.
1. Find the best moments in clips based on when rate of messages per user peaked. This involves answering the question "at which 2 min segment do the most users send the most messages?". If users X, Y, and Z all send 60% of their messages at timestamp range delta, then that timestamp might qualify as a "best moment"
1. Weigh each user by their chat rate, account age, etc. Heavier users predicted to chat more often at "best moment" timestamps

__Datasets used__:
1. Preliminary data `prelim_df`: 545 rows representing one 3 hour 35 minute 26 second twitch stream chat of [Hearthstone by LiiHS](https://www.twitch.tv/videos/963184458)
    * Used to create initial json import and resulting df clean/merge function `organize_twitch_chat`
2. Big data `big_df`: 2409 rows representing one 7 hour 37 minute, 0 second twitch stream chat of [Hearthstone by LiiHS](https://www.twitch.tv/videos/955629991)
    * Used to create all algorithms
