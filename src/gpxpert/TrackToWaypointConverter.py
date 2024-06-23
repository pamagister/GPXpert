import logging
import os
import re

import gpxpy
from gpxpy.gpx import GPXXMLSyntaxException

_logger = logging.getLogger(__name__)

VALID_HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd" version="1.1" creator="gpx.py -- https://github.com/tkrajina/gpxpy">"""


def _GetFirstPointFromGpxFile(gpxFileName):
    try:
        with open(gpxFileName, 'r') as gpxFile:
            gpx = gpxpy.parse(gpxFile)
    except GPXXMLSyntaxException:
        try:
            with open(gpxFileName, 'r', encoding='utf-8') as gpxFile:
                lines = gpxFile.readlines()
            gpxXml = ''.join(lines)
            headerRegex = r'^(.*?)<metadata>'
            extensionRegex = r'<extensions>.*?</extensions>'
            gpxXml = re.sub(headerRegex, VALID_HEADER+'\n<metadata>', gpxXml, flags=re.DOTALL)
            gpxXml = re.sub(extensionRegex, '', gpxXml, flags=re.DOTALL)
            with open(gpxFileName, 'w', encoding='utf-8') as file:
                file.write(gpxXml)
            with open(gpxFileName, 'r') as gpxFile:
                gpx = gpxpy.parse(gpxFile)
        except GPXXMLSyntaxException as err:
            _logger.error(f'Failed to parse {gpxFile.name}')
            return None

    for track in gpx.tracks:
        trackName = track.name
        segment = track.segments[0]
        firstPoint = segment.points[0]
        firstPoint.name = trackName
        firstPoint.time = None
        return firstPoint
    return None


class TrackToWaypointConverter:
    def __init__(self, contentToConvert: list | str):
        """
        Args:
            contentToConvert: List of gpx files or directory that contains gpx files
        """
        self.gpxFiles: list = []
        if not(isinstance(contentToConvert, list)) and os.path.isdir(contentToConvert):
            for filename in os.listdir(contentToConvert):
                if filename.endswith('.gpx'):
                    self.gpxFiles.append(os.path.join(contentToConvert, filename))
        else:
            self.gpxFiles = contentToConvert

    def Convert(self):
        newGpx = gpxpy.gpx.GPX()
        _dirNameFirstFile = os.path.basename(os.path.dirname(self.gpxFiles[0]))
        newGpx.name = f'{_dirNameFirstFile} Summary'

        for gpxFileName in self.gpxFiles:
            firstPoint = _GetFirstPointFromGpxFile(gpxFileName)
            if firstPoint:
                newGpx.waypoints.append(firstPoint)

        return self._Save(newGpx)

    def _Save(self, newGpx) -> str:
        saveDir = os.path.dirname(self.gpxFiles[0])
        fistGpxName = os.path.splitext(os.path.basename(self.gpxFiles[0]))[0]
        lastGpxName = os.path.splitext(os.path.basename(self.gpxFiles[-1]))[0]
        newGpxFileName = os.path.join(saveDir, fistGpxName + '_' + lastGpxName) + '_SUMMARY' + '.gpx'
        with open(newGpxFileName, 'w') as gpxFile:
            gpxFile.write(newGpx.to_xml())
        return newGpxFileName
