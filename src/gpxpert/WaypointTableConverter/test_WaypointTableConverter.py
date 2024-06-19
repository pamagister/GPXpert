from gpxpert.WaypointTableConverter.WaypointTableConverter import WaypointTableConverter


def test_ConvertToGpx():
    tableFile = '../../../res/test/waypoints_table.txt'
    converter = WaypointTableConverter(tableFile)
    success = converter.ConvertToGpx()
    assert success

