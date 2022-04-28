# lbryscripts

lbryscripts is a minimal python script that runs in command line and aims at assisting users in mass uploading videos to [LBRY](https://lbry.com/).\
Please note that this is a forked repository, so any changes being made to the script would be mostly based on personal needs.\
Full credit goes to [@paju1986](https://github.com/paju1986/lbryscripts) for developing the original script.

## Prerequisite
[ffmpeg](https://github.com/FFmpeg/FFmpeg) is required for thumbnail (.png) creation.\
macOS users can install it with [Homebrew](https://brew.sh/):
```bash
brew install ffmpeg
```

## Usage (for macOS)
1. First, make sure that the LBRY Desktop app is up and running. DO NOT CLOSE THE APP WHILE THE SCRIPT IS RUNNING.

2. Then, open a new terminal window and cd into the designated directory that stores the videos:
```bash
cd "path/to/directory"
```

3. Finally, run the script with the following command:
```bash
python "path/to/script" -i [ID] -n [Name] -p [price_in_lbc] -b [bid_ammount] -t [tag1,tag2,...] -e [file_ext1,file_ext2,...]
```

## Options
```
-i, --channel_id ID                          Specify the channel's claim ID, used for determining the upload location 
-n, --channel_name Name                      Specify the channel name, used for saving the uploaded video link
-p, --price PRICE                            Set the price (in LBC) for all videos, default is free
-b, --bid BID                                Set the bid (in LBC) for all videos, default is 0.00001
-t, --tags tag1,tag2,...                     Specify the tags for all videos, which are separated by ","
-e, --exclude file_ext1, file_ext2,...       Indicate which types of file should be excluded from upload (e.g. jpg,txt,...)
```

## On-going Development
- Detect and fix special characters in file names that LBRY doesn't allow (e.g. "@", "/", ":")
- Custom description for each video
- Connection with existing database