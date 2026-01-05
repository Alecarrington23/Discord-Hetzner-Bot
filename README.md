<hr>

# Discord-Hetzner-Bot
A discord bot to start a hetzner cloud server from a snapshot with the data on a separate volume

## Requirements
- python library hcloud-python
  - instal via pip install hcloud
- python library discord
  - install via pip install discord

## Usage
- get a API token for the hetzner cloud project
- get a discord app and create a bot
  - get the bot token
- create a snapshot with the app data on a separate volume
- modify the tokens.py and settings.py for your needs

## Notes
I recommend the usage of a systemd service unit for the bot itself, because currently the bot tends to stop while waiting for the server creation.
Also I recommend to make sure that the running application/game saves all data before exiting for example with an additional ExecStop line in the service unit which simply executes a sleep command.
The basic idea was a discord bot to start a gameserver when needed.
