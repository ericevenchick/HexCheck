# hexCheck.py
# This script takes a hex file as an argument, and makes sure that all of the 
# checksums are valid.
from optparse import OptionParser
import sys

class HexFile:
    def __init__(self, filename):
        self.infile = open(filename, 'r')

    def calculateLineChecksum(self, line):
        # remove whitespace
        line = line.strip()

        # get the length of this line (one byte per nybble)
        data_length = int(line[1:3], 16) * 2
        # add legnth other bytes (length, record type, address)
        line_length = data_length + 8 

        # add each byte to compute the checksum
        checksum = 0
        for i in xrange(1, line_length, 2):
            checksum = checksum + int(line[i:i+2], 16) 
        checksum = checksum & 0xFF
        
        # convert to 2's complement
        checksum = (-checksum & (2**8)-1)
        
        return checksum
    def getInvalidLengthLines(self):
        failed_lines = {}
        line_count = 1
        result_str = ""
        self.infile.seek(0)

        for line in self.infile.readlines():
            line = line.strip()
            try:
                # get the length of this line (one byte per nybble)
                data_length = int(line[1:3], 16) * 2
                # add legnth other bytes (length, record type, address)
                line_length = data_length + 11 

                if len(line) != line_length:
                    failed_lines[line_count] = line
                    result_str = result_str + ("Incorrect length on line %d" %
                                                line_count)
            except ValueError:
                result_str = result_str + ("Error parsing line %d\n" % 
                                            line_count)
                failed_lines[line_count] = line
                continue
            line_count = line_count + 1

        if len(failed_lines) == 0:
            result_str = "Record lengths are valid."

        return result_str


    def getInvalidChecksumLines(self):
        failed_lines = {}
        line_count = 1
        result_str = ""
        
        self.infile.seek(0)
        for line in self.infile.readlines():
            line = line.strip()

            try:
                # compute the valid checksum
                valid_checksum = self.calculateLineChecksum(line)
                # get the checksum from the line (last two characters)
                actual_checksum = int(line[-2:], 16)
            except ValueError:
                result_str = result_str + ("Error parsing line %d\n" % 
                                            line_count)
                failed_lines[line_count] = line
                continue

            if actual_checksum != valid_checksum:
                failed_lines[line_count] = line
                result_str = result_str + (("Failed checksum on line %d! " 
                                            "Checksum %X should be %X\n") % 
                                            (line_count, actual_checksum, 
                                            valid_checksum))

            line_count = line_count + 1

        # there are no errors
        if len(failed_lines) == 0:
            result_str = "Record checksums are valid."

        return result_str

if __name__ == '__main__':
    parser = OptionParser()
    (options, args) = parser.parse_args()

    if len(args) != 1:
        print "Input file argument required."
        sys.exit(1)
    hex_file = HexFile(args[0])
    print hex_file.getInvalidChecksumLines()
    print hex_file.getInvalidLengthLines()
