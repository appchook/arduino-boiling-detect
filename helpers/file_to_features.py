import numpy as np
#import matplotlib.pyplot as plt
import json
#import sys

HACK_COUNT = 20
HACK_FAR_BACK = 20

def hackArray(arr, count):
    ret = []
    for i in range(0, len(arr) - count):
        a = arr[i:i+count]
        ret.append(a)
    return np.array(ret)

def getDiffFromAvg(arr, i, count, idxForAvg):    
    if idxForAvg < 0:
        return None
    a = arr[idxForAvg:idxForAvg+count]
    prevAvg = np.average(a)
    return arr[i:i+count] - prevAvg

# def hackArrayAddStats(arr, count):
#     ret = []
#     firstTemp = 0
#     for i in range(0, len(arr) - count):
#         a = arr[i:i+count]
#         dif = np.diff(a)
#         dif2 = [1/v for v in dif]
#         b = np.array([np.sum(dif), np.var(a), np.var(dif), np.sum(np.cumsum(dif)), np.sum(dif2), np.var(dif2), np.sum(np.cumsum(dif2))])[:,None]
#         ret.append(b)
#     return np.array(ret)

def createFeatures(i, tempArr, timeArr, count, avgFarBack):
    diffFromFromAvg = getDiffFromAvg(tempArr, i, count, i-avgFarBack)
    if diffFromFromAvg is None:
        return None
    curAvg = np.average(tempArr[i:i+count])
    diffLastFromFirst = tempArr[i+count] - tempArr[i]
    tempDelta = tempArr[i] - tempArr[0]
    timeDelta = timeArr[i] - timeArr[0]

    return np.array([np.sum(diffFromFromAvg), np.var(diffFromFromAvg), np.sum(np.cumsum(diffFromFromAvg)), curAvg, diffLastFromFirst, tempDelta, timeDelta])#[:,None]

def hackArrayAddStatsWithAvg(tempArr, timeArr, count, avgFarBack):
    ret = []    
    for i in range(0, len(tempArr) - count):
        b = createFeatures(i, tempArr, timeArr, count, avgFarBack)
        if b is None:
            continue

        ret.append(b)
    return np.array(ret)

def last_features(inFile):
    print("reading", inFile)
    with open(inFile) as f:    
        jdata = json.load(f)

    temp_arr = np.array([ent["temp"] for ent in jdata])
    if(len(temp_arr) < HACK_COUNT):
        return None
    
    last_time = jdata[-1]["time"]
    time_arr = np.array([last_time - ent["time"] for ent in jdata])

    features = createFeatures(len(temp_arr)-HACK_COUNT-1, temp_arr, time_arr, HACK_COUNT, HACK_FAR_BACK)
    return features


def findBoilingTempIdx(temp_arr):
    # a=hackArray(temp_arr,20)
    # d = np.diff(a)
    # sums=np.cumsum(d,axis=1)
    # print(a)
    # print(d)
    # print(sums)
    count = HACK_COUNT
    avgFarBack = HACK_FAR_BACK
    boilingIdx = None
    lastBoilingIdx = None
    for i in range(0, len(temp_arr) - count):
        diffs = getDiffFromAvg(temp_arr, i, count, i-avgFarBack)
        if diffs is None:
            continue
        s = np.sum(diffs)
        if(s < 1 and boilingIdx is None):
            boilingIdx = i
            lastBoilingIdx = boilingIdx
            print("boiling index is",i)
        if(s > 1.5 and boilingIdx is not None):
            boilingIdx = None
            print("boiling reset at",i)    
    return lastBoilingIdx

def file_to_features(inFile):
    print("reading", inFile)
    with open(inFile) as f:    
        jdata = json.load(f)

    temp_arr = np.array([ent["temp"] for ent in jdata])
    boilingIdx = findBoilingTempIdx(temp_arr)    
    
    if(boilingIdx is None):
        print("Err: boiling idx not found!")
        boilingIdx = len(temp_arr)-1
    
    last_time = jdata[boilingIdx]["time"]
    time_arr = np.array([max(last_time - ent["time"],0) for ent in jdata])
    orig_time_arr = time_arr

    # just to make easier to debug
    # time_arr = time_arr[0:10]
    # temp_arr = temp_arr[0:10]

    # temp_diff_arr = np.diff(temp_arr, prepend=np.array([0]))

    # time_arr, temp_diff_arr = clean_outliers(time_arr, temp_diff_arr, -10, 10)

    # plt.scatter(temp_diff_arr, time_arr)
    # plt.show()

    print(time_arr.shape)

    time_arr = hackArray(time_arr,HACK_COUNT)
    time_arr = time_arr.squeeze()
    avg_time_arr = np.average(time_arr, axis=1)[:,None]

    #x_arr = hackArrayAddStats(temp_arr, 10)
    x_arr = hackArrayAddStatsWithAvg(temp_arr, orig_time_arr, HACK_COUNT, HACK_FAR_BACK)
    #x_arr = x_arr.squeeze()

    avg_time_arr = avg_time_arr[len(avg_time_arr) - len(x_arr):]

    # print(time_arr)
    # print(x_arr)

    return(x_arr, avg_time_arr), (orig_time_arr, temp_arr)