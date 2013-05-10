import argparse, csv, datetime, os.path
from ctypes import *

#Load library.
cdll.LoadLibrary("libftdimut.so")
lib = CDLL("libftdimut.so")

def parseData(argsData):
  data = []
  for d in argsData:
    title, request = d.split(":")
    new = {'title': title, 'request':request}
    data.append(new)
  return data

def csvHeaders():
  out = []
  out.append("Time")
  for d in data:
    out.append(d['title'])
  return out

def csvRow():
  out = []
  time = datetime.datetime.now() - start  
  out.append(time.seconds + time.microseconds / 1000000)
  for d in data:
    out.append(str(lib.ftdimut_getData(int(d['request'], 0))))
  return out

parser = argparse.ArgumentParser(description='Log MUT data using an openport 1.3 cable.')
parser.add_argument("-t", "--testing", action='store_true', help='Enable testing in the libftdimut library.')
parser.add_argument("-o", "--output", help='Output file.')
parser.add_argument("data", metavar='Name:Request', nargs='+', help='Data values to grab.')

args = parser.parse_args()
data = parseData(args.data)

if(args.testing):
  lib.ftdimut_setTesting(True)

if args.output is None:
  args.output = datetime.datetime.now().isoformat().replace("T", "_") + ".csv"

if(os.path.exists(args.output)):
  print("Output file exists!")
  exit(2)

ftStatus = lib.ftdimut_setup()
if ftStatus != 0:
  if ftStatus == 2:
    print("Device not found.")
  if ftStatus == 3:
    print("Cannot open device.")
  else:
    print("Unknown error.")
  exit(2)

ftStatus = 1
while ftStatus != 0:
  ftStatus = lib.ftdimut_init()


print("Connected")
print("Logging to %s" % args.output)

start = datetime.datetime.now()

import csv
with open(args.output, 'w', newline='') as csvfile:
  spamwriter = csv.writer(csvfile, delimiter=',',
                          quotechar='|', quoting=csv.QUOTE_MINIMAL)
  spamwriter.writerow(csvHeaders())
  try:
    while(True):
      spamwriter.writerow(csvRow())
  except KeyboardInterrupt:
    exit(0)

