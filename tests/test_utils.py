from lbry_batch_uploader.utils import get_file_name_no_ext


class TestGetFileNameNoExt():
    def test_alphabet_only(self):
        file_name_with_ext = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.webm'
        file_name = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        assert get_file_name_no_ext(file_name_with_ext) == file_name

    def test_number_only(self):
        file_name_with_ext = '1234567890.mp4'
        file_name = '1234567890'
        assert get_file_name_no_ext(file_name_with_ext) == file_name

    def test_alphabeta_and_number(self):
        file_name_with_ext = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890.webm'
        file_name = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
        assert get_file_name_no_ext(file_name_with_ext) == file_name

    def test_special_chars(self):
        file_name_with_ext = r'abcdef123-456 [~`!@#$%^&*()_-+={[}]|\:;\"\'<,>.?/].mp4'
        file_name = r'abcdef123-456 [~`!@#$%^&*()_-+={[}]|\:;\"\'<,>.?/]'
        assert get_file_name_no_ext(file_name_with_ext) == file_name

    def test_usual_format(self):
        file_name_with_ext = '08-abcdef-ghi [biyASgmFq9Q].webm'
        file_name = '08-abcdef-ghi [biyASgmFq9Q]'
        assert get_file_name_no_ext(file_name_with_ext) == file_name
