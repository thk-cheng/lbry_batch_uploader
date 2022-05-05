import pytest
from lbry_batch_uploader.utils import get_file_name_no_ext, _pipe_cmds
from lbry_batch_uploader.utils import PipeError


class TestGetFileNameNoExt:
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


class TestPipeCmds:
    def test_type_error(self):
        cmds = 'ls'
        with pytest.raises(TypeError, match='cmds must be a list'):
            p = _pipe_cmds(cmds)

    def test_pipe_error_case_tt(self):
        cmds = ['ls']
        with pytest.raises(PipeError, match='At least two commands are needed for piping'):
            p = _pipe_cmds(cmds)

    def test_pipe_error_case_tf(self):
        cmds = ['ls', '-l']
        with pytest.raises(PipeError, match='At least two commands are needed for piping'):
            p = _pipe_cmds(cmds)

    def test_pipe_error_case_ft(self):
        cmds = [['ls']]
        with pytest.raises(PipeError, match='At least two commands are needed for piping'):
            p = _pipe_cmds(cmds)

    def test_pipe_cmds(self):
        # cmd_0 = ['ffmpeg', '-i', file_name_absolute]
        # cmd_1 = ['grep', 'Duration']
        # cmd_2 = ['awk', '{print $2}']
        # cmd_3 = ['tr', '-d', ',']
        # cmd_4 = ['awk', '-F', ':', '{print ($3+$2*60+$1*3600)/2}']
        pass

