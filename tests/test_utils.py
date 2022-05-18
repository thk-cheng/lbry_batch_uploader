import pytest
from lbry_batch_uploader.utils import get_file_name_no_ext, get_file_name_no_ext_clean


class TestGetFileNameNoExt:
    """Testing the get_file_name_no_ext function"""

    @pytest.mark.parametrize(
        "file_name_with_ext, file_name",
        [
            (
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.webm",
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
            ),
            ("1234567890.mp4", "1234567890"),
            (
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ12345.webm",
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ12345",
            ),
            (
                r"abcdef123-456 [~`!@#$%^&*()_-+={[}]|\:;\"\'<,>.?/].mp4",
                r"abcdef123-456 [~`!@#$%^&*()_-+={[}]|\:;\"\'<,>.?/]",
            ),
            ("08-abcdef-ghi [biyASgmFq9Q].webm", "08-abcdef-ghi [biyASgmFq9Q]"),
        ],
    )
    def test_correct_output(self, file_name_with_ext, file_name):
        assert get_file_name_no_ext(file_name_with_ext) == file_name

    def test_not_string_input(self):
        file_name_with_ext = 123456
        err_msg = "file_name_with_ext must be a string"
        with pytest.raises(TypeError, match=err_msg):
            _ = get_file_name_no_ext(file_name_with_ext)


class TestGetFileNameNoExtClean:
    @pytest.mark.parametrize(
        "file_name_no_ext, file_name_no_ext_clean",
        [
            ("ABCDEF123456" + "!@#$%^&*()+=}{|:;'<,>?/" + '"' + "\\", "ABCDEF123456"),
            (
                "ABCDEF123456" + "！％……＊（）——『〖｛「【〔［" + "〚〘』〗｝」】〕］〛〙·・｜、＼：；“‘《〈，》〉。？",
                "ABCDEF123456",
            ),
            (
                "ABCDEF123456"
                + "!@#$%^&*()+=}{|:;'<,>?/"
                + '"'
                + "\\"
                + "！％……＊（）——『〖｛「【〔［〚〘』〗｝」】〕］〛〙·・｜、"
                + "＼：；“‘《〈，》〉。？",
                "ABCDEF123456",
            ),
        ],
    )
    def test_correct_output(self, file_name_no_ext, file_name_no_ext_clean):
        assert get_file_name_no_ext_clean(file_name_no_ext) == file_name_no_ext_clean
