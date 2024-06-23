import unittest

from gpxpert.TrackToWaypointConverter import TrackToWaypointConverter


class TrackToWaypointConverterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gpx1 = '../res/test/Track_01.gpx'
        gpx2 = '../res/test/Track_22.gpx'
        filesToSummarize: list = [gpx1, gpx2]
        converter = TrackToWaypointConverter(filesToSummarize)
        cls.gpxFileName = converter.Convert()

    def test_Convert(self):
        assert self.gpxFileName
        assert self.gpxFileName.endswith('gpx')

    def test_ConvertToGpx_VerifyContent(self):
        expectedWaypointString = \
            '  <wpt lat="46.022329330444336" lon="8.885900974273682">\n' \
            '    <ele>808.0</ele>\n'\
            '    <name>Tess_01_Cademario - Curio</name>'
        with open(self.gpxFileName, 'r') as gpxFile:
            assert expectedWaypointString in gpxFile.read()


if __name__ == '__main__':
    unittest.main()
