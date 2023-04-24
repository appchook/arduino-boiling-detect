import re

# Open the input file
with open("objects.txt", "r") as f:
    lines = f.readlines()

# Initialize two empty lists to store the arrays
time_array = []
temp_array = []

# Loop through each line in the file
for line in lines:
    # Extract the time and temperature values using regular expressions
    time_match = re.search(r'^(\d{2}:\d{2}:\d{2}\.\d{3})', line)
    temp_match = re.search(r'(\d+\.\d+)C', line)

    # If both time and temperature are found in the line, add them to their respective arrays
    if time_match and temp_match:
        time_array.append(time_match.group(1))
        temp_array.append(float(temp_match.group(1)))

# Print the arrays
print("time_array={")
for element in time_array:    
    print("\"",element, "\",")
print("}")

print("temp_array={")
for element in temp_array:    
    print(element, ",")
print("}")
