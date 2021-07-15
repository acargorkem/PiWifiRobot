import board
import busio
import adafruit_bme280
import requests
import threading

from flask import Flask, jsonify, render_template, Response, request
from camera import Camera
from motor_drive import Motor
from audio import *
from odometry import *

# i2c object
i2c = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

# sea level pressure : 1013.25 hecto pascal
bme280.sea_level_pressure = 1013.25

# database server BASE URL
BASE_URL = 'http://192.168.1.24/IOT-Platform/'

# loop interval of  database post request for sensor values
DatabasePostRequestInterval = 60  # seconds

# motor_drive object
motor = Motor(enable_left=12, enable_right=13,
              left_motor_forward=23, left_motor_backward=24,
              right_motor_forward=27, right_motor_backward=22)


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def get_bme280_values():
    return {'temperature': round(bme280.temperature, 2),
            'pressure': round(bme280.pressure, 2),
            'altitude': round(bme280.altitude, 2),
            'humidity': round(bme280.relative_humidity, 2)}


# send sensor data to database server
def post_sensor_values():
    while True:
        url = BASE_URL + 'query.php'
        payload = get_bme280_values()
        payload.update({'api_key': 'gorkem'})
        response = requests.post(url, data=payload, timeout=10)
        return response


# send image data to database server
def post_images():
    while True:
        frame = Camera().get_frame()
        url = BASE_URL + 'image-upload.php'
        payload = {'img_name': time.strftime('%Y-%m-%d__%H-%M-%S'),
                   'img_file': frame}

        response = requests.post(url, data=payload, timeout=10)
        return response


# send audio data to database server
def post_audio():
    while True:
        url = BASE_URL + 'audio-upload.php'
        audio_data = read_data(5)
        payload = {'audio_name': time.strftime('%Y-%m-%d__%H-%M-%S'),
                   'audio_data': audio_data}
        response = requests.post(url, data=payload, timeout=30)
        return response


def post_requests_thread():
    post_sensor_values()
    post_images()
    post_audio()
    time.sleep(DatabasePostRequestInterval)


# start post requests thread
post_requests_thread = threading.Thread(target=post_requests_thread)
post_requests_thread.setDaemon(True)
post_requests_thread.start()

# start flask server
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/bme280')
def hello():
    return jsonify(get_bme280_values())


@app.route('/video_feed')
def video_feed():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/drive', methods=['POST'])
def parse_request():
    angle = float(request.form.get('angle'))
    left_speed = float(request.form.get('leftSpeed'))
    right_speed = float(request.form.get('rightSpeed'))
    motor.drive(angle, left_speed, right_speed)
    return 'drive successful'


@app.route('/position')
def position():
    x, y = last_position()
    text = position_text(x, y)
    return jsonify({'x': x, 'y': y, 'Konum': text})


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
