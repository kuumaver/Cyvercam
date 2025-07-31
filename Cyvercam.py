from flask import Flask, render_template, Response
from picamera2 import Picamera2
from threading import Thread
import time
import io
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

servo = 27
GPIO.setup(servo, GPIO.OUT)
pwm = GPIO.PWM(servo, 50)
pwm.start(0)


app = Flask(__name__)
camera = Picamera2()
config = camera.create_video_configuration(
    main={"size": (1024, 768)},
    controls={"FrameDurationLimits": (15000, 15000)}, 
    buffer_count=2
    )

camera.configure(config)
camera.start()
time.sleep(1) 

#start of camera codes==================================================================

global startTime
startTime = time.time()
global streamFps 
streamFps = 33

def millis(): 
    return round((time.time()-startTime)*1000)

def cameraStream(): 
    global frame
    global streamFps
    lastFrameTime = 0
    while True:
        if ((millis()-lastFrameTime)>=streamFps):
            print("Last frame time " + str(millis()-lastFrameTime)) 
            stream = io.BytesIO()
            camera.capture_file(stream, format='jpeg')  
            stream.seek(0) 
            frame = stream.read() 
            lastFrameTime = millis()
            stream.truncate() 
def videoStream(): 
    global frame
    lastFrame = None
    while True:
        if frame != lastFrame:
            lastFrame = frame
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

#end of camera related code ========================================================

@app.route('/')
def index():
    return render_template('Cyver_index.html')

@app.route('/video_feed')
def video_feed(): 
    return Response(videoStream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/right')
def right():
	pwm.ChangeDutyCycle(2)
	time.sleep(0.3)
	pwm.ChangeDutyCycle(0)
	return render_template('Cyver_index.html')

@app.route('/left')
def left():
	pwm.ChangeDutyCycle(12)
	time.sleep(0.3)
	pwm.ChangeDutyCycle(0)
	return render_template('Cyver_index.html')


if __name__ == '__main__':
    streamThread = Thread(target=cameraStream)
    streamThread.start() 
    app.run(host='0.0.0.0', debug=False)
