import logging
import os
import json
import datetime

import azure.functions as func

# Azure Table Storage import and config
from azure.storage.blob import BlockBlobService, ContentSettings
from azure.storage import CloudStorageAccount
from azure.storage.table import TableService, Entity, EntityProperty, EdmType

table_service = TableService(os.environ.get("STORAGE_ACCOUNT"), os.environ.get("STORAGE_KEY"))

def datetimeconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def main(req: func.HttpRequest) -> func.HttpResponse:

    try:

        # Read game configuration
        game_config = table_service.get_entity(os.environ.get("GAME_CONFIG_TABLENAME"), os.environ.get("GAME_CONFIG_PARTITIONKEY"), os.environ.get("GAME_CONFIG_ROWKEY"))

        logging.info(game_config)

        #Int32 work-around (implicit assumption is Int64 in Python SDK)
        active_tier = game_config["ActiveTier"].value

        logging.info(f"Current Active Game Tier: {active_tier}")

        # find all entries that matched the hidden player for the current game play tier
        winning_entries = list(table_service.query_entities(os.environ.get("PLAY_ATTEMPTS_TABLENAME"), filter=f"gamelevel eq {active_tier} and status eq 'matched_bitly'"))

        if(len(winning_entries) > 0):

            current_winner = winning_entries[0]["PartitionKey"]
            game_config["currentwinner"] = current_winner
            game_config["winnersubmissoin"] = winning_entries[0]["submittedimage"]

            logging.info(f"Looking up image for player: {current_winner}")

            # find the winning player's submitted selfie
            winner_selfies = list(table_service.query_entities(os.environ.get("PLAYER_IMG_TABLENAME"), filter=f"PartitionKey eq {current_winner}'"))

            if(len(winner_selfies) > 0):

                game_config["winnerimgurl"] = winner_selfies[0]["imgurl"]

                # Write the game configuration change back to table storage
                table_service.update_entity(os.environ.get("GAME_CONFIG_TABLENAME"), game_config)

                # return result to client
                return func.HttpResponse(json.dumps(game_config, default=datetimeconverter))

            else:

                raise Exception("Unexpected state - winner without a selfie!")

        else:

            logging.info("No winners yet")            
            return func.HttpResponse("No winner yet for the current round", status_code=404)
                   
    except Exception as e:
        logging.critical(e)
        return func.HttpResponse("There was an error - please check logs", status_code=500)
