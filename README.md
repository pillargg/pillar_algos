# Background

Pillar is creating an innovative way to automatically select and splice clips from Twitch videos for streamers. This repo is focusing on the algorithm aspect. Two main algorithms are being tested.

1. Find the best moments in clips based on where the most users participated. Most is defined as the ratio of unique users during a 2 min section to unique users for the entire session.
1. Find the best moments in clips based on when rate of messages per user peaked. This involves answering the question "at which 2 min segment do the most users send the most messages?". If users X, Y, and Z all send 60% of their messages at timestamp range delta, then that timestamp might qualify as a "best moment"

# How To

Install the requirements `pip install -r requirements.txt`, then open the pillars.ipynb jupyter notebook. Algorithm 1 and 2 are labeled.