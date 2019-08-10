import logging
import os
import json

import azure.functions as func

# Azure Table Storage import and config
from azure.storage.blob import BlockBlobService, ContentSettings
from azure.storage import CloudStorageAccount
from azure.storage.table import TableService, Entity, EntityProperty, EdmType

table_service = TableService(os.environ.get("STORAGE_ACCOUNT"), os.environ.get("STORAGE_KEY"))

def main(req: func.HttpRequest) -> func.HttpResponse:

    game_round = req.params.get('gr')

    if not game_round:
        return func.HttpResponse(
             "Please pass a round number between 1 and 6 in the query string",
             status_code=400
        )

    try:
        if(game_round != 0):

            winningEntries = list(table_service.query_entities(os.environ.get("PLAY_ATTEMPTS_TABLENAME"), filter="status eq 'matched_bitly' and gamelevel eq " + str(game_round), select = "PartitionKey, postbody", num_results=1))

            return func.HttpResponse(json.dumps(winningEntries))
       
    except Exception as e:
        logging.critical(e)
        return func.HttpResponse("There was an error - please check logs", status_code=500)