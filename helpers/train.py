import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # avoid warning ' This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.' 

import tensorflow as tf
from sklearn.model_selection import train_test_split
from file_to_features import file_to_features, createFeatures

import numpy as np
import matplotlib.pyplot as plt
import sys

def clean_outliers(time_arr, temp_arr, min, max):
    ret_time_arr = []
    ret_temp_arr = []
    for time,temp in zip(time_arr, temp_arr):
        if(temp < max and temp > min):
            ret_time_arr.append(time)
            ret_temp_arr.append(temp)
    return np.array(ret_time_arr)[:,None], np.array(ret_temp_arr,None)[:,None]

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
    #inFile = "json_fixed_expanded.json"
    inFile = "3_expanded.json"
else:
    inFile = sys.argv[1]

(x_arr, avg_time_arr), (orig_time_arr, temp_arr) = file_to_features(inFile)

#sums = temp_diff_arr[:,[20]]
#vars = temp_diff_arr[:,[21]]
#plt.scatter(sums, avg_time_arr)
for i in range(len(x_arr[0])):
    plt.scatter(x_arr[:,[i]], avg_time_arr)

plt.show()

print("after hacking and consolidating:")
print(x_arr.shape)
print(avg_time_arr.shape)

# norm_l = tf.keras.layers.Normalization(axis=-1)
# norm_l.adapt(x_arr)  # learns mean, variance
# x_arr = norm_l(x_arr)


# ds = tf.data.Dataset.zip((tf.data.Dataset.from_tensor_slices(time_arr), 
#                           tf.data.Dataset.from_tensor_slices(temp_diff_arr)))

# ds = tf.data.Dataset.from_tensor_slices((x_arr[:,None], avg_time_arr))

# train_ds, val_ds, test_ds = get_dataset_partitions_tf(ds, int(tf.data.experimental.cardinality(ds)))

# x_tr, x_ts, y_tr, y_ts = train_test_split(x_arr, avg_time_arr, test_size = 0.2, random_state=42, shuffle=True)
x_tr = x_arr
y_tr = avg_time_arr

tf.random.set_seed(42)

# Create a model using the Sequential API
model = tf.keras.Sequential([
  tf.keras.Input(shape=(3,)),
  #tf.keras.layers.Dense(10, activation='sigmoid'),
  tf.keras.layers.Dense(3, activation= tf.keras.activations.relu),
  tf.keras.layers.Dense(1, activation= tf.keras.activations.linear)
])

model.summary()

# Compile the model
model.compile(loss=tf.keras.losses.mae, # mae is short for mean absolute error
              #optimizer=tf.keras.optimizers.SGD(), # SGD is short for stochastic gradient descent
              optimizer=tf.keras.optimizers.Adam(learning_rate=0.1)
              #metrics=["mae"]
              )  

# Fit the model
# model.fit(X, y, epochs=5) # this will break with TensorFlow 2.7.0+
#model.fit(x_arr, avg_time_arr, epochs=100)
model.fit(x_tr, y_tr, epochs=100)
#model.fit(ds, epochs=50)

model.save('boiler_model.keras')

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



