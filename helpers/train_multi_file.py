import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # avoid warning ' This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.' 

import tensorflow as tf
from sklearn.model_selection import train_test_split
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
    inFiles = sys.argv[1:]

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

x_tr, x_ts, y_tr, y_ts = train_test_split(x_arr, avg_time_arr, test_size = 0.2, random_state=42, shuffle=True)
x_tr = x_arr
y_tr = avg_time_arr

tf.random.set_seed(42)

# Create a model using the Sequential API
model = tf.keras.Sequential([
  tf.keras.Input(shape=(5,)),
  #tf.keras.layers.Dense(10, activation='sigmoid'),
  tf.keras.layers.Dense(5, activation= tf.keras.activations.relu),
  tf.keras.layers.Dense(3, activation= tf.keras.activations.relu),
  tf.keras.layers.Dense(1, activation= tf.keras.activations.linear)
])

model.summary()

# Compile the model
model.compile(loss=tf.keras.losses.mse, # mae is short for mean absolute error
              #optimizer=tf.keras.optimizers.SGD(), # SGD is short for stochastic gradient descent
              optimizer=tf.keras.optimizers.Adam(learning_rate=0.1)
              #metrics=["mae"]
              )  

# Fit the model
# model.fit(X, y, epochs=5) # this will break with TensorFlow 2.7.0+
#model.fit(x_arr, avg_time_arr, epochs=100)
model.fit(x_tr, y_tr, epochs=120)
#model.fit(ds, epochs=50)

model.save('boiler_model.keras')

score = model.evaluate(x_ts, y_ts)
print("model score:", score)

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
    pred = model.predict(my_xs)
    #print(pred.shape)

    plt.scatter(temp_arr, orig_time_arr)
    plt.scatter(pred_temp, pred)
    outFile = os.path.splitext(inFile)[0]+".png"
    plt.savefig(outFile)

if single:
    tst = x_arr[1,None]
    print(tst.shape)
    pred = model.predict(tst)
    print("prediction: ", pred)

    plt.clf()
    pred = []
    pred_temp = []
    my_xs = []
    for i in range(1, 100):
        idx = int(i*(len(temp_arr)/100))
        if(idx < 20):
            continue
        my_x = createFeatures(idx, temp_arr, 20, 20)#[None,:]
        my_xs.append(my_x)
        #print(my_x.shape)
        #model.predict(my_x)
        pred_temp.append(temp_arr[idx])

    my_xs = np.array(my_xs)
    #print(my_xs.shape)
    pred = model.predict(my_xs)
    #print(pred.shape)

    plt.scatter(temp_arr, orig_time_arr)
    plt.scatter(pred_temp, pred)
    plt.show()



