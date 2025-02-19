# The Regional Manager

This is a simple FastAPI app that acts as a GitHub Copilot Extension Agent.

# Installation and Usage

This is not currently being hosted so you'll need to set this up for your own use:

1) Run this repo as a FastAPI webserver somewhere that can be publically accessed
    - `pip install uv`
    - `git clone https://github.com/dskarbrevik/the-regional-manager.git`
    - `cd the-regional-manager`
    - `uv install`
    - `uv run fastapi dev api.py`
    Note: if you are running this on a local machine, consider [ngrok](https://ngrok.com/) to make it publically available for GitHub.

2) Create a GitHub app

2) Create a GitHub Application

3) Install the GitHub Application on your GitHub account

4) Open a GitHub Copilot chat session and @the-name-of-your-ext