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
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

#CHANGE THESE AS NEEDED
##################################
numDCTFeatures = 10
dctFeaturesFlag = 1
envFeaturesFlag = 1
physFeaturesFlag = 1
numFeaturesToSelect = 13
mRMRType = "MIQ"			#Has to be "MIQ" or "MID"
testTrainSplit = 0.3		#Default is 0.3
kernel = "linear"			#Default is linear, can be "linear", "poly", "rbf", "sigmoid"
numberOfRuns = 50			#Default it 50
##################################

names = ['GraceSpecsNew', 'MarcSpecsNew', 'PeteSpecsNew', 'CharlesSpecsNew']
subDirs = ['fallingSitting', 'fallingStanding', 'fallingWalking', 'Movement', 'Sitting', 'Walking']

#get filenames for data
path = "../../../ECE_Senior_Design_Our_Data"
fallingSittingFiles = []
fallingStandingFiles = []
fallingWalkingFiles = []
movementFiles = []
sittingFiles = []
walkingFiles = []

for name in names:
	fallingSittingFiles = fallingSittingFiles + [(path + "/"  + name + "/" + subDirs[0] + "/" + f) for f in listdir(join(path, name, subDirs[0])) if isfile(join(path, name, subDirs[0], f))]
	fallingStandingFiles = fallingStandingFiles + [(path + "/"  + name + "/" + subDirs[1] + "/" + f) for f in listdir(join(path, name, subDirs[1])) if isfile(join(path, name, subDirs[1], f))]
	fallingWalkingFiles = fallingWalkingFiles + [(path + "/"  + name + "/" + subDirs[2] + "/" + f) for f in listdir(join(path, name, subDirs[2])) if isfile(join(path, name, subDirs[2], f))]
	movementFiles = movementFiles + [(path + "/"  + name + "/" + subDirs[3] + "/" + f) for f in listdir(join(path, name, subDirs[3])) if isfile(join(path, name, subDirs[3], f))]
	sittingFiles = sittingFiles + [(path + "/"  + name + "/" + subDirs[4] + "/" + f) for f in listdir(join(path, name, subDirs[4])) if isfile(join(path, name, subDirs[4], f))]
	walkingFiles = walkingFiles + [(path + "/"  + name + "/" + subDirs[5] + "/" + f) for f in listdir(join(path, name, subDirs[5])) if isfile(join(path, name, subDirs[5], f))]


#get spectrograms and get features from spectrograms
eng = matlab.engine.start_matlab()
fallingSittingData = []
fallingStandingData = []
fallingWalkingData = []
movementData = []
sittingData = []
walkingData = []

for file in fallingSittingFiles:
	fallingSittingData.append(numpy.array(eng.spectrogramToFeatures(file, dctFeaturesFlag, envFeaturesFlag, physFeaturesFlag, numDCTFeatures)).tolist())

for file in fallingStandingFiles:
	fallingStandingData.append(numpy.array(eng.spectrogramToFeatures(file, dctFeaturesFlag, envFeaturesFlag, physFeaturesFlag, numDCTFeatures)).tolist())
    
for file in fallingWalkingFiles:
	fallingWalkingData.append(numpy.array(eng.spectrogramToFeatures(file, dctFeaturesFlag, envFeaturesFlag, physFeaturesFlag, numDCTFeatures)).tolist())

for file in movementFiles:
	movementData.append(numpy.array(eng.spectrogramToFeatures(file, dctFeaturesFlag, envFeaturesFlag, physFeaturesFlag, numDCTFeatures)).tolist())
    
for file in sittingFiles:
	sittingData.append(numpy.array(eng.spectrogramToFeatures(file, dctFeaturesFlag, envFeaturesFlag, physFeaturesFlag, numDCTFeatures)).tolist())

for file in walkingFiles:
	walkingData.append(numpy.array(eng.spectrogramToFeatures(file, dctFeaturesFlag, envFeaturesFlag, physFeaturesFlag, numDCTFeatures)).tolist())
    
eng.quit()    
  

#Fixing data. Was [[[list], [list]]] now is [[list], [list]]
fallingSittingData = [item for sublist in fallingSittingData for item in sublist]
fallingStandingData = [item for sublist in fallingStandingData for item in sublist]
fallingWalkingData = [item for sublist in fallingWalkingData for item in sublist]
movementData = [item for sublist in movementData for item in sublist]
sittingData = [item for sublist in sittingData for item in sublist]
walkingData = [item for sublist in walkingData for item in sublist]

#combine to form all data
allData = fallingSittingData + fallingStandingData + fallingWalkingData + movementData + sittingData + walkingData

#make classification list
results = [0] * len(fallingSittingData) + [1] * len(fallingStandingData) + [2] * len(fallingWalkingData) + [3] * len(movementData) + [4] * len(sittingData) + [5] * len(walkingData)

#find total number of features
numFeatures = 0
if dctFeaturesFlag == 1:
	numFeatures = numFeatures + numDCTFeatures
if envFeaturesFlag == 1:
	numFeatures = numFeatures + 7
if physFeaturesFlag == 1:
	numFeatures = numFeatures + 4

#prepare data for feature selection
numpyArrayofArrays = numpy.array([numpy.array(xi) for xi in allData])
colNames = []
for i in range(numFeatures):
	colNames.append(str(i))
kernels = ["poly", "rbf", "sigmoid"]
nums = [1,2,3,4,5,6,7,8,9,10,11,12,13]
array2d = []
for j in kernels:
	for k in nums:
		totalF1 = 0
		totalAcc = 0
		df = pandas.DataFrame(data = numpyArrayofArrays, index = None, columns = colNames)
		#improved feature selection using mRMR
		returned = pymrmr.mRMR(df, mRMRType, nums[k-1])
		returnedInts = [int(i) for i in returned]

		df.insert(numFeatures, "Classes", results)
		for i in range(numberOfRuns):
			#get data after feature selected
			dfFeatureSelectedData = df[df.columns[returnedInts]]
			dfFeatureSelectedResults = results
			#Split test and training sets
			allDataTrain, allDataTest, resultTrain, resultTest = train_test_split(dfFeatureSelectedData, dfFeatureSelectedResults, test_size = testTrainSplit)

			#Train algorithm
			if (kernel == "poly"):
				classifier = SVC(kernel=j, degree=3)
			elif (kernel == "rbf"):
				classifier = SVC(kernel='rbf', gamma=0.7)
			elif (kernel == "sigmoid"):
				classifier = SVC(kernel = 'sigmoid', gamma=2)
			else:
				classifier = SVC(kernel=j)

			classifier.fit(allDataTrain, resultTrain)

			#Make predictions
			predictions = list(classifier.predict(allDataTest))
			resultTest = list(resultTest)

			totalF1 = totalF1 + sklearn.metrics.f1_score(resultTest, predictions, average = 'weighted')
			totalAcc = totalAcc + sklearn.metrics.accuracy_score(resultTest, predictions)
		array = [str(k), str(returnedInts), str(totalF1/numberOfRuns), str(totalAcc/numberOfRuns)]
		print(array)
		array2d.append(array)


print(array2d)
dfArray2d = pandas.DataFrame(array2d)
dfArray2d.to_csv("test.csv", index = False, header = False)