import logging
import sys

from common.client import parse_args, setup_logging
from gpxpert.WaypointTableConverter import WaypointTableConverter

_logger = logging.getLogger(__name__)


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
    converter.Convert()

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
    #   python src/gpxpert/WaypointTableConverterClient.py C:/dev/GPXpert/res/test/waypoints_table.txt -vv
    #
    run()
