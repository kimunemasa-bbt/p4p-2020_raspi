#!/usr/bin/env python3
# coding: utf-8

## ライブラリインポート
import RPi.GPIO as GPIO
import time
from datetime import datetime
import picamera
import boto3
import os

## 変数
LedPin = 15            # GPIO15 LED
BtnPin = 12            # GPIO12 button
pathdir = "data"       # 画像保存先ディレクトリ
pathfile = "image.jpg" # 画像ファイル 
imageFile = os.path.join(pathdir, pathfile)


## 初期化
def setup():
    GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
    GPIO.setup(LedPin, GPIO.OUT)   # Set LedPin's mode is output
    GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V)
    GPIO.output(LedPin, GPIO.HIGH) # Set LedPin high(+3.3V) to make led off

## リセット
def destroy():
    GPIO.output(LedPin, GPIO.HIGH)     # led off
    GPIO.cleanup()                     # Release resource
    print('- cleanup GPIO -')


## 写真を撮る
def camera(filename):
    print('btn on')

    with picamera.PiCamera() as camera:
        GPIO.output(LedPin, GPIO.HIGH) # 撮った瞬間だけLEDを消す
        camera.brightness = 55
        camera.saturation = 0
        camera.start_preview()
        camera.capture(filename)
        GPIO.output(LedPin, GPIO.LOW) # 撮ったのでLEDをつける
        time.sleep(1)  # 1秒待つ


## S3に画像をアップロード
def upload_to_S3(filename):
    print("upload_to_S3:"+filename)
    bucket_name = "p4p-kimunemasa"
    s3 = boto3.resource('s3')
    s3.Bucket(bucket_name).upload_file(filename, filename)
    print("done")


def flow():
    timestr = datetime.now().strftime('%Y%m%d%H%M%S')
    filename=timestr+'.jpg'
    camera(filename)
    upload_to_S3(filename)
    os.remove(filename)

def main():
    while True:
        GPIO.output(LedPin, GPIO.LOW)  # led on
        if GPIO.input(BtnPin) == GPIO.LOW:
            flow()
        else:
            print('btn off')
        time.sleep(0.1)



if __name__ == '__main__': 
    setup()
    try:
        main()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()
