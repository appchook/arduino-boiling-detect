import os
import xgboost as xgb
from file_to_features import last_features

import sys
import time



if len(sys.argv) < 2:
    print("missing input file")
    #sys.exit()
    #inFile = "json_fixed_expanded.json"
    inFile = "3_half.json"
else:
    inFile = sys.argv[1]

outFile = None
if len(sys.argv) > 2:
    outFile = sys.argv[2]

regressor=xgb.XGBRegressor(eval_metric='rmse') # rmsle

regressor.load_model("xgb-boiler-model.json")

def predict():
    #(x_arr, _), _ = file_to_features(inFile)
    x_arr = last_features(inFile)
    if x_arr is None:
        predStr = "-1"
    else:
        tst = x_arr[None,:] 
        print(tst.shape)
        pred = regressor.predict(tst)
        print("prediction: ", pred)
        predStr = str(pred[0][0])

    if outFile != None:
        with open(outFile, "w") as outfile:
            outfile.write(predStr)

prev_stamp = 0
while(True):
    time.sleep(1)
    stamp = os.stat(inFile).st_mtime
    if stamp != prev_stamp:
        prev_stamp = stamp
        predict()