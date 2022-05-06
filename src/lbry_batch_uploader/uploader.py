import os
import subprocess
import sys
import getopt

import requests
import json
import pandas as pd

from utils import get_file_name_no_ext

class Uploader:
    def __init__(self):
        pass

    def upload_thumbnail(self, files, thumbnail_params):
        """Helper function for uploading thumbnail to spee.ch"""
        req_result = requests.post(
            "https://spee.ch/api/claim/publish",
            files=files,
            data=thumbnail_params
        )  
        return self._check_response(req_result)
    
    def upload_file_to_lbry(self, file_params):
        """Helper function for uploading file to LBRY"""
        req_result = requests.post(
            "http://localhost:5279/",
            json.dumps(file_params)
        )    
        return self._check_response(req_result)

    def _check_response(self, req_result, *, error_json=None):
        """Helper function for checking response from api"""
        status = req_result.status_code
        
        if error_json is None:
            error_json = {'Error': status}

        return req_result.json() if status == 200 else error_json


def main():
    # Initiate optional command line arguments
    channelId = ""
    channelName = ""
    price = ""
    bid = "0.00001"
    extExclude = []

    # Processing command line arguments
    short_options = "i:n:p:b:t:e:"
    long_options = ["channel_id=", "channel_name=",
                    "price=", "bid=", "tags=", "exclude="]
    argument_list = sys.argv[1:]

    try:
        arguments, values = getopt.getopt(
            argument_list, short_options, long_options)
    except getopt.error as err:
        # Output error, and return with an error code
        print(str(err))
        sys.exit(2)

    for current_argument, current_value in arguments:
        if current_argument in ("-i", "--channel_id"):
            channelId = current_value
        elif current_argument in ("-n", "--channel_name"):
            channelName = current_value
        elif current_argument in ("-p", "--price"):
            price = current_value
        elif current_argument in ("-b", "--bid"):
            bid = current_value
        elif current_argument in ("-t", "--tags"):
            tags = current_value.split(",")
        elif current_argument in ("-e", "--exclude"):
            extExclude = current_value.split(",")

    print("Channel ID = {}".format(channelId), end="\n")
    print("Channel Name = {}".format(channelName), end="\n")
    print("Price = {}".format(price), end="\n")
    print("Bid = {}".format(bid), end="\n")
    print("Tags = {}".format(tags), end="\n")
    print("Excluded file extension = {}".format(extExclude), end="\n\n")

    # Scan current directory (should be the directory that contains all videos)
    path = os.getcwd()

    # Loop through the directory
    with os.scandir(path) as entries:
        for entry in entries:
            # Check whether the entry is a file or not
            if entry.is_file():
                thumbUrl = ""
                splitedName = entry.name.split(".")

                # Check the file extension to see whether it should be processed or not
                if not splitedName[-1] in extExclude:
                    # Join back by "." in case the original file name contains the character "."
                    fileNameNoExtension = '.'.join(splitedName[0:-1])

                    # Create a "clean" version of the file name, i.e. without any forbidden characters,
                    # that will be used as the name of the video attached to the URL
                    fileNameNoExtension_clean = fileNameNoExtension.replace(
                        " ", "").replace("(", "").replace(")", "").replace(
                        "?", "").replace("@", "").replace(".", "").replace(
                        "/", "").replace(":", "").replace("#", "").replace(
                        ";", "").replace("：", "").replace("，", "").replace(
                        "‧", "").replace("[", "").replace("]", "")

                    # Create a thumbnail for the video (only for mp4 or mkv files)
                    if len(splitedName) > 1 and (splitedName[-1] == "mp4" or splitedName[-1] == "mkv"):
                        print("Creating thumbnail for file: {}".format(
                            entry.name), end="\n")

                        if os.path.exists(path + "/" + fileNameNoExtension + ".png"):
                            thumbName = fileNameNoExtension + '.png'
                        elif os.path.exists(path + "/" + fileNameNoExtension + ".jpg"):
                            thumbName = fileNameNoExtension + '.jpg'
                        else:
                            thumbName = create_thumbnail(path, entry.name)

                        print("Created thumbnail for file: {}".format(
                            entry.name), end="\n\n")

                        # Prepare json to send to spee.ch
                        thumbnailParams = {
                            "name": thumbName
                        }
                        files = {
                            'file': open(path + "/" + thumbName, 'rb')
                        }

                        # Upload thumbnail to spee.ch
                        print("Uploading thumbnail to spee.ch...", end="\n")
                        uploadNotSuccessful = True
                        while uploadNotSuccessful:
                            try:
                                uploadNotSuccessful = False
                                returnJson = upload_thumbnail(
                                    files, thumbnailParams)
                                thumbUrl = returnJson["data"]["serveUrl"]
                            except KeyError:
                                uploadNotSuccessful = True
                                print(
                                    "Upload thumbnail not successful, retrying...")
                        print("Uploaded thumbnail for file: {}".format(
                            entry.name), end="\n\n")

                        # Remove the thumbnail to free up memory
                        os.remove(path + "/" + thumbName)

                    # Prepare json to send to lbrynet api
                    params = {
                        "method": "publish",
                        "params": {
                            "name": fileNameNoExtension_clean,
                            "title": fileNameNoExtension,
                            "bid": bid,
                            "file_path": path + "/" + entry.name,
                            "validate_file": False,
                            "optimize_file": False,
                            "tags": [],
                            "languages": [],
                            "locations": [],
                            "thumbnail_url": thumbUrl,
                            "funding_account_ids": [],
                            "preview": False,
                            "blocking": False
                        }
                    }
                    if(len(channelId) != 0):
                        params["params"]["channel_id"] = channelId
                    if(len(price) != 0):
                        params["params"]["fee_currency"] = "lbc"
                        params["params"]["fee_amount"] = price
                    if(len(tags) != 0):
                        params["params"]["tags"] = tags

                    # Upload video to lbrynet
                    print("Uploading video {} to LBRY".format(
                        entry.name), end="\n")
                    uploadNotSuccessful = True
                    while uploadNotSuccessful:
                        try:
                            uploadNotSuccessful = False
                            dictJson = upload_file_to_lbry(params)
                            tmp = dictJson["result"]
                        except KeyError:
                            uploadNotSuccessful = True
                            print("Upload video not successful, retrying...")

                    header = "https://odysee.com/@" + channelName + "/"
                    perm_uri = dictJson["result"]["outputs"][0]["permanent_url"].replace(
                        "lbry://", header)
                    print("Uploaded video {} to LBRY".format(
                        entry.name), end="\n\n")

                    # Save metadata to csv file
                    if os.path.exists(path + "/" + "lbry_link.csv"):
                        df_lbry = pd.read_csv(path + "/" + "lbry_link.csv")

                        df_lbry = df_lbry.append({
                            "epid_title": fileNameNoExtension,
                            "epid_backup_link": perm_uri
                        }, ignore_index=True)

                        df_lbry.to_csv(
                            path + "/" + "lbry_link.csv", index=False)
                        print("Updated lbry_link.csv for {}".format(
                            entry.name), end="\n\n")

                    else:
                        df_lbry = pd.DataFrame(
                            columns=["epid_title", "epid_backup_link"])

                        df_lbry = df_lbry.append({
                            "epid_title": fileNameNoExtension,
                            "epid_backup_link": perm_uri
                        }, ignore_index=True)

                        df_lbry.to_csv(
                            path + "/" + "lbry_link.csv", index=False)
                        print("Created and updated lbry_link.csv for {}".format(
                            entry.name), end="\n\n")

                    # Process completed for one video
                    print("Completed all processes for {}".format(
                        entry.name), end="\n\n")


if __name__ == '__main__':
    main()
