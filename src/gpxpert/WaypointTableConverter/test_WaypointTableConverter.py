from gpxpert.WaypointTableConverter.WaypointTableConverter import WaypointTableConverter

import unittest


class WaypointTableConverterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tableFile = '../../../res/test/waypoints_table.txt'
        converter = WaypointTableConverter(tableFile)
        cls.gpxFileName: str = converter.ConvertToGpx()


    def test_ConvertToGpx(self):
        assert self.gpxFileName
        assert self.gpxFileName.endswith('gpx')

    def test_ConvertToGpx_VerifyContent(self):
        expectedWaypointString = \
            '  <wpt lat="46.006348" lon="8.970043">\n' \
            '    <name>9 Monte Bre - Monte Boglia Cassarate</name>\n'\
            '  </wpt>'
        with open(self.gpxFileName, 'r') as gpxFile:
            assert expectedWaypointString in gpxFile.read()
