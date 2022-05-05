import os
import subprocess
from subprocess import PIPE, STDOUT, CompletedProcess


class Error(Exception):
    """Base class for other exceptions"""
    pass


class PipeError(Error):
    """Exception raised for error in piping commands."""
    pass

class ThumbnailCreationError(Error):
    """
    Exception raised for error in creating thumbnail from an input.

    Attributes
    ----------
    file_name_absolute: str
        The absolute path of the input file

    p: subprocess.CompletedProcess
        An instance of CompletedProcess for the command
            that attempts to create the thumbnail

    """

    def __init__(self, file_name_absolute: str, p: CompletedProcess):
        self.file_name_absolute = file_name_absolute
        self.p = p
        super().__init__()

    def __str__(self):
        return f'Fail to create thumbnail for {self.file_name_absolute}'


def get_file_name_no_ext(file_name_with_ext: str) -> str:
    """
    Get the name of the input file without extension.

    Parameters
    ----------
    file_name_with_ext: str
        The name of input file with extension

    Returns
    -------
    str
        The name of the input file without extension

    """

    try:
        name_parts = file_name_with_ext.split('.')[0:-1]
    except AttributeError:
        raise TypeError('file_name_with_ext must be a string') from None

    # Join the parts back together with '.', as the original name may contain '.'
    return '.'.join(name_parts)


def create_thumbnail(base_path: str, file_name: str) -> str:
    """
    Create a thumbnail from the input file.

    The selected frame is chosen to be at the middle of the input file.

    Parameters
    ----------
    base_path: str
        The base path which contains the input file

    file_name: str
        The name of input file with extension

    Returns
    -------
    str
        The name of the thumbnail with extension

    """

    file_name_absolute = os.path.join(base_path, file_name)
    thumbnail_name = f'{get_file_name_no_ext(file_name)}.png'
    thumbnail_name_absolute = os.path.join(base_path, thumbnail_name)

    # Explanation for all the commands below:
    #   cmd_0: Get info of the input file by ffmpeg
    #   cmd_1: Grep the line that contains the duration of input file
    #   cmd_2: Isolate the duration of video from that line
    #   cmd_3: Remove trailing comma
    #   cmd_4: Find the time corresponds to the middle of the input file
    #   cmd_5: Actual command that creates the thumbnail by ffmpeg

    cmd_0 = ['ffmpeg', '-i', file_name_absolute]
    cmd_1 = ['grep', 'Duration']
    cmd_2 = ['awk', '{print $2}']
    cmd_3 = ['tr', '-d', ',']
    cmd_4 = ['awk', '-F', ':', '{print ($3+$2*60+$1*3600)/2}']

    # Same as adding "2>&1" at the end of cmd_0
    p = subprocess.run(cmd_0, stdout=PIPE, stderr=STDOUT, text=True)

    # Pipe commands from cmd_0 to cmd_4
    p = _pipe_cmds([cmd_1, cmd_2, cmd_3, cmd_4], prev_p=p)

    # # Format the delayed start time as "00:00:00.000"
    # delayed_time_in_sec = float(p.stdout)
    # delayed_hour = delayed_time_in_sec // 3600
    # delayed_min = (delayed_time_in_sec - delayed_hour * 3600) // 60
    # delayed_sec, delayed_millisec = divmod(delayed_time_in_sec - delayed_hour * 3600 - delayed_min * 60, 1)
    # delayed_start_time = f'{int(delayed_hour):02}:{int(delayed_min):02}:{int(delayed_sec):02}.{delayed_millisec*1000:.0f}'

    # Get the delayed start time from p
    delayed_start_time = str(float(p.stdout))

    cmd_5 = [
        'ffmpeg',
        '-y',
        '-i', file_name_absolute,
        '-frames:v', '1',
        '-ss', delayed_start_time,
        thumbnail_name_absolute
    ]

    p1 = subprocess.run(cmd_5, capture_output=True, text=True)

    if p1.returncode != 0:
        raise ThumbnailCreationError(file_name_absolute, p1)
    else:
        print(f'Successfully created thumbnail for {file_name_absolute}')

    return thumbnail_name


def _pipe_cmds(cmds: list[list[str]], *, prev_p: CompletedProcess = None) -> CompletedProcess:
    """
    Piping commands using the subprocess module.

    Parameters
    ----------
    cmds: list[str]
        A list that stores all the commands

    prev_p: subprocess.CompletedProcess (Optional)
        An instance of CompletedProcess for the previous command

    Returns
    -------
    p: subprocess.CompletedProcess
        An instance of CompletedProcess for the final result

    """

    if not isinstance(cmds, list):
        raise TypeError('cmds must be a list')

    if not isinstance(cmds[0], list) or len(cmds)<2:
        raise PipeError('At least two commands are needed for piping')

    if prev_p is not None:
        p = prev_p
    else:
        p = subprocess.run(cmd[0], capture_output=True, text=True)
        cmds = cmds[1:]

    for cmd in cmds:
        p = subprocess.run(cmd, capture_output=True, text=True, input=p.stdout)

    return p


def main():
    base_path = '/Users/kennethcheng/Downloads/lbry-upload/short-videos'
    file_name = 'Shortest Video on Youtube Part 1 [tPEE9ZwTmy0].webm'
    print(create_thumbnail(base_path, file_name))


if __name__ == '__main__':
    main()
