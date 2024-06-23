from gpxpert.WaypointTableConverterClient import main

def test_main(capsys):
    """CLI Tests"""
    # capsys is a pytest fixture that allows asserts against stdout/stderr
    # https://docs.pytest.org/en/stable/capture.html
    tableFile = '../res/test/waypoints_table.txt'
    main([tableFile])
    captured = capsys.readouterr()
    assert f"Convert {tableFile}" in captured.out