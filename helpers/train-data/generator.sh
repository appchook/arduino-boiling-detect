#!/bin/bash

FILES="/home/gil/projects/BoilDetectServer/sessions/good/*.xz"
for fullPath in $FILES; do
	# copy xz file from /home/gil/projects/BoilDetectServer/sessions/good/ to here

	echo $fullPath

	fullName=$(basename "$fullPath")
	cp $fullPath $fullName
	
	# extract the file
	tar -xf $fullName
	fileName=$(basename "$fullPath" .tar.xz)
	
	# delete the file
	rm $fullName
	
	# on the decompressed file run the two python scripts - fix and expand
	python3 /home/gil/Arduino/thrmal_detect_boiling_wifi/helpers/convert_alomst_json_to_fixed.py "$fileName".json
	python3 /home/gil/Arduino/thrmal_detect_boiling_wifi/helpers/convert_json_to_expanded.py "$fileName"_fixed.json

	# delete intermediate files	
	rm "$fileName".json "$fileName"_fixed.json
done


