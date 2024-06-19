import os.path
import re


import logging

_logger = logging.getLogger(__name__)

PATTERN = r"(\d{2}) ([\w\s.-]+) N([\d.]+) E([\d.]+)"
REPLACEMENT = r'<wpt lat="\3" lon="\4">\n\t<name>\1 \2</name>\n</wpt>'


class WaypointTableConverter:
    def __init__(self, textFile):
        _logger.info(f'textFile to parse: {textFile}')
        assert os.path.isfile(textFile)
        self.textFile = textFile

    def ConvertToGpx(self):
        results = []
        with open(self.textFile, 'r') as file:
            lines = file.readlines()
            for line in lines:
                _logger.debug(f'Process line {line}')
                result = re.sub(PATTERN, REPLACEMENT, line.strip())
                results.append(result)

        with open(self.textFile + '_GPX' + '.gpx', 'w') as file:
            file.write(self.GetHeader())
            for result in results:
                file.write(result + '\n')
            file.write(self.GetFooter())
        return True

    def GetHeader(self) -> str:
        filename = os.path.basename(self.textFile)
        header = (
            f'<?xml version="1.0" encoding="UTF-8"?>'
            f'<gpx version="1.0">'
            f'<metadata>'
            f'    <name>{filename}</name>'
            f'/metadata>') + '\n'
        return header

    @staticmethod
    def GetFooter() -> str:
        return "</gpx>"


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="Parse names and Positions from a table-like formatted test file")
    parser.add_argument(
        "--version",
        action="version",
        version=f"GPXpert {__version__}",
    )
    parser.add_argument(dest="file", help="text file to be converted", type=str, metavar="STR")
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):
    """Wrapper allowing this function to be called with string arguments in a CLI fashion

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose"]``).
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Starting conversion")
    tableFile = args.file
    converter = WaypointTableConverter(tableFile)
    converter.ConvertToGpx()

    print(f"Convert {args.file}")
    _logger.info("Script ends here")


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html

    # Usage from terminal:
    #
    #   python src/gpxpert/WaypointTableConverter.py C:/dev/GPXpert/res/test/waypoints_table.txt -vv
    #
    run()