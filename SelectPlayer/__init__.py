import logging

import azure.functions as func

import random
import requests
import os
import io
from PIL import Image, ImageDraw, ImageOps
from io import BytesIO

# Azure Table Storage import and config
from azure.storage.blob import BlockBlobService, ContentSettings
from azure.storage import CloudStorageAccount
from azure.storage.table import TableService, Entity, EntityProperty, EdmType

table_service = TableService(os.environ.get("STORAGE_ACCOUNT"), os.environ.get("STORAGE_KEY"))

def main(req: func.HttpRequest) -> func.HttpResponse:

    new_game_round = req.params.get('gr')

    if not new_game_round:
        return func.HttpResponse(
             "Please pass a round number between 1 and 6 in the query string",
             status_code=400
        )

    try:

        # Read game configuration
        game_config = table_service.get_entity(os.environ.get("GAME_CONFIG_TABLENAME"), os.environ.get("GAME_CONFIG_PARTITIONKEY"), os.environ.get("GAME_CONFIG_ROWKEY"))

        # Select records for players only if they are 'confirmed' and have not previously been selected as the hidden character (byteround = 0)
        results = list(table_service.query_entities(os.environ.get("PLAYER_TABLENAME"), filter="confirmed eq true and byteround eq 0", select="PartitionKey", num_results=200))

        # total available users 
        item_count = len(results)

        # select a random integer representing position in list to select
        user_to_select = random.randint(0,item_count-1)
        # select new Bit user from list - list consists of document ID
        new_bit_user = results[user_to_select]
    
        user_doc = table_service.get_entity(os.environ.get("PLAYER_TABLENAME"), new_bit_user['PartitionKey'], game_config['ActiveEvent'])              

        # Load the static Bit character image (should have an alpha background - PNG)
        bit_img_response = requests.get(os.environ.get("BIT_IMAGE_SAS_URL"))
        bit_image = Image.open(io.BytesIO(bit_img_response.content))      

        ## Load one of the player's selfies
        images = list(table_service.query_entities(os.environ.get("PLAYER_IMG_TABLENAME"), filter="PartitionKey eq '" + new_bit_user['PartitionKey'] + "'", num_results=1))

        player_img_url = images[0]['imgurl']

        face_id = images[0]['faceid']
        rect_top =int(images[0]['faceRectTop'].value)
        rect_left = int(images[0]['faceRectLeft'].value)
        rect_width = int(images[0]['faceRectWidth'].value)
        rect_height = int(images[0]['faceRectHeight'].value)
        rect_right = rect_left + rect_width
        rect_bottom = rect_top + rect_height

        player_img_response = requests.get(player_img_url)
        player_img = Image.open(io.BytesIO(player_img_response.content))

        ## Resize static Bit image to be smaller that selfie
        resized_bit_image = ImageOps.fit(image = bit_image, size = (rect_width, rect_height))

        ## Uncomment to draw a rectangle where the face rectangle has been determined.
        ##dr = ImageDraw.Draw(playerImage)
        ##dr.rectangle((rectLeft, rectTop, rectRight, rectBottom), outline="red")

        ## Paste Bit into the player's selfie, using alpha mask from Bit image.
        player_img.paste(im = resized_bit_image, box = (rect_left, rect_top, rect_right, rect_bottom), mask = resized_bit_image)

        ## Upload merged image to Blob storage so we can serve on big screen.        
        new_img_byte_array = io.BytesIO()
        player_img.save(new_img_byte_array,'JPEG')
        block_blob_service = BlockBlobService(account_name=os.environ.get("STORAGE_ACCOUNT"), account_key=os.environ.get("STORAGE_KEY"))
        block_blob_service.create_blob_from_bytes(container_name = os.environ.get("PLAYER_IMAGE_CONTAINER"), blob_name = face_id +".jpg", blob = new_img_byte_array.getvalue(), content_settings=ContentSettings(content_type='image/jpeg'))

        bitly_user_handle = user_doc['PartitionKey']
        bitly_blob_url = 'https://' + os.environ.get("STORAGE_ACCOUNT") + '.blob.core.windows.net/' + os.environ.get("PLAYER_IMAGE_CONTAINER") + '/' + face_id + '.jpg'

        ######
        ## If images processed OK then write content to Cosmos

        ## Set the round ID to be the currently selected round.
        user_doc['byteround'].value = new_game_round
        ## Write document back to Cosmos
        table_service.update_entity(os.environ.get("PLAYER_TABLENAME"), user_doc)

        # # Set the new game level and write game configuration to Cosmos
        game_config['ActiveTier'].value = new_game_round
        game_config['BitImgUrl'] = bitly_blob_url
        game_config['BitClearUrl'] = player_img_url
        game_config['CurrentBit'] = bitly_user_handle
        game_config['CurrentPersonId'] = user_doc['personid']

        table_service.update_entity(os.environ.get("GAME_CONFIG_TABLENAME"), game_config)

    except Exception as e:
        logging.critical(e)
        return func.HttpResponse("There was an error - please check logs", status_code=500)

    return func.HttpResponse("Selected new player to find!")