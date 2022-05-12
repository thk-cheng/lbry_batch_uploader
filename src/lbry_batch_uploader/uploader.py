import os
import time
import requests
from argparse import Namespace
from .utils import get_file_name_no_ext, get_file_name_no_ext_clean
from .utils import ConnectionError


class Uploader:
    """Class for uploading files to lbrynet."""

    def __init__(self, args: Namespace) -> None:
        """Initialize the class with parsed arguments."""
        self.base_path = args.file_directory
        self.port_url = f"http://localhost:{args.port}/"

        files_name_all = os.listdir(self.base_path)
        self.files_name_valid = self._get_valid_files(files_name_all)
        files_name_valid_no_ext = [
            get_file_name_no_ext(name) for name in self.files_name_valid
        ]

        self.files_valid = {
            file_name_no_ext: {
                "file_name": file_name,
                "desc_name": None,
                "thumbnail_name": None,
            } for file_name, file_name_no_ext in \
                zip(self.files_name_valid, files_name_valid_no_ext)
        }
        self._get_valid_descriptions(files_name_all)
        self._get_valid_thumbnails(files_name_all)

        self.base_params = {
            "channel_name": args.channel_name,
            "optimize_file": args.optimize_file and self._has_ffmpeg(),
            "bid": args.bid,
            "fee_currency": "lbc",
            "fee_amount": args.fee_amount,
            "tags": args.tags,
            "languages": args.languages,
            "license": args.license,
            "funding_account_ids": [],
            "preview": False,
            "blocking": False,
        }
        if self.base_params["license"] == "Other":
            self.base_params["license_url"] = args.license_url

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

            if params["desc_name"] is not None:
                full_path = os.path.join(
                    self.base_path,
                    params["desc_name"]
                )
                with open(full_path, "r") as f:
                    file_params["description"] = f.read()

            if params["thumbnail_name"] is not None:
                full_path = os.path.join(
                    self.base_path,
                    params["thumbnail_name"]
                )
                file_params["thumbnail_url"] = self._upload_thumbnail(
                    file_params["name"],
                    full_path
                )

            claim_id = self._upload_file(file_params)
            claim_url = f"lbry://{file_params['name']}#{claim_id}"
            upload_msg = f"Sucessfully uploaded {params['file_name']}\n" + \
                            f"The claim id is {claim_id}\n" + \
                            f"The claim url is {claim_url}"
            print(upload_msg, end="\n\n")

            if idx != len(self.files_valid) - 1:
                print("Wait 10 seconds to space out uploads...", end="\n\n")
                time.sleep(10)

    def _get_valid_descriptions(self, files_name_all) -> None:
        """Get all valid descriptions for the corresponding files, if any."""
        target_ext = ("txt", "description")
        for name_no_ext in self.files_valid.keys():
            target_desc_names = [f"{name_no_ext}.{ext}" for ext in target_ext]
            for desc_name in target_desc_names:
                if desc_name in files_name_all:
                    self.files_valid[name_no_ext]["desc_name"] = desc_name
                    break

    def _get_valid_files(self, files_name_all) -> list[str]:
        """Get all valid files for upload in the specified directory."""
        target_ext = ("mp4", "mkv", "webm", "mp3", "opus")
        files_name_valid = []
        for name in files_name_all:
            ext = name.split(".")[-1]
            if ext in target_ext:
                files_name_valid.append(name)
        return sorted(files_name_valid)

    def _get_valid_thumbnails(self, files_name_all) -> None:
        """Get all valid thumbnails for the corresponding files, if any."""
        target_ext = ("gif", "jpg", "png")
        for name_no_ext in self.files_valid.keys():
            target_t_names = [f"{name_no_ext}.{ext}" for ext in target_ext]
            for t_name in target_t_names:
                if t_name in files_name_all:
                    self.files_valid[name_no_ext]["thumbnail_name"] = t_name
                    break

    def _has_ffmpeg(self) -> bool:
        """Helper function for verifying proper configuration of ffmpeg."""
        json = {"method": "ffmpeg_find"}
        req_result = self._post_req(json=json)["result"]
        if not req_result["available"]:
            msg = "ffmpeg is not configured properly." + \
                    "--optimize-file set to False."
            print(msg)
        return req_result["available"]

    def _post_req(self, port=None, **kwargs) -> dict[str, str]:
        """Helper function for submitting post request."""
        if port is None:
            port = self.port_url

        try:
            return requests.post(port, **kwargs).json()
        except ConnectionRefusedError:
            msg = "Please check that LBRY Desktop is up and running " + \
                    "with a properly configured port (default to 5279)."
            raise ConnectionError(msg) from None

    def _upload_file(self, file_params: dict) -> [str, str]:
        """Upload a single file to LBRY, return claim id."""
        json = {"method": "publish", "params": file_params}
        req_result = self._post_req(json=json)["result"]
        req_result_outputs = req_result["outputs"][0]
        return req_result_outputs["claim_id"]

    def _upload_thumbnail(self, t_name: str, t_path: str) -> str:
        """Upload a single thumbnail to spee.ch, return thumbnail url."""
        with open(t_path, "rb") as f:
            thumbnail = f.read()
        req_data = self._post_req(
            port="https://spee.ch/api/claim/publish",
            files={"file": thumbnail},
            data={"name": t_name}
        )["data"]
        return req_data["serveUrl"]


if __name__ == "__main__":
    pass
