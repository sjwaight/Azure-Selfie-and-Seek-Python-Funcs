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

        return func.HttpResponse(json.dumps(game_config, default=datetimeconverter), headers= {
                                                "Access-Control-Allow-Origin" : "*",
                                                "Access-Control-Allow-Credentials" : "true",
                                                "Access-Control-Allow-Methods" : "GET",
                                                "Access-Control-Allow-Headers" : "Origin, Content-Type, Accept"})
       
    except Exception as e:
        logging.critical(e)
        return func.HttpResponse("There was an error - please check logs", status_code=500, headers= {
                                                "Access-Control-Allow-Origin" : "*",
                                                "Access-Control-Allow-Credentials" : "true",
                                                "Access-Control-Allow-Methods" : "GET",
                                                "Access-Control-Allow-Headers" : "Origin, Content-Type, Accept"})