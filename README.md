# LBRY Batch Uploader

A convenient and minimalistic batch uploader for [LBRY Desktop](https://lbry.com/get) written in Python.\
For a detail specification of the LBRY protocol, please visit https://lbry.tech/ \

## Installation

Install through pip

```bash
pip install lbry-batch-uploader
```

## Dependencies

- [ffmpeg](https://github.com/FFmpeg/FFmpeg)

## Usage

### Unix-like (Linux/BSD/macOS)

1. Make sure LBRY Desktop is up and running. **DO NOT CLOSE THE APP WHILE THE SCRIPT IS RUNNING**.

2. Open a new terminal session and cd into the designated directory that stores the videos:
```bash
cd "path/to/directory"
```

3. Run the following command:
```bash
lbry-batch-uploader -i [ID] -n [Name] -p [price_in_lbc] -b [bid_ammount] -t [tag1,tag2,...] -e [file_ext1,file_ext2,...]
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

## License

This project is MIT licensed. For the full license, see [LICENSE](LICENSE).
