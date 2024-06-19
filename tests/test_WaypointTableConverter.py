import pytest

from gpxpert.WaypointTableConverter import WaypointTableConverter, main


def test_ConvertToGpx():
    tableFile = '../res/test/waypoints_table.txt'
    converter = WaypointTableConverter(tableFile)
    success = converter.ConvertToGpx()
    assert success


def test_main(capsys):
    """CLI Tests"""
    # capsys is a pytest fixture that allows asserts against stdout/stderr
    # https://docs.pytest.org/en/stable/capture.html
    tableFile = '../res/test/waypoints_table.txt'
    main([tableFile])
    captured = capsys.readouterr()
    assert f"Convert {tableFile}" in captured.out