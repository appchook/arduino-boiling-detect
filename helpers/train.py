import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # avoid warning ' This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.' 

import tensorflow as tf

import numpy as np
import matplotlib.pyplot as plt
import json
import sys

def clean_outliers(time_arr, temp_arr, min, max):
    ret_time_arr = []
    ret_temp_arr = []
    for time,temp in zip(time_arr, temp_arr):
        if(temp < max and temp > min):
            ret_time_arr.append(time)
            ret_temp_arr.append(temp)
    return np.array(ret_time_arr)[:,None], np.array(ret_temp_arr)[:,None]

def get_dataset_partitions_tf(ds, ds_size, train_split=0.8, val_split=0.1, test_split=0.1, shuffle=True, shuffle_size=10000):
    assert (train_split + test_split + val_split) == 1
    
    if shuffle:
        # Specify seed to always have the same split distribution between runs
        ds = ds.shuffle(shuffle_size, seed=12)
    
    train_size = int(train_split * ds_size)
    val_size = int(val_split * ds_size)
    
    train_ds = ds.take(train_size)    
    val_ds = ds.skip(train_size).take(val_size)
    test_ds = ds.skip(train_size).skip(val_size)
    
    return train_ds, val_ds, test_ds

if len(sys.argv) < 2:
    print("missing input file")
    #sys.exit()
    inFile = "json_fixed_expanded.json"
else:
    inFile = sys.argv[1]

print("reading", inFile)
with open(inFile) as f:    
    jdata = json.load(f)

time_arr = np.array([ent["time"] for ent in jdata])
temp_arr = np.array([ent["temp"] for ent in jdata])
temp_diff_arr = np.diff(temp_arr, prepend=np.array([0]))

time_arr, temp_diff_arr = clean_outliers(time_arr, temp_diff_arr, -10, 10)

print(temp_diff_arr.shape)

norm_l = tf.keras.layers.Normalization(axis=-1)
norm_l.adapt(temp_diff_arr)  # learns mean, variance
temp_diff_arr = norm_l(temp_diff_arr)

plt.scatter(time_arr, temp_diff_arr)
plt.show()

temp_diff_arr = np.reshape(temp_diff_arr, (-1,10))
time_arr = np.reshape(time_arr, (-1,10))
avg_time_arr = np.average(time_arr, axis=1)[:,None]

print("after consolidating:")
print(temp_diff_arr.shape)
print(avg_time_arr.shape)

# ds = tf.data.Dataset.zip((tf.data.Dataset.from_tensor_slices(time_arr), 
#                           tf.data.Dataset.from_tensor_slices(temp_diff_arr)))

ds = tf.data.Dataset.from_tensor_slices((temp_diff_arr, avg_time_arr))

train_ds, val_ds, test_ds = get_dataset_partitions_tf(ds, int(tf.data.experimental.cardinality(ds)))

tf.random.set_seed(42)

# Create a model using the Sequential API
model = tf.keras.Sequential([
  tf.keras.Input(shape=(10,)),
  tf.keras.layers.Dense(10, activation='relu'),
  tf.keras.layers.Dense(1, activation='relu')
])

model.summary()

# Compile the model
model.compile(loss=tf.keras.losses.mae, # mae is short for mean absolute error
              optimizer=tf.keras.optimizers.SGD(), # SGD is short for stochastic gradient descent
              metrics=["mae"]
              )

# Fit the model
# model.fit(X, y, epochs=5) # this will break with TensorFlow 2.7.0+
model.fit(temp_diff_arr, avg_time_arr, epochs=50)
# model.fit(train_ds, epochs=50)

print(temp_diff_arr[0,None].shape)
pred = model.predict(temp_diff_arr[0,None])
print("prediction: ", pred)
