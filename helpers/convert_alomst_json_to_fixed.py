
import sys
import os
import json

if len(sys.argv) < 2:
    print("missing input file")
    #sys.exit()
    inFile = "json.json"
else:
    inFile = sys.argv[1]

outFile = os.path.splitext(inFile)[0]+"_fixed.json"
if len(sys.argv) > 2:
    outFile = sys.argv[2]

print("reading", inFile)

with open(inFile) as f:
    lines = f.readlines()

print("writing", outFile)
with open(outFile, "w") as outfile:
    outfile.write("[")
    lines[-1]=lines[-1].removesuffix(",\n")
    outfile.writelines(lines)
    outfile.write("]")


