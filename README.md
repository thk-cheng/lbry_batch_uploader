# LBRY Batch Uploader

![Tests](https://github.com/thk-cheng/lbry_batch_uploader/actions/workflows/workflow.yml/badge.svg)
![PreCommit](https://github.com/thk-cheng/lbry_batch_uploader/actions/workflows/pre-commit.yml/badge.svg)
![Coverage](https://img.shields.io/codecov/c/gh/thk-cheng/lbry_batch_uploader)
![PyVersions](https://img.shields.io/pypi/pyversions/lbry-batch-uploader)
![Wheel](https://img.shields.io/pypi/wheel/lbry-batch-uploader)
![PyPIVersion](https://img.shields.io/pypi/v/lbry-batch-uploader)
![License](https://img.shields.io/github/license/thk-cheng/lbry_batch_uploader)

A convenient and minimalistic batch uploader for [LBRY Desktop](https://lbry.com/get) written in Python.\
For a detail specification of the LBRY protocol, please visit https://lbry.tech/

If you have any questions/suggestions, please open an [issue](https://github.com/thk-cheng/lbry_batch_uploader/issues). I am more than happy to discuss with you!\
There is also a list of [known issues](#known-issues) below, which contains issues that are directly caused by how LBRY processes transactions.
Since this project relies on the lbrynet api, these are all unavoidable and I could not do much on my part.

If you find any mistakes/room for improvement, please open a [pull request](https://github.com/thk-cheng/lbry_batch_uploader/pulls). I will respond asap!

## Installation

Install through pip, preferably inside a virtual environment, from the terminal:

```shell
python -m pip install --upgrade pip
pip install lbry_batch_uploader
```

n.b. If you are unfamiliar with creating virtual environment, please refer to the documentation of either [venv](https://docs.python.org/3/library/venv.html) or [virtualenv](https://virtualenv.pypa.io/en/latest/).

## Dependencies

- python>=3.8.13
- [requests](https://docs.python-requests.org/en/latest/)>=2.0.0

## Usage

### Unix-like (Linux/BSD/macOS)

1. Open the LBRY Desktop and make sure it stays open for the whole uploading process
2. Inside an environment that has installed this package, run the following command from the terminal:
```shell
python -m lbry_batch_uploader \
    file_directory \
    channel_name \
    --port PORT \
    --bid BID \
    --fee-amount FEE_AMOUNT \
    --tags TAG1 TAG2 ... \
    --languages L1 L2 ... \
    --license LICENSE \
    --license-url LICENSE_URL
```

n.b. The meaning and usage of each argument is documented in the [following section](#arguments).

#### Descriptions and Thumbnails

The uploader will automatically scan for files that have the same name with the one currently being uploaded,
but with a correct file extension of being either a description or a thumbnail.

E.g. if you have the following directory structure:

```
|
|- testing_videos
|   |
|   |- sample_video.mp4
|   |
|   |- sample_video.txt
|   |
|   |- sample_video.png
|   |
|   |- ...
|   |
```

Then the uploader would automatically scan for `testing_videos` and pick up `sample_video.txt`, `sample_video.png` as the description and thumbnail for `sample_video.mp4` respectively.

The currently supported file extensions are as follows:

```
description    .txt, .description
thumbnail      .gif, .jpg, .png
```

### Windows

This package currently does not have ``cygwin``, ``win32``, ``win64`` support. Please accept my sincere apology :(

## Arguments

### Positional

```
file_directory             The absolute path of the directory that contains all the files to be uploaded

channel_name               The name of the publisher channel (with the @)
```

### Optional

```
-h, --help                 Show the help message and exit

--port PORT                The port that lbrynet listens to, default to 5279 if not specified.

--bid BID                  The amount to back the claim, default to 0.0001 if not specified.

--fee-amount FEE_AMOUNT    The content download fee in LBC, default to 0 if not specified (i.e. free).

--tags TAGS [TAGS ...]     The content tags of the claims, default to [] if not specified.

--languages L [L ...]      The languages of the claims in RFC5646 format, default to ["en"] if not specified.
                           More than one could be specified. Please refer to RFC5646 for the complete list.

--license LICENSE          The publication license of the claims, default to "Public Domain" if not specified.
                           You must choose from the following list.
                           List of available licenses: {
                               Public Domain,
                               Creative Commons Attribution 4.0 International,
                               Creative Commons Attribution-ShareAlike 4.0 International,
                               Creative Commons Attribution-NoDerivatives 4.0 International,
                               Creative Commons Attribution-NonCommercial 4.0 International,
                               Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International,
                               Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International,
                               Copyrighted (All rights reserved),
                               Other
                           }

--license-url LICENSE_URL  The url of custom license. This option should be specified if and only if --license="Other".
```

<!--
--optimize-file            Whether to transcode the video & audio or not, default to False if not specified.
                           If specified, i.e. set to True, ffmpeg must first be configured properly in the LBRY Desktop.
-->

### Example

```shell
python -m lbry_batch_uploader \
    "/path/to/dir" \
    "@abc-xyz-ch" \
    --port 9999 \
    --bid 0.1 \
    --fee-amount 1.23 \
    --tags "tag1" "tag2" "tag3" \
    --languages "en" \
    --license "Creative Commons Attribution-NonCommercial 4.0 International"
```

n.b. If you would like to explore the full list of optional arguments that lbrynet accepts, please head to [the exploratory notebooks](https://github.com/thk-cheng/lbry_batch_uploader/tree/main/notebooks) or [the official lbrynet api documentation](https://lbry.tech/api/sdk). Have fun!

## Known Issues

- The order of videos appearing in your channel might not be the same as the upload order.
- The `optimize_file` option in the `publish` method of the lbrynet api is not stable, as a result the `--optimize-file` flag is disabled for the time being.

## Developing

This project uses ``black`` for code formatting and ``flake8`` for linting.

``pre-commit`` is also supported to ensure the above checks have been run.

To properly configure your local environment, please install the development dependencies and set up the commit hooks accordingly.

```shell
python -m pip install --upgrade pip
pip install -r requirements_dev.txt
pip install -e .
pre-commit install
```

## Todos

- Generate thumbnails using ffmpeg if no matching thumbnail is found for a file
- Add a flag that will save the uploading result to a file named "uploaded.txt"
- Add a flag that will scan the `file_directory` for "uploaded.txt", if it is found, the uploader will skip the files listed in it.
- Use the lbrynet api to warn user for insufficient fund (e.g. < 2 LBC)
- Catch `InsufficientFundsError` separately

## License

This project is MIT licensed. For the full license, see [LICENSE](LICENSE).
