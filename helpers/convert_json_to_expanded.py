
import sys
import os
import json
 

if len(sys.argv) < 2:
    print("missing input file")
    #sys.exit()
    inFile = "json_fixed.json"
else:
    inFile = sys.argv[1]

print("reading", inFile)

time_value = []

# Opening JSON file
with open(inFile) as f:
    
    # returns JSON object as 
    # a dictionary
    data = json.load(f)

    for line in data:
        time = line["time"] - len(line["temps"])
        for temp in line["temps"]:
            time+=1
            time_value.append({"time": time, "temp": temp})

outFile = os.path.splitext(inFile)[0]+"_expanded.json"
print("writing", outFile)
with open(outFile, "w") as outfile:
    json.dump(time_value, outfile, indent=2)

