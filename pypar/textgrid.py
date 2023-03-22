import re


###############################################################################
# Textgrid
###############################################################################


class TextGrid:

    def __init__(self, tiers=None):
        self.tiers = [] if tiers is None else tiers

    def __len__(self):
        return len(self.tiers)

    def __getitem__(self, i):
        return self.tiers[i]

    def read(self, file):
        # Open file
        with open(file) as file:

            # Parse header
            _, short = parse_header(file)
            first_line_beside_header = file.readline()
            try:
                parse_line(first_line_beside_header, short)
            except Exception:
                short = True
            parse_line(first_line_beside_header, short)
            parse_line(file.readline(), short)
            file.readline()
            if short:
                tiers = int(file.readline().strip())
            else:
                tiers = int(file.readline().strip().split()[2])
            if not short:
                file.readline()

            # Iterate over tiers
            for _ in range(tiers):

                # Maybe flush extra line 
                if not short:
                    file.readline()

                # Create interval tier
                if parse_line(file.readline(), short) == 'IntervalTier':

                    # Initialize
                    name = parse_line(file.readline(), short)
                    tier = IntervalTier(name)

                    # Flush tier min/max time
                    parse_line(file.readline(), short)
                    parse_line(file.readline(), short)

                    # Populate
                    for _ in range(int(parse_line(file.readline(), short))):
                        if not short:
                            file.readline().rstrip().split()
                        minTime = parse_line(file.readline(), short)
                        maxTime = parse_line(file.readline(), short)
                        mark = parseMark(file, short)
                        if minTime < maxTime:
                            tier.add(minTime, maxTime, mark)
                    self.tiers.append(tier)

                else:
                    raise ValueError('TextGrid error')

    def write(self, file):
        with open(file, 'w') as file:
            # Write header
            file.write('File type = "ooTextFile"\n')
            file.write('Object class = "TextGrid"\n\n')
            file.write('xmin = {0}\n'.format(self.tiers[0][0].minTime))
            file.write('xmax = {0}\n'.format(self.tiers[0][-1].maxTime))
            file.write('tiers? <exists>\n')
            file.write('size = {0}\n'.format(len(self)))
            file.write('item []:\n')

            # Write interval tiers
            for i, tier in enumerate(self.tiers, 1):
                file.write('\titem [{0}]:\n'.format(i))
                file.write('\t\tclass = "IntervalTier"\n')
                file.write('\t\tname = "{0}"\n'.format(tier.name))
                file.write('\t\txmin = {0}\n'.format(tier[0].minTime))
                file.write('\t\txmax = {0}\n'.format(tier[-1].maxTime))
                file.write(
                    '\t\tintervals: size = {0}\n'.format(len(tier.intervals)))

                # Write intervals
                for j, interval in enumerate(tier.intervals, 1):
                    file.write('\t\t\tintervals [{0}]:\n'.format(j))
                    file.write('\t\t\t\txmin = {0}\n'.format(interval.minTime))
                    file.write('\t\t\t\txmax = {0}\n'.format(interval.maxTime))
                    mark = interval.mark.replace('"', '""')
                    file.write('\t\t\t\ttext = "{0}"\n'.format(mark))

    @classmethod
    def fromFile(cls, file):
        textgrid = cls()
        textgrid.read(file)
        return textgrid


###############################################################################
# Textgrid interval
###############################################################################


class Interval:

    def __init__(self, minTime, maxTime, mark):
        if minTime >= maxTime:
            raise ValueError(minTime, maxTime)
        self.minTime = minTime
        self.maxTime = maxTime
        self.mark = mark


class IntervalTier:

    def __init__(self, name):
        self.name = name
        self.intervals = []

    def __iter__(self):
        return iter(self.intervals)

    def __len__(self):
        return len(self.intervals)

    def __getitem__(self, i):
        return self.intervals[i]

    def add(self, minTime, maxTime, mark):
        self.intervals.append(Interval(minTime, maxTime, mark))


###############################################################################
# Utilities
###############################################################################


def parse_header(source):
    header = source.readline()
    m = re.match(r'File type = "([\w ]+)"', header)
    short = 'short' in m.groups()[0]
    file_type = parse_line(source.readline(), short)
    source.readline()
    return file_type, short


def parse_line(line, short):
    line = line.strip()
    if short:
        if '"' in line:
            return line[1:-1]
        return float(line)
    if '"' in line:
        m = re.match(r'.+? = "(.*)"', line)
        return m.groups()[0]
    m = re.match(r'.+? = (.*)', line)
    return float(m.groups()[0])


def parseMark(text, short):
    line = text.readline()

    # read until the number of double-quotes is even
    while line.count('"') % 2:
        next_line = text.readline()
        line += next_line

    if short:
        pattern = r'^"(.*?)"\s*$'
    else:
        pattern = r'^\s*(text|mark) = "(.*?)"\s*$'
    entry = re.match(pattern, line, re.DOTALL)

    return entry.groups()[-1].replace('""', '"')
