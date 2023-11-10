import tensorflow as tf
from file_to_features import file_to_features, createFeatures

import sys

if len(sys.argv) < 2:
    print("missing input file")
    #sys.exit()
    #inFile = "json_fixed_expanded.json"
    inFile = "3_half.json"
else:
    inFile = sys.argv[1]

if len(sys.argv) > 2:
    outFile = sys.argv[2]

model = tf.keras.models.load_model('my_model.keras')

(x_arr, _), _ = file_to_features(inFile)

tst = x_arr[-1,None]
print(tst.shape)
pred = model.predict(tst)
print("prediction: ", pred)

if outFile:
    with open(outFile, "w") as outfile:
        outfile.write(pred)

