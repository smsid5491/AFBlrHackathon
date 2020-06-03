# Detect if a person is weaaring mask or not

# importing packages
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from imutils.video import VideoStream
from twilio.rest import Client
import configparser
import numpy as np
import argparse
import imutils
import time
import cv2
import os

#Function to detect if a person is wearing mask or not
def mask_or_no_mask(videoFrame, faceDetector, maskDetector):
	(height, width) = videoFrame.shape[:2]
	blob = cv2.dnn.blobFromImage(videoFrame, 1.0, (300, 300),
		(104.0, 177.0, 123.0))

	faceDetector.setInput(blob)
	detections = faceDetector.forward()

	faces = []
	coordinates = []
	probabilities = []

	for i in range(0, detections.shape[2]):
		actualFaceProbability = detections[0, 0, i, 2]

		if actualFaceProbability > 0.5:
			box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
			(startX, startY, endX, endY) = box.astype("int")

			(startX, startY) = (max(0, startX), max(0, startY))
			(endX, endY) = (min(width - 1, endX), min(height - 1, endY))

			face = videoFrame[startY:endY, startX:endX]
			face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
			face = cv2.resize(face, (224, 224))
			face = img_to_array(face)
			face = preprocess_input(face)
			face = np.expand_dims(face, axis=0)
			faces.append(face)
			coordinates.append((startX, startY, endX, endY))

	if len(faces) > 0:
		for face in faces:
			probabilities.append(maskDetector.predict(face))

	return (coordinates, probabilities)

prototxtPath = os.path.sep.join(["face_detector", "deploy.prototxt"])
weightsPath = os.path.sep.join(["face_detector",
	"res10_300x300_ssd_iter_140000.caffemodel"])
faceDetector = cv2.dnn.readNet(prototxtPath, weightsPath)

maskDetector = load_model("mask_detector.model")

vs = VideoStream(src=0).start()
time.sleep(2.0)

config = configparser.ConfigParser()
config.read('config.ini')

account_sid = config['twilio']['accountSid']
auth_token = config['twilio']['authToken']
client = Client(account_sid, auth_token)
showSuccess = False

while True:
	videoFrame = vs.read()
	videoFrame = imutils.resize(videoFrame, width=500)
	cv2.putText(videoFrame, config['common']['closeWindowMessage'], (110, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (255, 0, 0), 1)
	if showSuccess:
		cv2.putText(videoFrame, config['common']['successMessage'], (50, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

	(coordinates, probabilities) = mask_or_no_mask(videoFrame, faceDetector, maskDetector)

	negativeFaces = []
	for i in range(0, len(coordinates)):
		(startX, startY, endX, endY) = coordinates[i]
		(maskPositive, maskNegative) = probabilities[i][0]

		if maskNegative > 0.90:
			prob = maskNegative * 100
			cv2.putText(videoFrame, config['common']['sendWhatsAppMessage'], (70, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 0, 255), 1)
			cv2.putText(videoFrame, "Not Wearing Mask", (startX, startY - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1)
			cv2.rectangle(videoFrame, (startX, startY), (endX+5, endY+5), (0, 0, 255), 1)
			negativefaceExtract = videoFrame[startY-20:endY+20, startX-20:endX+20]
			fileName = str(i)
			negativeFaces.append(negativefaceExtract)
		else:
			cv2.putText(videoFrame, "Wearing Mask", (startX, startY - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
			cv2.rectangle(videoFrame, (startX, startY), (endX+5, endY+5), (0, 255, 0), 1)

	cv2.imshow("Frame", videoFrame)
	key = cv2.waitKey(1) & 0xFF

	if key == ord(config['common']['sendkey']):
		if len(negativeFaces) > 0:
			for i in range(0, len(negativeFaces)):
				fileName = str(i)+".jpg"
				cv2.imwrite(fileName, negativeFaces[i])
				url = config['twilio']['url']+fileName
				message = client.messages.create(
					media_url=[url],
					from_=config['twilio']['from'],
					body=config['twilio']['body'],
					to=config['twilio']['to']
				)
				showSuccess = True
		cv2.putText(videoFrame, config['common']['successMessage'], (70, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 5)
	if key == ord(config['common']['okKey']):
		showSuccess = False
	if key == ord(config['common']['exitKey']):
		break

cv2.destroyAllWindows()
vs.stop()