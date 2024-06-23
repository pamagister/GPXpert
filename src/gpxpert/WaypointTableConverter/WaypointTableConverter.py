import logging
import os.path
import re
import gpxpy

_logger = logging.getLogger(__name__)

PATTERN = r"(\d{2}) ([\w\s.-]+) N([\d.]+) E([\d.]+)"
REPLACEMENT = r'<wpt lat="\3" lon="\4">\n\t<name>\1 \2</name>\n</wpt>'


class WaypointTableConverter:
    def __init__(self, textFile):
        _logger.info(f'textFile to parse: {textFile}')
        assert os.path.isfile(textFile)
        self.textFile = textFile

    def ConvertToGpx(self):
        gpx = gpxpy.gpx.GPX()
        gpx.name = self.textFile
        with open(self.textFile, 'r') as tableFile:
            lines = tableFile.readlines()
            for line in lines:
                match = re.match(PATTERN, line.strip())

                if match:
                    gpx_wps = gpxpy.gpx.GPXWaypoint()
                    number = int(match.group(1))
                    name = str(match.group(2))
                    gpx_wps.latitude = float(match.group(3))
                    gpx_wps.longitude = float(match.group(4))
                    gpx_wps.name = f'{number} {name}'
                    gpx.waypoints.append(gpx_wps)

        gpxFileName = self.textFile + '_GPX' + '.gpx'
        with open(gpxFileName, 'w') as gpxFile:
            _logger.info(f'write results to: {gpxFile.name}')
            gpxFile.write(gpx.to_xml())

        return gpxFileName
