# Azure-Selfie-and-Seek-Python-Funcs

Sample config

```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "{AzureWebJobsStorage}",
    "STORAGE_ACCOUNT": "azselfiedemo01",
    "STORAGE_KEY": "XXXXXXXXXX",
    "PLAYER_TABLENAME" : "playerlist",
    "GAME_CONFIG_TABLENAME": "gameconfig",
    "GAME_CONFIG_PARTITIONKEY": "config",
    "GAME_CONFIG_ROWKEY": "bit",
    "BIT_IMAGE_SAS_URL": "https://azselfiedemo01.blob.core.windows.net/src/bitwally.png?SAS_KEY",
    "PLAYER_IMAGE_CONTAINER": "bitplayer",
    "PLAYER_IMG_TABLENAME": "regourls",
    "PLAY_ATTEMPTS_TABLENAME": "playlogs"
  }
}
```
