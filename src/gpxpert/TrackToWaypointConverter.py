import os

import gpxpy


def _GetFirstPointFromGpxFile(gpxFile):
    gpx = gpxpy.parse(gpxFile)
    for track in gpx.tracks:
        trackName = track.name
        segment = track.segments[0]
        firstPoint = segment.points[0]
        firstPoint.name = trackName
        break
    return firstPoint


class TrackToWaypointConverter:
    def __init__(self, gpxFiles: list):
        self.gpxFiles: list = gpxFiles

    def Convert(self):
        newGpx = gpxpy.gpx.GPX()
        newGpx.name = 'Generated from many gpx files'
        for gpxFileName in self.gpxFiles:
            with open(gpxFileName) as gpxFile:
                firstPoint = _GetFirstPointFromGpxFile(gpxFile)
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

