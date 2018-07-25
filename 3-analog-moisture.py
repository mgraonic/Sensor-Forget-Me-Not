#!/usr/bin/python
import datetime, time, signal, sys, pytz
import pyrebase
import config
import  Adafruit_ADS1x15
from twilio.rest import Client

token = config.twilio_token
account_sid = config.twilio_sid
client = Client(account_sid, token)

# Modify code below with your custom threshold
def messageMe(percent):
        message = client.messages \
                        .create(
                        to='<YOUR PHONE NUMBER>',
                        from_='<YOUR TWILIO PHONE NUMBER>',
                        body="It's time to water me! My critical moisture threshold is <DESIRED PERCENTAGE>%% and I'm at %d%%." % (percent)
                        )


creds = config.credentials

firebase = pyrebase.initialize_app(creds)
db = firebase.database()

def update_firebase(percent, time):
    data = {"moisture": percent, "utc_time": time}
    db.child("levels").push(data)

while True:

    def signal_handler(signal, frame):
            print ('You pressed Ctrl+C!')
            sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    print ('Press Ctrl+C to exit')

    ADS1015 = 0x00  # 12-bit ADC
    ADS1115 = 0x01  # 16-bit ADC

    # Initialise the ADC using the default mode (use default I2C address)
    #adc = ADS1x15(ic=ADS1015)
    adc = Adafruit_ADS1x15.ADS1015()

    # Read channel 0 in  single-ended mode
    reading = adc.read_adc(0, gain=1)

    # Convert to human-readable value
    percent = round((100 * reading) / 1330)

    # Create an instance of utc time and format as string
    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
    time_string = utc_now.isoformat()


    print ("%d%%" % (percent))
    update_firebase(percent, time_string)
    if percent <= 80:
        messageMe(percent)

    time.sleep(86400)
