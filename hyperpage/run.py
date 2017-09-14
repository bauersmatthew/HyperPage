from hyperpage import display
from hyperpage import input
from hyperpage import settings
from hyperpage import document
import argparse
import sys
import os.path

def valid_file(s):
    if not None and not os.path.isfile(s):
        raise argparse.ArgumentTypeError(
            'File \'{}\' is not a valid file.'.format(s))
    return s

DEFAULT_CONFIG_PATH = '~/.config/hyperpage/hyperpage.ini'

class GenerateINI(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
        sys.stdout.write(settings.default_settings_ini)
        sys.exit(0)

def main():
    # parse options
    parser = argparse.ArgumentParser(
        description='Display markdown files in the terminal.')
    parser.add_argument('file', metavar='file.md',
                        type=valid_file, default=None,
                        help='The initial file to be opened.')
    parser.add_argument('-c', '--config', metavar='config.ini',
                        type=valid_file, default=None,
                        help=('The config file to use. If unspecified, '
                              '{} is used. '
                              'If that is not available, internal defaults '
                              'will be used instead.').format(
                                  DEFAULT_CONFIG_PATH))
    parser.add_argument('-g', '--generate', nargs=0, action=GenerateINI,
                        help='Print a default config file to stdout.')
    
    args = parser.parse_args()

    try:
        display.init()
        input.init()
        settings.init(args.config)
        
        document.load(args.file)

        while True:
            input.handle_next()
    except input.ExitException:
        sys.exit(0)
    except:
        raise
    finally:
        display.exit()
        input.exit()

if __name__ == '__main__':
    main()
