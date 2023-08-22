import board
import wifi
import time
import ssl
import adafruit_requests
import socketpool
import busio
import adafruit_gps
import neopixel
pixels = neopixel.NeoPixel(board.D5, 32)

try:
    from secrets import secrets
except ImportError:
    print("no secrets found")
    raise

try:
    print("Connecting to %s" % secrets["ssid"])
    wifi.radio.connect(secrets["ssid"], secrets["password"])
    print("Connected to %s!" % secrets["ssid"])
# Wi-Fi connectivity fails with error messages, not specific errors, so this except is broad.
except Exception as e:  # pylint: disable=broad-except
    print("Failed to connect to WiFi. Error:", e, "\nBoard will hard reset in 30 seconds.")
    time.sleep(30)
    microcontroller.reset()

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())
r = requests.get("http://api.open-notify.org/iss-now.json")
r2= r.json()

ISS_LAT = float(r2["iss_position"]["latitude"])
ISS_LON = float(r2["iss_position"]["longitude"])

print(ISS_LAT)
print(ISS_LON)

uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)


gps = adafruit_gps.GPS(uart, debug=False)


gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")

gps.send_command(b"PMTK220,1000")

last_print = time.monotonic()
wait = 0
while True:

    gps.update()

    current = time.monotonic()
    if current - last_print >= 1.0:
        last_print = current
        if wait == 10:
            break
        if not gps.has_fix:

            print("Waiting for fix...")
            wait += 1
            continue
        else:
            print("Latitude: {0:.6f} degrees".format(gps.latitude))
            print("Longitude: {0:.6f} degrees".format(gps.longitude))
            break

try:
    YOUR_LAT = float(gps.latitude)
except:
    YOUR_LAT = 35.270378
try:
    YOUR_LON = float(gps.longitude)
except:
    YOUR_LON = 120.6596

print(YOUR_LAT)
print(YOUR_LON)

if YOUR_LAT - ISS_LAT < 5 and YOUR_LAT - ISS_LAT > -5:
    if YOUR_LAT - ISS_LAT < 5 and YOUR_LAT - ISS_LAT > -5:
        print("its close")
        for n in range (0,32):
            pixels[n] = (0,255,0)

    else:
        print("its far")
        for n in range (0,32):
            pixels[n] = (255,0,0)

else:
    print("its far")
    for n in range (0,32):
        pixels[n] = (255,0,0)

time.sleep(5)
for n in range (0,32):
    pixels[n] = (0,0,0)
