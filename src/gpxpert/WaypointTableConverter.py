import os.path
import re

# Der Text mit einem Punkt im Namen
PATTERN = r"(\d{2}) ([\w\s.-]+) N([\d.]+) E([\d.]+)"
REPLACEMENT = r'<wpt lat="\3" lon="\4">\n\t<name>\1 \2</name>\n</wpt>'


class WaypointTableConverter:
    def __init__(self, textFile):
        assert os.path.isfile(textFile)
        self.textFile = textFile

    def ConvertToGpx(self):
        results = []
        with open(self.textFile, 'r') as file:
            lines = file.readlines()
            for line in lines:
                result = re.sub(PATTERN, REPLACEMENT, line.strip())
                results.append(result)

        with open(self.textFile+'.xml', 'w') as file:
            for result in results:
                file.write(result + '\n')
        return True
