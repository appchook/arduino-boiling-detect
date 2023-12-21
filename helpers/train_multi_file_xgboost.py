import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # avoid warning ' This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.' 

import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error as MSE 
from sklearn.metrics import mean_squared_log_error
from file_to_features import file_to_features, createFeatures

import numpy as np
import matplotlib.pyplot as plt
import sys


if len(sys.argv) < 2:
    print("missing input file")
    #sys.exit()
    #inFile = "json_fixed_expanded.json"
    inFiles = ["3_expanded.json", "12_fixed_expanded.json", "15_fixed_expanded.json"]
else:
    inFiles = sys.argv[1:] # best to run: python3 train_multi_file_xgboost.py train-data/*.json

single = len(inFiles) == 1

def myConcat(ar1, ar2):
    if ar1 is None:
        return ar2
    else:
        return np.concatenate((ar1, ar2), axis=0)

x_arr = None
avg_time_arr = None
for inFile in inFiles:
    (single_x_arr, single_avg_time_arr), (orig_time_arr, temp_arr) = file_to_features(inFile)
    x_arr = myConcat(x_arr, single_x_arr)
    avg_time_arr = myConcat(avg_time_arr, single_avg_time_arr)

if single:
    for i in range(len(x_arr[0])):
        plt.scatter(x_arr[:,[i]], avg_time_arr)
    plt.show()

print("after hacking and consolidating:")
print(x_arr.shape)
print(avg_time_arr.shape)

x_tr, x_ts, y_tr, y_ts = train_test_split(x_arr, avg_time_arr, test_size = 0.5, random_state=42, shuffle=True)
# x_tr = x_arr
# y_tr = avg_time_arr

# Instantiation 
regressor=xgb.XGBRegressor(eval_metric='rmse') # rmsle

# set up our search grid
param_grid = {"max_depth":    [3, 4, 5, 6, 7],
              "n_estimators": [400, 500, 600, 700, 800],
              "learning_rate": [0.007, 0.01, 0.015, 0.02]}

# try out every combination of the above values
search = GridSearchCV(regressor, param_grid, cv=5, verbose=2).fit(x_tr, y_tr)

print("The best hyperparameters are ",search.best_params_)

regressor=xgb.XGBRegressor(learning_rate = search.best_params_["learning_rate"],
                           n_estimators  = search.best_params_["n_estimators"],
                           max_depth     = search.best_params_["max_depth"],
                           eval_metric='rmse') # rmsle

# Fitting the model 
regressor.fit(x_tr, y_tr) 
  
# Predict the model 
pred = regressor.predict(x_ts) 

# RMSE Computation 
rmse = np.sqrt(MSE(y_ts, pred)) 
print("RMSE : % f" %(rmse)) 

# RMSLE = np.sqrt( mean_squared_log_error(y_ts, pred) )
# print("RMSLE : %.5f" % RMSLE )

regressor.save_model("xgb-boiler-model.json")

for inFile in inFiles:
    (x_arr, avg_time_arr), (orig_time_arr, temp_arr) = file_to_features(inFile)
    plt.clf()
    pred = []
    pred_temp = []
    my_xs = []
    for i in range(1, 100):
        idx = int(i*(len(temp_arr)/100))
        if(idx < 20 or idx > len(temp_arr) - 20):
            continue
        my_x = createFeatures(idx, temp_arr, 20, 20)#[None,:]
        my_xs.append(my_x)
        #print(my_x.shape)
        #model.predict(my_x)
        pred_temp.append(temp_arr[idx])

    my_xs = np.array(my_xs)
    #print(my_xs.shape)
    pred = regressor.predict(my_xs)
    #print(pred.shape)

    plt.scatter(temp_arr, orig_time_arr)
    plt.scatter(pred_temp, pred)
    outFile = os.path.splitext(inFile)[0]+".png"
    plt.savefig(outFile)

if single:
    tst = x_arr[1,None]
    print(tst.shape)
    pred = regressor.predict(tst)
    print("prediction: ", pred)

    plt.clf()
    pred = []
    pred_temp = []
    my_xs = []
    for i in range(1, 100):
        idx = int(i*(len(temp_arr)/100))
        if(idx < 20 or idx > len(temp_arr) - 20):
            continue
        my_x = createFeatures(idx, temp_arr, 20, 20)#[None,:]
        my_xs.append(my_x)
        #print(my_x.shape)
        #model.predict(my_x)
        pred_temp.append(temp_arr[idx])

    my_xs = np.array(my_xs)
    #print(my_xs.shape)
    pred = regressor.predict(my_xs)
    #print(pred.shape)

    plt.scatter(temp_arr, orig_time_arr)
    plt.scatter(pred_temp, pred)
    plt.show()



