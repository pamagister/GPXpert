import logging
import os
import re
import shutil
import tempfile
import zipfile

import gpxpy
from gpxpy.gpx import GPXXMLSyntaxException

_logger = logging.getLogger(__name__)

VALID_HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd" version="1.1" creator="gpx.py -- https://github.com/tkrajina/gpxpy">"""


def _GetFirstPointFromGpxFile(gpxFileName):
    try:
        with open(gpxFileName, 'r', encoding='utf-8') as gpxFile:
            gpx = gpxpy.parse(gpxFile)
    except GPXXMLSyntaxException:
        try:
            with open(gpxFileName, 'r', encoding='utf-8') as gpxFile:
                lines = gpxFile.readlines()
            gpxXml = ''.join(lines)
            headerRegex = r'^(.*?)<metadata>'
            extensionRegex = r'<extensions>.*?</extensions>'
            gpxXml = re.sub(headerRegex, VALID_HEADER + '\n<metadata>', gpxXml, flags=re.DOTALL)
            gpxXml = re.sub(extensionRegex, '', gpxXml, flags=re.DOTALL)
            with open(gpxFileName, 'w', encoding='utf-8') as file:
                file.write(gpxXml)
            with open(gpxFileName, 'r', encoding='utf-8') as gpxFile:
                gpx = gpxpy.parse(gpxFile)
        except GPXXMLSyntaxException as err:
            _logger.error(f'Failed to parse {gpxFile.name}')
            return None
    except:
        _logger.error(f'Fatal: Failed to parse {gpxFile.name}')
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
            contentToConvert: List of gpx files, directory that contains gpx files, or a ZIP file containing gpx files
        """
        self.gpxFiles: list = []
        self.destinationDir: str = ''
        self.saveFileName: str = ''
        self.temp_dir = None

        if isinstance(contentToConvert, list):
            self.gpxFiles = contentToConvert
            self.destinationDir = os.path.dirname(self.gpxFiles[0])
            fistGpxName = os.path.splitext(os.path.basename(self.gpxFiles[0]))[0]
            lastGpxName = os.path.splitext(os.path.basename(self.gpxFiles[-1]))[0]
            self.saveFileName = fistGpxName + '_' + lastGpxName + '_SUMMARY' + '.gpx'
        elif os.path.isdir(contentToConvert):
            self.destinationDir = os.path.dirname(contentToConvert)
            self.saveFileName = os.path.basename(contentToConvert) + '.gpx'
            self._AddGpxFilesFromDir(contentToConvert)
        elif contentToConvert.endswith('.zip'):
            self.temp_dir = tempfile.mkdtemp()
            self.destinationDir = os.path.dirname(contentToConvert)
            self.saveFileName = os.path.basename(os.path.splitext(contentToConvert)[0]) + '.gpx'
            self._AddGpxFilesFromZip(contentToConvert)
        else:
            raise ValueError("Unsupported input type. Please provide a list of files, a directory, or a zip file.")

    def _AddGpxFilesFromDir(self, directory: str):
        for filename in os.listdir(directory):
            if filename.endswith('.gpx'):
                self.gpxFiles.append(os.path.join(directory, filename))
            elif filename.endswith('.zip'):
                converter = TrackToWaypointConverter(os.path.join(directory, filename))
                converter.Convert()

    def _AddGpxFilesFromZip(self, zip_path: str):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)
            self._AddGpxFilesFromDir(self.temp_dir)

    def __del__(self):
        # Cleanup the temporary directory when the instance is deleted
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def Convert(self):
        newGpx = gpxpy.gpx.GPX()
        newGpx.name = f'{self.saveFileName}'

        for gpxFileName in self.gpxFiles:
            firstPoint = _GetFirstPointFromGpxFile(gpxFileName)
            if firstPoint:
                newGpx.waypoints.append(firstPoint)

        return self._Save(newGpx)

    def _Save(self, newGpx) -> str:
        newGpxFileName = os.path.join(self.destinationDir, self.saveFileName)
        with open(newGpxFileName, 'w', encoding='utf-8') as gpxFile:
            gpxFile.write(newGpx.to_xml())
        return newGpxFileName
