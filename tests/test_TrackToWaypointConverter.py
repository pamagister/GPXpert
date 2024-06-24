import os
import unittest

from gpxpert.TrackToWaypointConverter import TrackToWaypointConverter


class TrackToWaypointConverterTest(unittest.TestCase):
    gpx1 = '../res/test/Track_01.gpx'
    gpx2 = '../res/test/Track_22.gpx'
    filesToSummarize: list = [gpx1, gpx2]
    testDir = '../res/test'
    testZip = '../res/test/Tracks.zip'

    def test_Convert(self):
        # setup
        converter = TrackToWaypointConverter(self.filesToSummarize)
        gpxFileName = converter.Convert()
        # assert
        assert gpxFileName
        assert gpxFileName.endswith('gpx')

    def test_Convert_VerifyContent(self):
        # setup
        converter = TrackToWaypointConverter(self.filesToSummarize)
        gpxFileName = converter.Convert()
        # assert
        expectedWaypointString = \
            '  <wpt lat="46.022329330444336" lon="8.885900974273682">\n' \
            '    <ele>808.0</ele>\n' \
            '    <name>Tess_01_Cademario - Curio</name>'
        with open(gpxFileName, 'r', encoding='utf-8') as gpxFile:
            assert expectedWaypointString in gpxFile.read()

    def test_Convert_VerifyContent_SummarizeDir(self):
        # setup
        converter = TrackToWaypointConverter(self.testDir)
        gpxFileName = converter.Convert()
        # assert
        expectedWaypointString = \
            '  <wpt lat="46.023641685023904" lon="8.856273796409369">\n' \
            '    <ele>706.0</ele>\n' \
            '    <name>Tess_02_Monte Lema</name>'
        with open(gpxFileName, 'r', encoding='utf-8') as gpxFile:
            assert expectedWaypointString in gpxFile.read()

    def test_Convert_VerifyContent_SummarizeZip(self):
        # setup
        converter = TrackToWaypointConverter(self.testZip)
        gpxFileName = converter.Convert()
        # assert
        expectedWaypointString = \
            '  <wpt lat="46.023641685023904" lon="8.856273796409369">\n' \
            '    <ele>706.0</ele>\n' \
            '    <name>Tess_02_Monte Lema</name>'
        with open(gpxFileName, 'r', encoding='utf-8') as gpxFile:
            assert expectedWaypointString in gpxFile.read()

    def test_Compress(self):
        return
        # setup
        converter = TrackToWaypointConverter(self.gpx1)
        gpxFileName = converter.Compress()[0]
        # assert
        expectedWaypointString = \
            '    <name>Tess_01_Cademario - Curio</name>\n' \
            '    <trkseg>\n' \
            '      <trkpt lat="46.02233" lon="8.8859">\n' \
            '        <ele>808</ele>\n' \
            '      </trkpt>\n'
        with open(gpxFileName, 'r', encoding='utf-8') as gpxFile:
            assert expectedWaypointString in gpxFile.read()

    def test_Compress_Multiple(self):
        # setup
        converter = TrackToWaypointConverter(self.filesToSummarize)
        gpxFileName = converter.Compress()
        # assert
        expectedWaypointString = \
            '    <name>Tess_01_Cademario - Curio</name>\n' \
            '    <trkseg>\n' \
            '      <trkpt lat="46.02233" lon="8.8859">\n' \
            '        <ele>808</ele>\n' \
            '      </trkpt>\n'
        with open(gpxFileName, 'r', encoding='utf-8') as gpxFile:
            assert expectedWaypointString in gpxFile.read()

    def test_Compress_Dir(self):
        # setup
        converter = TrackToWaypointConverter(self.testDir)
        gpxFileName = converter.Compress()
        # assert
        expectedWaypointString = \
            '    <name>Tess_01_Cademario - Curio</name>\n' \
            '    <trkseg>\n' \
            '      <trkpt lat="46.02233" lon="8.8859">\n' \
            '        <ele>808</ele>\n' \
            '      </trkpt>\n'
        with open(gpxFileName, 'r', encoding='utf-8') as gpxFile:
            assert expectedWaypointString in gpxFile.read()

    def test_Compress_Zip(self):
        # setup
        converter = TrackToWaypointConverter(self.testZip)
        gpxFileName = os.path.join(converter.destinationDir, converter.saveFileName) + '_SMALL' + '.gpx'
        # assert
        expectedWaypointString = \
            '    <name>Tess_01_Cademario - Curio</name>\n' \
            '    <trkseg>\n' \
            '      <trkpt lat="46.02233" lon="8.8859">\n' \
            '        <ele>808</ele>\n' \
            '      </trkpt>\n'
        with open(gpxFileName, 'r', encoding='utf-8') as gpxFile:
            assert expectedWaypointString in gpxFile.read()


if __name__ == '__main__':
    unittest.main()
