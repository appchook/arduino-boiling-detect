import re

MAX_TEMPS_IN_ARRAY = 5
temp_array = []
first_time = None

def printJsonLine(isEnd : bool):
    # {"time":35,"temps":[8,9.3,10,11.4]},
    print("{\"time\":", last_time - first_time, ",\"temps\":[", ",".join(map(lambda fl: f'{fl:.2f}', temp_array)), "]}", "" if isEnd else ",")

def getSec(hour, min, sec):
    return int(sec) + int(min)*60 + int(hour)*60*60

# Loop through each line in the file
# Open the input file
with open("objects.txt", "r") as f:
    lines = f.readlines()

    for line in lines:
        # Extract the time and temperature values using regular expressions
        time_match = re.search(r'^(\d{2}):(\d{2}):(\d{2})\.\d{3}', line)
        temp_match = re.search(r'(\d+\.\d+)C', line)

        # If both time and temperature are found in the line, add them to their respective arrays
        if time_match and temp_match:        
            temp_array.append(float(temp_match.group(1)))
            last_time = getSec(time_match.group(1), time_match.group(2), time_match.group(3))
            if(first_time == None):
                first_time = last_time
            if len(temp_array) == MAX_TEMPS_IN_ARRAY:
                printJsonLine(False)
                temp_array.clear()
            
printJsonLine(True)

