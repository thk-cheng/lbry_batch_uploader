import sys
from lbry_batch_uploader.parser import Parser
from lbry_batch_uploader.uploader import Uploader


parser = Parser()
parser.parse(sys.argv[1:])

uploader = Uploader(parser.args)
uploader.get_all_files()
uploader.upload_all_files()
