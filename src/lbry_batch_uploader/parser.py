from argparse import ArgumentParser
from typing import Sequence
from lbry_batch_uploader.utils import RFC5646_LANGUAGE_TAGS, LICENSES


class Parser:
    """Class for a customized argument parser."""

    def __init__(self) -> None:
        """Initialize the Parser instance."""
        self.argparser = ArgumentParser(description="Batch uploader for LBRY Desktop")
        self._add_args()

    def parse(self, cmd_args: Sequence[str]) -> None:
        """Parse arguments from the command line."""
        self.args = self.argparser.parse_args(cmd_args)

        is_other = self.args.license == "Other"
        if (is_other and (self.args.license_url is None)) or (
            not is_other and (self.args.license_url is not None)
        ):
            del self.args
            err_msg = (
                "--license-url should be specified "
                + "if and only if --license='Other'"
            )
            self.argparser.error(err_msg)

    def _add_args(self) -> None:
        """Add arguments to the Parser instance."""
        self.argparser.add_argument(
            "file_directory",
            type=str,
            help="""The absolute path of directory that \
                    contains the files to be uploaded""",
        )

        self.argparser.add_argument(
            "channel_name", type=str, help="The name of publisher channel (with the @)"
        )

        self.argparser.add_argument(
            "--optimize-file",
            action="store_true",
            help="""Whether to transcode the video & audio or not, \
                    default to False if not specified. \
                    If specified, i.e. set to True, \
                    ffmpeg must first be configured properly \
                    in the LBRY Desktop.""",
        )

        self.argparser.add_argument(
            "--port",
            default=5279,
            type=int,
            help="""The port that lbrynet listens to, \
                        default to 5279 if not specified.""",
        )

        self.argparser.add_argument(
            "--bid",
            default="0.0001",
            type=str,
            help="""The amount to back the claim, \
                    default to 0.0001 if not specified.""",
        )

        self.argparser.add_argument(
            "--fee-amount",
            default="0",
            type=str,
            help="""The content download fee in LBC, \
                    default to 0 if not specified.""",
        )

        self.argparser.add_argument(
            "--tags",
            nargs="+",
            default=[],
            type=str,
            help="""The content tags of the claims, \
                        default to [] if not specified.""",
        )

        self.argparser.add_argument(
            "--languages",
            nargs="+",
            default=["en"],
            type=str,
            choices=list(RFC5646_LANGUAGE_TAGS.keys()),
            help="""The languages of the claims in RFC5646 format, \
                        default to ["en"] if not specified. \
                        More than one could be specified. \
                        Please refer to RFC5646 for the complete list.""",
            metavar="L",
        )

        self.argparser.add_argument(
            "--license",
            type=str,
            choices=LICENSES,
            help="""The publication license of the claims. \
                        List of available licenses: {%(choices)s}""",
            metavar="LICENSE",
        )

        self.argparser.add_argument(
            "--license-url",
            type=str,
            help="""The url of custom license. \
                        This option should be specified \
                        if and only if --license='Other'.""",
        )
