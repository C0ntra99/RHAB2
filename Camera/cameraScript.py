#April 29 2018
#Matthew Harrison

'''
This program was written to be on a raspberry pie to take videos and pictures

Said Raspberry pie is to be part of 3 pie system that will be part of RHAB (Rose state Hot Air Balloon) <-- thats not right, I don't know what the accronym stands for, I'm dumb
'''
import time
import datetime
import picamera
from picamera import PiCamera, Color

now = datetime.datetime.now()

camera = picamera.PiCamera()

nowDate = str(now.month) + "-" + str(now.day) + "-" + str(now.year)
nowTime = str(now.hour) + ":" + str(now.minute) + ":" + str(now.second)
##Get with cool python socket SHIT WHICH FUCKING SUCKS GOD DAMNIT
pictureAltitude = "my ass"


def cameraTakePicture(imageResolutionWidth, imageResotutionLength, nameOfImage):
    camera.resolution = (imageResolutionWidth, imageResotutionLength)

    camera.start_preview()

    #This block is to add an annotation somewhere to the image, it includes the message, the size, and color of the annotation
    camera.annotate_text = "Date: " + nowDate + "\nTime: " + nowTime + "\nAltitude: " + pictureAltitude
    camera.annotate_text_size = 25
    #camera.annotate_background = Color('white')
    camera.annotate_foreground = Color('white')

    # this gives the camera time to adjust to light/ focus
    ##time.sleep(5)

    camera.capture(nameOfImage)

    camera.stop_preview()

    camera.close()




def cameraTakeVideo(videoResolutionWidth, videoResotutionLength, videoRecordTime, pathVideosWillBeSaved):
    camera.resolution = (videoResolutionWidth, videoResotutionLength)

    camera.start_preview()
    camera.start_recording(pathVideosWillBeSaved)

    #in seconds
    sleep(videoRecordTime)
    camera.stop_recording()
    camera.stop_preview()

    camera.close()


cameraTakePicture(1440,1080,'/test.jpg')

#cameraTakeVideo(1080, 1080, 5, 'test.mp4')


