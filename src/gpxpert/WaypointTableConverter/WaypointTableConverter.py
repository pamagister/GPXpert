import logging
import os.path
import re

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
        with open(self.textFile, 'r') as tableFile:
            lines = tableFile.readlines()
            for line in lines:
                _logger.debug(f'Process line {line}')
                result = re.sub(PATTERN, REPLACEMENT, line.strip())
                results.append(result)

        with open(self.textFile + '_GPX' + '.gpx', 'w') as gpxFile:
            _logger.info(f'write results to: {gpxFile}')
            gpxFile.write(self.GetHeader())
            for result in results:
                gpxFile.write(result + '\n')
            gpxFile.write(self.GetFooter())
        return True

    def GetHeader(self) -> str:
        filename = os.path.basename(self.textFile)
        header = (
            f'<?xml version="1.0" encoding="UTF-8"?>' + '\n'
            f'<gpx xmlns="http://www.topografix.com/GPX/1/1" creator="python">' + '\n'
            f'<metadata>' + '\n'
            f'    <name>{filename}</name>' + '\n'
            f'</metadata>') + '\n'
        return header

    @staticmethod
    def GetFooter() -> str:
        return "</gpx>"

