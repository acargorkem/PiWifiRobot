import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class Motor:
    def __init__(self, enable_left, left_motor_forward, left_motor_backward,
                 enable_right, right_motor_forward, right_motor_backward):
        self.enable_left = enable_left
        self.left_motor_forward = left_motor_forward
        self.left_motor_backward = left_motor_backward
        GPIO.setup(self.enable_left, GPIO.OUT)
        GPIO.setup(self.left_motor_forward, GPIO.OUT)
        GPIO.setup(self.left_motor_backward, GPIO.OUT)

        self.pwm_left = GPIO.PWM(self.enable_left, 1000)  # enable with 1000 freq
        self.pwm_left.start(0)  # start with 0 duty cycle

        self.enable_right = enable_right
        self.right_motor_forward = right_motor_forward
        self.right_motor_backward = right_motor_backward
        GPIO.setup(self.enable_right, GPIO.OUT)
        GPIO.setup(self.right_motor_forward, GPIO.OUT)
        GPIO.setup(self.right_motor_backward, GPIO.OUT)

        self.pwm_right = GPIO.PWM(self.enable_right, 1000)  # enable with 1000 freq
        self.pwm_right.start(0)  # start with 0 duty cycle

    def drive(self, angle, left_speed, right_speed):
        self.pwm_left.ChangeDutyCycle(left_speed)
        self.pwm_right.ChangeDutyCycle(right_speed)

        if 5 < angle < 175:
            ''' MOVING FORWARD'''
            GPIO.output(self.left_motor_forward, GPIO.HIGH)
            GPIO.output(self.left_motor_backward, GPIO.LOW)
            GPIO.output(self.right_motor_forward, GPIO.HIGH)
            GPIO.output(self.right_motor_backward, GPIO.LOW)
        elif 185 < angle < 350:
            ''' MOVING BACKWARD'''
            GPIO.output(self.left_motor_forward, GPIO.LOW)
            GPIO.output(self.left_motor_backward, GPIO.HIGH)
            GPIO.output(self.right_motor_forward, GPIO.LOW)
            GPIO.output(self.right_motor_backward, GPIO.HIGH)
        elif (0 <= angle < 5) or (355 <= angle < 360):
            ''' MOVING RIGHT'''
            GPIO.output(self.left_motor_forward, GPIO.LOW)
            GPIO.output(self.left_motor_backward, GPIO.HIGH)
            GPIO.output(self.right_motor_forward, GPIO.HIGH)
            GPIO.output(self.right_motor_backward, GPIO.LOW)
        elif 175 < angle < 185:
            ''' MOVING LEFT'''
            GPIO.output(self.left_motor_forward, GPIO.HIGH)
            GPIO.output(self.left_motor_backward, GPIO.LOW)
            GPIO.output(self.right_motor_forward, GPIO.LOW)
            GPIO.output(self.right_motor_backward, GPIO.HIGH)
        else:
            ''' STOP '''
            GPIO.output(self.left_motor_forward, GPIO.LOW)
            GPIO.output(self.left_motor_backward, GPIO.LOW)
            GPIO.output(self.right_motor_forward, GPIO.LOW)
            GPIO.output(self.right_motor_backward, GPIO.LOW)
