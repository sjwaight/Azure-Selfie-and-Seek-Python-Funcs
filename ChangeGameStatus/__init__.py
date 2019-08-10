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

    new_status = req.get_json().get('newstatus')

    if not new_status:
        return func.HttpResponse(
             "Please pass new status as one of 'pending', 'active' or 'winner'",
             status_code=400
        )

    new_status = new_status.lower()

    if new_status != 'pending' and new_status != 'active' and new_status != 'winner':
        return func.HttpResponse(
            "Please pass new status as one of 'pending', 'active' or 'winner'",
            status_code=400
        )

    try:

        # Read game configuration
        game_config = table_service.get_entity(os.environ.get("GAME_CONFIG_TABLENAME"), os.environ.get("GAME_CONFIG_PARTITIONKEY"), os.environ.get("GAME_CONFIG_ROWKEY"))

        # Set the new game level and write game configuration to Cosmos
        game_config['GameStatus'] = new_status

        table_service.update_entity(os.environ.get("GAME_CONFIG_TABLENAME"), game_config)

    except Exception as e:
        logging.critical(e)
        return func.HttpResponse("There was an error - please check logs", status_code=500)

    return func.HttpResponse(f"Set new game status to '{new_status}'")