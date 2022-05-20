import os
import time
import requests
from requests import RequestException
from argparse import Namespace
from typing import Dict, List
from lbry_batch_uploader.utils import get_file_name_no_ext, get_file_name_no_ext_clean


class Uploader:
    """Class for uploading files to lbrynet."""

    def __init__(self, args: Namespace) -> None:
        """Initialize the class with parsed arguments."""
        self._set_base_path(args.file_directory)
        self._set_port_url(args.port)
        self.base_params = {
            "channel_name": args.channel_name,
            "optimize_file": args.optimize_file and self._has_ffmpeg(),
            "bid": args.bid,
            "tags": args.tags,
            "languages": args.languages,
            "license": args.license,
            "preview": False,
            "blocking": False,
        }
        if float(args.fee_amount):
            self.base_params["fee_currency"] = "lbc"
            self.base_params["fee_amount"] = args.fee_amount
        if self.base_params["license"] == "Other":
            self.base_params["license_url"] = args.license_url

    def get_all_files(self) -> None:
        """Get all valid files, and their descriptions and thumbnails."""
        files_name_all = os.listdir(self.base_path)
        files_name_valid = self._get_valid_files(files_name_all)
        files_name_valid_no_ext = [
            get_file_name_no_ext(name) for name in files_name_valid
        ]

        self.files_valid: Dict[str, Dict[str, str]] = {}
        for fn, fn_no_ext in zip(files_name_valid, files_name_valid_no_ext):
            self.files_valid[fn_no_ext] = {
                "file_name": fn,
                "desc_name": "",
                "thumbnail_name": "",
            }

        self._get_valid_ftypes(files_name_all, "descriptions", ("txt", "description"))

        self._get_valid_ftypes(files_name_all, "thumbnails", ("gif", "jpg", "png"))

    def upload_all_files(self) -> None:
        """Upload all valid files to lbrynet."""
        for idx, (name_no_ext, params) in enumerate(self.files_valid.items()):
            file_params = self.base_params.copy()
            file_params["title"] = name_no_ext
            file_params["name"] = get_file_name_no_ext_clean(name_no_ext)

            if file_params["optimize_file"]:
                file_ext = params["file_name"].split(".")[-1]
                file_name = f"{name_no_ext}_fixed.{file_ext}"
            else:
                file_name = params["file_name"]
            file_params["file_path"] = os.path.join(self.base_path, file_name)

            if params["desc_name"]:
                full_path = os.path.join(self.base_path, params["desc_name"])
                with open(full_path, "r") as f:
                    file_params["description"] = f.read()

            if params["thumbnail_name"]:
                full_path = os.path.join(self.base_path, params["thumbnail_name"])
                file_params["thumbnail_url"] = self._upload_thumbnail(
                    file_params["name"], full_path
                )

            claim_id = self._upload_file(file_params)
            claim_url = f"lbry://{file_params['name']}#{claim_id}"
            upload_msg = (
                f"Sucessfully uploaded {params['file_name']}\n"
                + f"The claim id is {claim_id}\n"
                + f"The claim url is {claim_url}"
            )
            print(upload_msg, end="\n\n")

            if idx != len(self.files_valid) - 1:
                print("Wait 10 seconds to space out uploads...", end="\n\n")
                time.sleep(10)

    def _get_req_info(self, req_json: dict, info_type: str) -> dict:
        """Get 'result' from json, except error occured in the post request."""
        if (info_type != "data") and (info_type != "result"):
            err_msg = "'info_type' should be either 'data' or 'result'."
            raise ValueError(err_msg)

        try:
            req_info: dict = req_json[info_type]
        except KeyError as e:
            req_err = req_json["error"]
            if req_err["data"]["name"] == "ValueError":
                raise ValueError(req_err["message"]) from None
            else:
                raise e from None

        return req_info

    def _get_valid_files(self, files_name_all) -> List[str]:
        """Get all valid files for upload in the specified directory."""
        target_ext = ("mp4", "mkv", "webm", "mp3", "opus")
        files_name_valid = []
        for name in files_name_all:
            ext = name.split(".")[-1]
            if ext in target_ext:
                files_name_valid.append(name)
        return sorted(files_name_valid)

    def _get_valid_ftypes(self, files_name_all, f_type, target_ext) -> None:
        """Get all valid desc/thumbnails for the corresponding files."""
        if (f_type != "descriptions") and (f_type != "thumbnails"):
            err_msg = "Only support getting thumbnails or descriptions."
            raise ValueError(err_msg)

        for name_no_ext, finfos in self.files_valid.items():
            target_names = [f"{name_no_ext}.{ext}" for ext in target_ext]
            for name in target_names:
                if name in files_name_all:
                    if f_type == "descriptions":
                        finfos["desc_name"] = name
                    else:
                        finfos["thumbnail_name"] = name
                    break

    def _has_ffmpeg(self) -> bool:
        """Helper function for verifying proper configuration of ffmpeg."""
        json_ffmpeg = {"method": "ffmpeg_find"}
        req_json: dict = post_req(self.port_url, json=json_ffmpeg)
        req_result: dict = self._get_req_info(req_json, "result")
        req_result_avail: bool = req_result["available"]

        if not req_result_avail:
            msg = "ffmpeg is not configured properly." + "--optimize-file set to False."
            print(msg)

        return req_result_avail

    def _set_base_path(self, path: str) -> None:
        """Set 'base_path', check existence and convert to absolute."""
        path_abs = os.path.abspath(path)
        if os.path.exists(path_abs):
            self.base_path = path_abs
        else:
            err_msg = f"The directory {path_abs} does not exist."
            raise FileNotFoundError(err_msg)

    def _set_port_url(self, port: int) -> None:
        """Set 'path_url', check value and availability."""
        if (port < 0) or (port > 65353):
            err_msg = f"The port {port} is not between 0 and 65353."
            raise TypeError(err_msg)

        # Check that the provided port is accessible
        port_url = f"http://localhost:{port}"
        _ = post_req(port_url, json={"method": "version"})

        self.port_url = port_url

    def _upload_file(self, file_params: dict) -> str:
        """Upload a single file to LBRY, return claim id."""
        json_uploadfile = {"method": "publish", "params": file_params}
        req_json: dict = post_req(self.port_url, json=json_uploadfile)
        req_result: dict = self._get_req_info(req_json, "result")
        claim_id: str = req_result["outputs"][0]["claim_id"]
        return claim_id

    def _upload_thumbnail(self, t_name: str, t_path: str) -> str:
        """Upload a single thumbnail to spee.ch, return thumbnail url."""
        with open(t_path, "rb") as f:
            thumbnail = f.read()

        req_json: dict = post_req(
            "https://spee.ch/api/claim/publish",
            files={"file": thumbnail},
            data={"name": t_name},
        )
        req_data: dict = self._get_req_info(req_json, "data")
        thumbnail_url: str = req_data["serveUrl"]
        return thumbnail_url


def post_req(port_url: str, **kwargs) -> dict:
    """Helper function for submitting post request, return json response."""
    try:
        req_json: dict = requests.post(port_url, **kwargs).json()
        return req_json
    except RequestException as e:
        raise e from None
