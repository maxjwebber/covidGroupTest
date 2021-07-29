import sys
from os import path
import csv

WORD_SIZE_BYTES = 8

def repToInt(arr, base):
    llen = len(arr)
    power = 1
    num = 0

    # int equivalent is arr[len-1]*1 +
    # arr[len-2]*base + arr[len-3]*(base^2) + ...
    for i in range(llen - 1, -1, -1):
        if int(arr[i]) >= base:
            print('Invalid Number passed to repToDec:'+arr[i])
            exit(1)
        num += int(arr[i]) * power
        power = power * base
    return num

def intToRep(inputNum, base):

    # Convert input number is given base
    # by repeatedly dividing it by base
    # and taking remainder
    if inputNum == 0:
        return [0]
    result = list()
    while (inputNum > 0):
        result.append(inputNum % base)
        inputNum = inputNum // base
    # Reverse the result
    result = result[::-1]

    return result


if len(sys.argv) < 3:
    print("Input should be: convertbincsv.py [0 for csv to bin, 1 for bin to csv] bytesofdata.bin")
    exit(1)
if not path.exists(sys.argv[2]):
    print("File not found: "+sys.argv[2])
    exit(1)

if sys.argv[1] == '0':
    #read csv, convert to binary
    for i in range(2,len(sys.argv)):
        writer = open(sys.argv[i][:(len(sys.argv[2]) - 4)] + ".bin", "wb")
        with open(sys.argv[i], 'r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            params = next(reader)
            '''
            params[0] = n (values per row)
            params[1] = base of string
            params[2] = L, or number of partitions per run (1 for testdata)
            params[3] = number of values (digits) per word
            
            '''
            for i in range(4):
                params[i] = int(params[i])

            writer.write(params[0].to_bytes(2, "big"))
            writer.write(params[1].to_bytes(2, "big"))
            writer.write(params[2].to_bytes(2, "big"))
            writer.write(params[3].to_bytes(2, "big"))

            # n is the length of the string, and groupsPerPartition is the base.
            #first, combine all rows of the csv into one linear array
            rows = list()
            reading = True
            while reading:
                try:
                    row = next(reader)
                    rows.extend(row)
                except StopIteration:
                    reading = False
            i = 0
            while i < len(rows):
                stepUp = i + params[3]
                nextInt = repToInt(rows[i:stepUp], params[1])
                nextbytes = nextInt.to_bytes(WORD_SIZE_BYTES, "big")
                writer.write(nextbytes)
                i += params[3]
            csvfile.close()
        writer.close()
elif sys.argv[1] == '1':
    #read binary, convert to csv
    readfile = open(sys.argv[2], "rb")
    w_filename = sys.argv[2][:(len(sys.argv[2]) - 4)] + ".csv"
    '''
    params[0] = n (values per row)
    params[1] = base of string
    params[2] = L, or number of partitions per run (1 for testdata)
    params[3] = max number of values (digits) per word
    '''
    params = list()
    params.append(int.from_bytes(readfile.read(2), "big"))
    params.append(int.from_bytes(readfile.read(2), "big"))
    params.append(int.from_bytes(readfile.read(2), "big"))
    params.append(int.from_bytes(readfile.read(2), "big"))

    row = list()

    with open(w_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|')
        writer.writerow(params)
        nextWord = readfile.read(WORD_SIZE_BYTES)
        while nextWord:
            nextInt = int.from_bytes(nextWord, "big")
            nextBaseRep = intToRep(nextInt, params[1])
            nextWord = readfile.read(WORD_SIZE_BYTES)
            if len(nextBaseRep) < params[3] and nextWord is not None:
                nextBaseRep = [0] * (params[3] - len(nextBaseRep)) + nextBaseRep
            row.extend(nextBaseRep)
            while len(row) > params[0]:
                writer.writerow(row[:params[0]])
                row = row[params[0]:len(row)]
            if len(row) == params[0]:
                writer.writerow(row)
                row.clear()
else:
    print("First arg should be 0 for csv to bin or 1 for bin to csv.")
    exit(1)