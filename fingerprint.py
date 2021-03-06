import re  # regular expression packet
import numpy
import scipy.stats as st
import math
import re

import csv
import codecs
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

data = {}

with open('fingerprint_data.csv', mode='rb') as f:
    f_csv = csv.reader(codecs.iterdecode(f, 'utf-8'))
    for row in f_csv:
        deviceId = re.sub("\D", "", row[0].strip())
        # high support for annbor
        if deviceId not in ['90', '10129', '10131', '10133', '10134', '10137', '10154', '10155', '10158', '10160',
                            '10177']:
            continue
        # high support for vertical
        # if deviceId not in ['90','501','10131','10138','10140','10150','10164','10176','10574','10587','10612','10616','15101','17101','17102','17103']:
        #    continue
        # high support for straight
        # if deviceId not in ['10146','13103','10610','10607','10587','10188','10146','502','10137','10161','10602','10605']:
        #    continue
        # high support for plymonth
        # if deviceId not in ['10141','10207','10594','13103','13107','13108']:
        #    continue
        # high support for oneTry
        # if deviceId not in ['10141','10163','10188','10207','10567','10570','10594']:
        #    continue
        # high support for oneTry1
        # if deviceId not in ['10141','10163','10188','10207','10515','10567','10570','10594','10612','13101','13103','13105','13107','13108','13109']:
        #    continue
        # high support for oneTry0-7200
        # if deviceId not in ['10141','10163','10188','10207','10515','10567','10570','10594','10612','13101','13103','13105','13107','13108','13109']:
        #    continue

        tripId = row[1].strip()
        if deviceId not in data:
            data[deviceId] = {}

        if tripId not in data[deviceId]:
            data[deviceId][tripId] = [[], [], [], [], []]
        data[deviceId][tripId][0].append(float(row[3].strip()))  # 60
        data[deviceId][tripId][1].append(float(row[8].strip()))  # 72
        data[deviceId][tripId][2].append(float(row[20].strip()))  # 39
        data[deviceId][tripId][3].append(float(row[21].strip()))  # 38
        data[deviceId][tripId][4].append(float(row[22].strip()))  # 63
        '''
        if not data[deviceId].has_key(tripId):
            data[deviceId][tripId]=[[]]
        data[deviceId][tripId][0].append(float(row[22].strip()))  # 60
        '''
        # data[deviceId][tripId][0].append(float(row[11].strip())) # 29

# print data.keys()
lookup = {}
######################
# index:
# 0: Device id
# 1: Trip id
# 2: Time
# 3: AccelPadal # 60 #32
# 7: Ax #43
# 8: Ay #72
# 9: BounderyLeft #29
# 10: BounderyRight  #41
# 11: Brake #29
# 20: Speed # 39
# 21: TurnSignal # 38
# 22: YawRate # 63
######################


dataX = []
dataY = []
# print type(data['10177'][0])
for deviceId in data:
    if len(data[deviceId]) < 10:
        continue
    for tripId in data[deviceId]:
        dataY.append(deviceId)
        tmpArr = []
        dataArr = data[deviceId][tripId]
        for i in range(len(dataArr)):
            narray = numpy.array(dataArr[i])
            N = len(dataArr[i])
            sum1 = narray.sum()
            narray2 = narray * narray
            sum2 = narray2.sum()
            mean = sum1 / N
            tmpArr.append(mean)
            tmpArr.append(math.sqrt(abs(sum2 / N)))
            tmpArr.append(min(dataArr[i]))
            tmpArr.append(max(dataArr[i]))
            tmpArr.append(st.skew(narray))
            tmpArr.append(st.kurtosis(narray))
        dataX.append(tmpArr)
print("ok")
'''
fileout = open("./annborPredictTable1_original", "w")

for d in dataNew:
    strout = ""
    strout += str(d[0])
    strout += ' '
    for i in range(1, len(d)):
        strout += str(i) + ":" + str(d[i]) + " "
    strout += "\n"
    fileout.write(strout)
fileout.close()
'''


x_train, x_test, y_train, y_test = train_test_split(dataX, dataY, test_size=0.75, random_state=11)
clf = RandomForestClassifier(n_estimators=200, criterion='entropy')
clf.fit(x_train, y_train)
y_pred = clf.predict(x_test)

# map predictions to a number for use in the privacy check test
pred_map = {'90': 0, '10129': 1, '10131': 2, '10133': 3, '10134': 4, '10137': 5, '10154': 6, '10155': 7, '10158': 8, '10160': 9, '10177': 10}
with open('fingerprints.txt', 'w') as predictions_file:
    for pred in y_pred:
        print(pred_map[str(pred)], file=predictions_file)

print('Classification report:')
print(classification_report(y_test, y_pred))
