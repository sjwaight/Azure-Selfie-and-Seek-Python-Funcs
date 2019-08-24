# Azure Selfie and Seek Python Functions

This repository contains Azure Functions written in Python that can be used as an alternative to the Python Flask Admin Web application used in the Azure Self-and-Seek game.

The Functions work as follows:

- ActiveGame, GameStatus and WinnerGame: these are all used by the booth SPA to determine what data to display on screen. These require CORS to work.
- ChangeGameStatus, SelectPlayer and SelectWinner: these replace screens in the admin web application. See below for how you can use them.

## Using the admin APIs:

### ChangeGameStatus

This API determines which screen to display on the booth. 

POST https://YOUR_HOST.azurewebsites.net/api/changegamestatus?code=YOUR_FUNCTION_KEY

Set body to application/json and send:

```json
{
  "newstatus": "*status*"
}
```

*status* can be one of: "pending", "active" and "winner". You can switch between any value.

### SelectPlayer

Use this API to select a player at random to be the "hidden" player everyone else has to find.

GET https://YOUR_HOST.azurewebsites.net/api/selectplayer?code=YOUR_FUNCTION_KEY&gr=*ROUND_NUMBER*

Set *ROUND_NUMBER* to any integer value greater than zero. Don't re-use integer values you've already used.

### SelectWinner

Display the list of players that have successfully found the hidden player. The first person in the list is your winner!

GET https://YOUR_HOST.azurewebsites.net/api/selectwinner?code=YOUR_FUNCTION_KEY&gr=*ROUND_NUMBER*

Set *ROUND_NUMBER* to the integer value you used when using SelectPlayer.

## Deployment and Configuration

Sample Functions config

```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "{AzureWebJobsStorage}",
    "STORAGE_ACCOUNT": "YOUR_STORAGE_ACCOUNT",
    "STORAGE_KEY": "XXXXXXXXXX",
    "PLAYER_TABLENAME" : "playerlist",
    "GAME_CONFIG_TABLENAME": "gameconfig",
    "GAME_CONFIG_PARTITIONKEY": "config",
    "GAME_CONFIG_ROWKEY": "bit",
    "BIT_IMAGE_SAS_URL": "https://YOUR_STORAGE_ACCOUNT.blob.core.windows.net/src/bitwally.png?SAS_KEY",
    "PLAYER_IMAGE_CONTAINER": "bitplayer",
    "PLAYER_IMG_TABLENAME": "regourls",
    "PLAY_ATTEMPTS_TABLENAME": "playlogs"
  }
}
```

Deploy to your target Function app using this command:

```bash
func azure functionapp publish YOUR_HOST --build remote
```