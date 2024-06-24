import logging
import os
import re
import shutil
import tempfile
import zipfile

import gpxpy
import srtm
from gpxpy.gpx import GPXXMLSyntaxException, GPX, GPXTrackPoint

_logger = logging.getLogger(__name__)

VALID_HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd" version="1.1" creator="gpx.py -- https://github.com/tkrajina/gpxpy">"""


def _GetGpxObjectFromFile(gpxFileName: str) -> GPX | None:
    gpx = None
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
    except GPXXMLSyntaxException:
        try:
            with open(gpxFileName, 'r', encoding='utf-8') as gpxFile:
                gpx = gpxpy.parse(gpxFile)
        except GPXXMLSyntaxException as err:
            _logger.error(f'Failed to parse {gpxFileName}')
    except:
        _logger.error(f' Fatal: Failed to parse {gpxFileName}')
    return gpx


def _GetFirstPointFromGpxFile(gpx: GPX) -> GPXTrackPoint:
    if gpx:
        for track in gpx.tracks:
            trackName = track.name
            segment = track.segments[0]
            firstPoint = segment.points[0]
            firstPoint.name = trackName
            firstPoint.time = None
            return firstPoint


class TrackToWaypointConverter:
    ELEVATION_DATA = srtm.get_data()

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
            firstGpxName = os.path.splitext(os.path.basename(self.gpxFiles[0]))[0]
            lastGpxName = os.path.splitext(os.path.basename(self.gpxFiles[-1]))[0]
            self.saveFileName = firstGpxName + '_' + lastGpxName + '_SUMMARY'
        elif os.path.isdir(contentToConvert):
            self.destinationDir = os.path.dirname(contentToConvert)
            self.saveFileName = os.path.basename(contentToConvert)
            self._ProcessGpxFilesFromDir(contentToConvert)
        elif contentToConvert.endswith('.zip'):
            self.temp_dir = tempfile.mkdtemp()
            self.destinationDir = os.path.dirname(contentToConvert)
            self.saveFileName = os.path.basename(os.path.splitext(contentToConvert)[0])
            self._ProcessGpxFilesFromZip(contentToConvert)
        elif contentToConvert.endswith('.gpx'):
            self.gpxFiles = contentToConvert,
            self.destinationDir = os.path.dirname(self.gpxFiles[0])
            gpxName = os.path.splitext(os.path.basename(self.gpxFiles[0]))[0]
            self.saveFileName = gpxName + '_NEW'
        else:
            raise ValueError("Unsupported input type. Please provide a list of files, a directory, or a zip file.")

    def _ProcessGpxFilesFromList(self, dirList: list):
        for filename in dirList:
            if filename.endswith('.gpx'):
                self.gpxFiles.append(filename)
            elif filename.endswith('.zip'):
                converter = TrackToWaypointConverter(filename)
                converter.Convert()
                converter.Compress()

    def _ProcessGpxFilesFromDir(self, directory: str):
        files = os.listdir(directory)
        self._ProcessGpxFilesFromList([os.path.join(directory, file) for file in files])

    def _ProcessGpxFilesFromZip(self, zip_path: str):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)
            self._ProcessGpxFilesFromDir(self.temp_dir)

    def __del__(self):
        # Cleanup the temporary directory when the instance is deleted
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def Convert(self) -> str:
        newGpx = gpxpy.gpx.GPX()
        newGpx.name = f'{self.saveFileName}'

        for gpxFileName in self.gpxFiles:
            gpx = _GetGpxObjectFromFile(gpxFileName)
            firstPoint = _GetFirstPointFromGpxFile(gpx)
            if firstPoint:
                newGpx.waypoints.append(firstPoint)

        return self._Save(newGpx)

    def Compress(self) -> str:
        newGpx = gpxpy.gpx.GPX()
        newGpx.name = f'{self.saveFileName}'

        resultList = []
        for gpxFileName in self.gpxFiles:
            gpx = _GetGpxObjectFromFile(gpxFileName)
            gpx.reduce_points(min_distance=50)
            for wpt in gpx.waypoints:
                newWpt = gpxpy.gpx.GPXWaypoint(
                    latitude=round(wpt.latitude, 5),
                    longitude=round(wpt.longitude, 5),
                    elevation=self._GetAdjustedElevation(wpt),
                    name=wpt.name
                )
                newGpx.waypoints.append(newWpt)

            for track in gpx.tracks:
                newTrack = gpxpy.gpx.GPXTrack(track.name, track.description)
                for segment in track.segments:
                    newSegment = gpxpy.gpx.GPXTrackSegment()
                    for point in segment.points:
                        point.remove_time()
                        point.latitude = round(point.latitude, 5)
                        point.longitude = round(point.longitude, 5)
                        point.elevation = self._GetAdjustedElevation(point)

                        newSegment.points.append(point)
                    newTrack.segments.append(newSegment)
                newGpx.tracks.append(newTrack)

        self.saveFileName = self.saveFileName + '_SMALL'
        return self._Save(newGpx)

    def _GetAdjustedElevation(self, point) -> int | None:
        try:
            ele = point.elevation or self.ELEVATION_DATA.get_elevation(point.latitude, point.longitude)
            return round(ele)
        except:
            _logger.error(f'unable to determine elevation in {point.name}')
        return

    def _Save(self, newGpx) -> str:
        newGpxFileName = os.path.join(self.destinationDir, self.saveFileName) + '.gpx'
        with open(newGpxFileName, 'w', encoding='utf-8') as gpxFile:
            gpxFile.write(newGpx.to_xml())
        return newGpxFileName
