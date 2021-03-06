# -*- coding: utf-8 -*-


# import os
# import pathlib
# import csv
import os

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
import pandas as pd
# import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.style.use('ggplot')
# import os
# import tensorflow as tf
# from tensorflow.python.client import device_lib
# from keras.models import load_model
# from sklearn.preprocessing import StandardScaler

df = pd.read_csv('driver_score_data.csv')


def substr(string, start, length=None):
    if start < 0:
        start = start + len(string)
    if not length:
        return string[start:]
    elif length > 0:
        return string[start:start + length]
    else:
        return string[start:length]


"extra functions I added"
import time
import datetime


def check_dateform(date_str):
    # 'debug'
    # print("check_dateform function called!")
    # old=date_str

    strings = date_str.split()
    if len(strings) == 2:
        flag = 0
        date = strings[0].split('-')
        time = strings[1].split(':')
        'check month'
        if len(date[0]) > 2:
            date[0] = date[0][-2:]
        if (date[1] == 'set'):
            date[1] = 'sep'

        'check time'
        for cnt in range(2):
            if len(time[cnt]) > 2:
                time[cnt] = time[cnt][-2:]
        min = time[2].split('.')
        if len(min[0]) > 2:
            min[0] = min[0][-2:]
            time[2] = '.'.join(min)

        strings[0] = '-'.join(date)
        strings[1] = ':'.join(time)
        date_str = ' '.join(strings)
        return flag, date_str
    else:
        if len(strings[4]) > 3:
            flag = 1
            strings[4] = strings[4][0:6] + strings[4][7:9]
            date_str = ' '.join(strings)
            return flag, date_str

        if len(strings[4]) == 3 and strings[4] == 'BRT':
            strings[4] = 'GMT-0300'
            date_str = ' '.join(strings)
            flag = 1
            return flag, date_str

        if len(strings[4]) == 3:
            flag = 2
            return flag, date_str

        # 'debug'
        # if old!=date_str:
        #   print('wrong format!!,returning',date_str)


def datestr2num(date_str):
    if date_str == '∞':
        return -1

    flag, date_str = check_dateform(date_str)
    if flag == 0:
        element = datetime.datetime.strptime(date_str, '%d-%b-%Y %H:%M:%S.%f')
    elif flag == 1:
        element = datetime.datetime.strptime(date_str, '%a %b %d %H:%M:%S %Z%z %Y')
    elif flag == 2:
        element = datetime.datetime.strptime(date_str, '%a %b %d %H:%M:%S %Z %Y')

    tuple = element.timetuple()
    timestamp = time.mktime(tuple)

    return timestamp


def pre_processing(df):
    goods_list = []
    for ind in df.index:
        tmp_list = []
        tmp_list.append(df['GPS_Speed_Km'][ind])
        tmp_list.append(datestr2num(df['Device_Time'][ind]))
        tmp_list.append(df['GPS_Long'][ind])
        tmp_list.append(df['GPS_Lat'][ind])
        tmp_list.append(df['OBD_Engine_RPM'][ind])
        tmp_list.append(datestr2num(df['Device_Time'][ind]) - datestr2num(df['Device_Time'][0]))
        goods_list.append(tmp_list)
    return goods_list


def driver_score(goods_list):
    # counters
    overSpeedCounter = 0
    overAccelCounter = 0
    hardBreakCounter = 0
    fullStopCounter = 0
    totalCounter = len(goods_list)
    max_speed = 0
    maxDrivingDuration = 0

    # Index
    TIMESTAMP = 1
    LATITUDE = 3
    LONGITUDE = 2
    RPM = 4
    SPEED = 0
    ENGINE_RUNTIME = 5
    # FUEL_ECONOMY = 26;

    # 0：last time status is increase;1: last time status is decrease; 3: even ; 4:over increase; 5:over decrese
    INCREASE = 0
    DECREASE = 1
    EVEN = 3
    OVER_INCREASE = 4
    OVER_DECREASE = 5

    # Boundary, this value should be get from the experiment
    AcceMax = 25
    # BreakMax = 28
    BreakMax = 25

    # Fule comsumption
    maxFuleComsmption = 0
    minFuleComsmption = 0
    avgFuleComsmption = 0

    # coordinate list
    fullStopCoList = []  # TODO: make sure its usage later
    hardBreakCoList = []
    overAccelCoList = []

    buff0 = goods_list[0]
    buff1 = goods_list[0]
    i = 0
    while i < totalCounter:
        if i > 0:
            if goods_list[i][SPEED] == 0.00 and goods_list[i - 1][SPEED] > 0:
                fullStopCounter = fullStopCounter + 1;
                # add Co to the list
                if goods_list[i][LATITUDE] != goods_list[i - 1][LATITUDE] or goods_list[i][LONGITUDE] != \
                        goods_list[i - 1][LONGITUDE]:
                    buff0 = goods_list[i - 1]
                    buff1 = goods_list[i]

                if goods_list[i][LATITUDE] == goods_list[i - 1][LATITUDE] and goods_list[i][LONGITUDE] == \
                        goods_list[i - 1][LONGITUDE]:
                    j = i
                    while j > 0:
                        if goods_list[i][LATITUDE] != goods_list[j][LATITUDE] or goods_list[i][LONGITUDE] != \
                                goods_list[j][LONGITUDE]:
                            buff0 = goods_list[j];
                            buff1 = goods_list[i];
                            break;
                        j -= 1

                fullStopCoList.append((buff0, buff1))
        i += 1

    flag = EVEN
    overAccelCo = []
    hardBreakCo = []
    i = 0
    while i < totalCounter - 2:
        # increase
        speed_next = goods_list[i + 1][SPEED]
        speed_curr = goods_list[i][SPEED]
        if speed_curr < speed_next and speed_next - speed_curr < AcceMax:
            # add $overAccelCo to the $overAccelCoList then clean $overAccelCo;
            if flag == OVER_DECREASE:
                hardBreakCoList.append(hardBreakCo)
                hardBreakCo = []
            # add $hardBreakCo to the $hardBreakCoList then clean $hardBreakCo;
            if flag == OVER_INCREASE:
                overAccelCoList.append(overAccelCo)
                overAccelCo = []

            flag = INCREASE

        # over increase
        if (speed_curr < speed_next):
            if speed_next - speed_curr > AcceMax and flag != OVER_INCREASE:
                overAccelCounter += 1

                # add $hardBreakCo to the $hardBreakCoList then clean $hardBreakCo;
                if flag == OVER_DECREASE:
                    hardBreakCoList.append(hardBreakCo)
                    hardBreakCo = []

                # add Co to the $overAccelCo
                if goods_list[i][LATITUDE] == goods_list[i + 1][LATITUDE] and goods_list[i][LONGITUDE] == \
                        goods_list[i + 1][LONGITUDE]:
                    j = i
                    while j < len(goods_list) - i:
                        if goods_list[i][LATITUDE] != goods_list[j][LATITUDE] or goods_list[i][LONGITUDE] != \
                                goods_list[j][LONGITUDE]:
                            overAccelCo.append(goods_list[i])
                            overAccelCo.append(goods_list[j])
                            break;
                        j += 1
                else:
                    overAccelCo.append(goods_list[i])
                    overAccelCo.append(goods_list[i + 1])
                flag = OVER_INCREASE

            if speed_next - speed_curr > AcceMax and flag == OVER_INCREASE:
                overAccelCo.append(goods_list[i + 1])

        # decrease
        if speed_curr > speed_next and speed_curr - speed_next < BreakMax:
            # add hardBreakCo to the hardBreakCoList then clean hardBreakCo
            if (flag == OVER_DECREASE):
                hardBreakCoList.append(hardBreakCo)
                hardBreakCo = []

            # add OverAccelCo to the OverAccelCoList then clean OverAccelCo
            if (flag == OVER_INCREASE):
                overAccelCoList.append(overAccelCo)
                overAccelCo = []

            flag = DECREASE

        # over decrease
        if speed_curr > speed_next:
            if speed_curr - speed_next > BreakMax and flag != OVER_DECREASE:
                hardBreakCounter += 1

                # add OverAccelCo to the OverAccelCoList then clean OverAccelCo
                if (flag == OVER_INCREASE):
                    overAccelCoList.append(overAccelCo)
                    overAccelCo = []

                # add Co to the $hardBreakCo
                if goods_list[i][LATITUDE] == goods_list[i + 1][LATITUDE] and goods_list[i][LONGITUDE] == \
                        goods_list[i + 1][LONGITUDE]:
                    j = i
                    while j < len(goods_list) - i:
                        if goods_list[i][LATITUDE] != goods_list[j][LATITUDE] or goods_list[i][LONGITUDE] != \
                                goods_list[j][LONGITUDE]:
                            hardBreakCo.append(goods_list[i])
                            hardBreakCo.append(goods_list[j])
                            break;
                        j += 1
                else:
                    hardBreakCo.append(goods_list[i])
                    hardBreakCo.append(goods_list[i + 1])
                flag = OVER_DECREASE

            if speed_curr - speed_next > BreakMax and flag == OVER_DECREASE:
                # add Co to the hardBreakCo
                hardBreakCo.append(goods_list[i + 1])

        # even
        if speed_curr == speed_next:
            # add hardBreakCo to the hardBreakCoList then clean hardBreakCo
            if (flag == OVER_DECREASE):
                hardBreakCoList.append(hardBreakCo)
                hardBreakCo = []

            # add OverAccelCo to the OverAccelCoList then clean OverAccelCo
            if (flag == OVER_INCREASE):
                overAccelCoList.append(overAccelCo)
                overAccelCo = []

            flag = EVEN

        i += 1

    return 100 - (hardBreakCounter * 2)  # driving_score


p_1 = df[df['Person_Id'] == 1]
p_1 = p_1.reset_index(drop=True)

p_2 = df[df['Person_Id'] == 2]
p_2 = p_2.reset_index(drop=True)

p_3 = df[df['Person_Id'] == 3]
p_3 = p_3.reset_index(drop=True)

p_4 = df[df['Person_Id'] == 4]
p_4 = p_4.reset_index(drop=True)

p_5 = df[df['Person_Id'] == 5]
p_5 = p_5.reset_index(drop=True)

p_6 = df[df['Person_Id'] == 6]
p_6 = p_6.reset_index(drop=True)

p_7 = df[df['Person_Id'] == 7]
p_7 = p_7.reset_index(drop=True)

p_8 = df[df['Person_Id'] == 8]
p_8 = p_8.reset_index(drop=True)

p_9 = df[df['Person_Id'] == 9]
p_9 = p_9.reset_index(drop=True)

p_10 = df[df['Person_Id'] == 10]
p_10 = p_10.reset_index(drop=True)

'Driving Score of Person 1'
goods_list_1 = pre_processing(p_1)
ds_1 = driver_score(goods_list_1)
print('Driving Score of Driver 1 is:', ds_1)

'Driving Score of Person 2'
goods_list_2 = pre_processing(p_2)
ds_2 = driver_score(goods_list_2)
print('Driving Score of Driver 2 is:', ds_2)

'Driving Score of Person 3'
goods_list_3 = pre_processing(p_3)
ds_3 = driver_score(goods_list_3)
print('Driving Score of Driver 3 is:', ds_3)

'Driving Score of Person 4'
goods_list_4 = pre_processing(p_4)
ds_4 = driver_score(goods_list_4)
print('Driving Score of Driver 4 is:', ds_4)

'Driving Score of Person 5'
goods_list_5 = pre_processing(p_5)
ds_5 = driver_score(goods_list_5)
print('Driving Score of Driver 5 is:', ds_5)

'Driving Score of Person 6'
goods_list_6 = pre_processing(p_6)
ds_6 = driver_score(goods_list_6)
print('Driving Score of Driver 6 is:', ds_6)

'Driving Score of Person 7'
goods_list_7 = pre_processing(p_7)
ds_7 = driver_score(goods_list_7)
print('Driving Score of Driver 7 is:', ds_7)

'Driving Score of Person 8'
goods_list_8 = pre_processing(p_8)
totalCounter = len(goods_list_8)
ds_8 = driver_score(goods_list_8)
print('Driving Score of Driver 8 is:', ds_8)

'Driving Score of Person 9'
goods_list_9 = pre_processing(p_9)
totalCounter = len(goods_list_9)
ds_9 = driver_score(goods_list_9)
print('Driving Score of Driver 9 is:', ds_9)

'Driving Score of Person 10'
goods_list_10 = pre_processing(p_10)
totalCounter = len(goods_list_10)
ds_10 = driver_score(goods_list_10)
print('Driving Score of Driver 10 is:', ds_10)

big_list = goods_list_1 + goods_list_2 + goods_list_3 + goods_list_4 + goods_list_5 + \
           goods_list_6 + goods_list_7 + goods_list_8 + goods_list_9 + goods_list_10
size = 10000
hop = 250
scores = []
for i in range(0, len(big_list) - size, hop):
    score = driver_score(big_list[i:i + size])
    scores.append(score)
with open('scores.txt', 'w') as scores_file:
    for s in scores:
        print(s, file=scores_file)
