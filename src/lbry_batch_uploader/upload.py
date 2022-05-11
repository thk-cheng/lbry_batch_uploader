import sys
from parser import Parser
from uploader import Uploader
from utils import get_file_name_no_ext, get_file_name_no_ext_clean


def main():
    parser = Parser()
    parser.parse(sys.argv[1:])

    uploader = Uploader(parser.args)
    uploader.upload_all_files()


if __name__ == '__main__':
    main()
