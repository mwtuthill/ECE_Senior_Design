import sys
import os
import matlab.engine
import sklearn.metrics
import numpy
import joblib
import pandas
import pymrmr
import time

from os import listdir
from os.path import isfile, join
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix

#get filenames for data
names = ['Grace', 'Marc', 'Pete']
fallSubdirs = ['fallingSitting', 'fallingStanding', 'fallingWalking']
nonFallSubdirs = ['Movement', 'Sitting', 'Walking']

#get filenames for data
path = "../../../ECE_Senior_Design_Our_Data"
fallFiles = []
nonFallFiles = []
for name in names:
	for fallDir in fallSubdirs:
		fallFiles = fallFiles + [(path + "/"  + name + "/" + fallDir + "/" + f) for f in listdir(join(path, name, fallDir)) if isfile(join(path, name, fallDir, f))]
	for nonFallDir in nonFallSubdirs:
		nonFallFiles = nonFallFiles + [(path + "/"  + name + "/" + nonFallDir + "/" + f) for f in listdir(join(path, name, nonFallDir)) if isfile(join(path, name, nonFallDir, f))]

#get spectrograms and get features from spectrograms
eng = matlab.engine.start_matlab()
fallData = []
nonFallData = []

for file in nonFallFiles:
	print(file)
	outfile = 'out_' + str(int(round(time.time() * 1000))) + '.png'
	nonFallData.append(numpy.array(eng.binToDct(file, outfile)).tolist())
for file in fallFiles:
	print(file)
	outfile = 'out_' + str(int(round(time.time() * 1000))) + '.png'
	fallData.append(numpy.array(eng.binToDct(file, outfile)).tolist())
    

eng.quit()    

#Fixing data. Was [[[list], [list]]] now is [[list], [list]]
nonFallData = [item for sublist in nonFallData for item in sublist]
fallData = [item for sublist in fallData for item in sublist]

#combine to form all data
allData = nonFallData + fallData

#make classification list
results = [0] * len(nonFallData) + [1] * len(fallData)
print(results)

#feature selection (keep 3 of 10 features)
#prepare data for feature selection
numpyArrayofArrays = numpy.array([numpy.array(xi) for xi in allData])
colNames = []
for i in range(500):
	colNames.append(str(i))
df = pandas.DataFrame(data = numpyArrayofArrays, index = None, columns = colNames)
df.insert(0, "Classes", results)

print(df)

#improved feature selection using mRMR
returned = pymrmr.mRMR(df, "MID", 3)
returnedInts = [(int(i)+1) for i in returned]

#get data after feature selected
dfFeatureSelectedData = df[df.columns[returnedInts]]
dfFeatureSelectedResults = df[df.columns[0]]
print("Returned")
print(dfFeatureSelectedData)
print(dfFeatureSelectedResults)

#Split test and training sets
allDataTrain, allDataTest, resultTrain, resultTest = train_test_split(dfFeatureSelectedData, dfFeatureSelectedResults, test_size = 0.2)
print("Result Train")
print(resultTrain)

#Train algorithm
classifier = SVC(kernel='linear')
classifier.fit(allDataTrain, resultTrain)

#Make predictions
predictions = list(classifier.predict(allDataTest))
resultTest = list(resultTest)

print(predictions)
print(resultTest)

#show results
print(sklearn.metrics.f1_score(resultTest, predictions, average = 'binary'))