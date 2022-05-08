import os
from parser import Parser
from uploader import Uploader
from utils import get_file_name_no_ext, get_file_name_no_ext_clean


def main():
    # Scan current directory (should be the directory that contains all videos)
    path = os.getcwd()

    # Loop through the directory
    with os.scandir(path) as entries:
        for entry in entries:
            # Check whether the entry is a file or not
            if entry.is_file():
                file_name_with_ext = entry.name
                file_ext = file_name_with_ext.split(".")[-1]

                # Check the file extension to see whether it should be processed or not
                if not (file_ext in excluded_ext):
                    file_name_no_ext = get_file_name_no_ext(file_name_with_ext)
                    file_name_no_ext_clean = get_file_name_no_ext_clean(file_name_no_ext)

                    thumbnail_name = f'{file_name_no_ext}.png'
                    thumbnail_path = os.path.join(path, f'{file_name_no_ext}.png')
                    with open(thumbnail_path, 'rb') as f:
                        thumbnail = f.read()

                    # Prepare json to send to spee.ch
                    thumbnail_params = {
                        'name': thumbnail_name,
                        'file': thumbnail,
                        }

                    # Upload thumbnail to spee.ch
                    print(f'Uploading thumbnail for {file_name_with_ext} to spee.ch...', end='\n')
                    upload_not_successful = True
                    while upload_not_successful:
                        try:
                            upload_not_successful = False
                            thumbnail_json = upload_thumbnail(thumbnail_params)
                        except KeyError:
                            upload_not_successful = True
                            print('Upload thumbnail not successful, retrying...')

                    thumbnail_url = thumbnail_json['data']['serveUrl']
                    print(f'Uploaded thumbnail for {file_name_with_ext}', end='\n')
                    print(f'thumbnail_url: {thumbnail_url}', end='\n')

                    # Prepare json to send to lbrynet api
                    file_params = {
                        'method': 'publish',
                        'params': {
                            'name': file_name_no_ext_clean,
                            'title': file_name_no_ext,
                            'bid': bid,
                            'file_path': os.path.join(path, file_name_with_ext),
                            'validate_file': False,
                            'optimize_file': False,
                            'tags': [],
                            'languages': [],
                            'locations': [],
                            'thumbnail_url': thumbnail_url,
                            'funding_account_ids': [],
                            'preview': False,
                            'blocking': False,
                        },
                    }
                    if(len(channel_id) != 0):
                        params['params']['channel_id'] = channel_id
                    if(len(price) != 0):
                        params['params']['fee_currency'] = 'lbc'
                        params['params']['fee_amount'] = price
                    if(len(tags) != 0):
                        params['params']['tags'] = tags

                    # Upload video to lbrynet
                    print(f'Uploading video {file_name_with_ext} to LBRY', end='\n')
                    upload_not_successful = True
                    while upload_not_successful:
                        try:
                            upload_not_successful = False
                            file_json = upload_file_to_lbry(params)
                        except KeyError:
                            upload_not_successful = True
                            print('Upload video not successful, retrying...')

                    header = f'https://odysee.com/@{channel_name}/'
                    file_url = file_json['result']['outputs'][0]['permanent_url']
                    file_url = file.url.replace('lbry://', header)
                    print(f'Uploaded video {file_name_with_ext} to LBRY', end='\n')
                    print(f'file_url: {file_url}', end='\n\n')


if __name__ == '__main__':
    main()
