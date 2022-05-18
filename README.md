# LBRY Batch Uploader

![Tests](https://github.com/thk-cheng/lbry_batch_uploader/actions/workflows/workflow.yml/badge.svg)
![Coverage](https://img.shields.io/codecov/c/gh/thk-cheng/lbry_batch_uploader)
![Issues](https://img.shields.io/github/issues/thk-cheng/lbry_batch_uploader)
![Forks](https://img.shields.io/github/forks/thk-cheng/lbry_batch_uploader)
![Stars](https://img.shields.io/github/stars/thk-cheng/lbry_batch_uploader)
![License](https://img.shields.io/github/license/thk-cheng/lbry_batch_uploader)

A convenient and minimalistic batch uploader for [LBRY Desktop](https://lbry.com/get) written in Python.\
For a detail specification of the LBRY protocol, please visit https://lbry.tech/

# Work In Progress

Coming soon!

# Developing

This project uses ``black`` to format code and ``flake8`` for linting. ``pre-commit`` is also supported to ensure
these have been run. To configure your local environment please install the development dependencies and set up
the commit hooks.

```shell

pip install -r requirements_dev.txt
pip install -e .
pre-commit install

```

## License

This project is MIT licensed. For the full license, see [LICENSE](LICENSE).

<!---
## Installation

Install through pip

```shell

pip install lbry_batch_uploader

```

## Dependencies

- [requests]()

## Usage

### Unix-like (Linux/BSD/macOS)

1. Make sure LBRY Desktop is up and running. **DO NOT CLOSE THE APP WHILE THE SCRIPT IS RUNNING**.

2. Open a new terminal session and cd into the designated directory that stores the videos:

```bash

cd "path/to/directory"

```

3. Run the following command:

```bash

lbry_batch_uploader -i [ID] -n [Name] -p [price_in_lbc] -b [bid_ammount] -t [tag1,tag2,...] -e [file_ext1,file_ext2,...]

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
-->
