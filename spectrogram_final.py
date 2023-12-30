import webbrowser
import io
import base64
from picamera import PiCamera
from time import sleep
from PIL import Image
import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library
import numpy as np
import colour
from colour.colorimetry import MSDS_CMFS
from flask import *
import sqlite3
import datetime

import matplotlib.pyplot as plt
import matplotlib

from PIL import Image

# initialisation
GPIO.setwarnings(False)  # Ignore warning for now
GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

camera = PiCamera()
camera.rotation = 180
camera.resolution = (2000, 1900)

camera.shutter_speed = 2000
camera.start_preview()
while True:  # Run forever
    if GPIO.input(10) == GPIO.HIGH:
        camera.capture('/home/user/Desktop/image3.jpg')
        camera.stop_preview()
        break
    else:
        continue
original = Image.open('/home/user/Desktop/image3.jpg')
original = original.transpose(Image.FLIP_TOP_BOTTOM)
width, height = original.size   # Get original dimensions
print(width, height)
left = 0.1*width
top = height/4
right = 0.725*width
bottom = 3*height/4

x = datetime.datetime.now()
formatFile = x.strftime("%d") + x.strftime("%m") + x.strftime("%y")+"_" + x.strftime("%H") + x.strftime("%M")
cropped_image = original.crop((left, top, right, bottom))
cropped_image.save('S'+formatFile+'.jpg', "JPEG")


# horizontal spectrum (i.e. colours go from left to right, not top to bottom)
# im = Image.open("croppedimage3.jpg")
threshold = 0.3
print("threshold V: ", threshold)
pic = cropped_image.load()
print("image size: ", cropped_image.size)
# find average rgb
RGBs = []
for p in range(cropped_image.size[0]):
    cur = [0, 0, 0]
    pno = 0
    for r in range(cropped_image.size[1]):
        if (max(pic[p, r][0]/255, pic[p, r][1]/255, pic[p, r][2]/255)) >= threshold:  # convert RGB to HSV and consider V values
            cur[0] += pic[p, r][0]/255
            cur[1] += pic[p, r][1]/255
            cur[2] += pic[p, r][2]/255
            pno += 1
    if cur != [0, 0, 0]:
        cur[0] = (cur[0]/pno)**(1/2.2)
        cur[1] = (cur[1]/pno)**(1/2.2)
        cur[2] = (cur[2]/pno)**(1/2.2)
        RGBs.append(cur)
print("no. of rows: ", len(RGBs))

print(RGBs[-1])
cmfs = MSDS_CMFS['CIE 1964 10 Degree Standard Observer']
xy_n = np.array([0.31382, 0.33100])
# xy_n = np.array([0.3142, 0.3289])


domwaveSets = []
intensity = []


def correction(wave):
    # return wave
    return 0.99696*wave + 11.33123


for i in range(len(RGBs)):
    RGBset = np.array([RGBs[i][0], RGBs[i][1], RGBs[i][2]])
    lumin = colour.sRGB_to_XYZ(RGBset, colour.CCS_ILLUMINANTS['CIE 1964 10 Degree Standard Observer']['D65'])[1]
    # print(colour.sRGB_to_XYZ(RGBset,colour.CCS_ILLUMINANTS['CIE 1964 10 Degree Standard Observer']['D65']),lumin)
    xycords = colour.XYZ_to_xy(colour.sRGB_to_XYZ(RGBset, colour.CCS_ILLUMINANTS['CIE 1964 10 Degree Standard Observer']['D65']))
    domwave = colour.dominant_wavelength(xycords, xy_n, cmfs)
    if float(domwave[0]) > 0 and float(domwave[0]) < 700:
        domwaveSets.append(correction(float(domwave[0])))
        intensity.append(lumin)
# print((589-domwaveSets[intensity.index(max(intensity))])/589*100)
normFact = max(intensity)
for i in range(len(intensity)):
    intensity[i] = intensity[i]/normFact
print(domwaveSets)
plt.plot(domwaveSets, intensity, 'o')
plt.xticks(np.arange(420, 660, 20))
plt.xlabel("wavelength/nm")
plt.ylabel("Rel. Intensity")

plt.savefig("G"+formatFile+".jpg")


with open("S"+formatFile+".jpg", "rb") as f:
    img_data = f.read()
S_encoded = base64.b64encode(img_data).decode("utf-8")
with open("G"+formatFile+".jpg", "rb") as f:
    img_data = f.read()
G_encoded = base64.b64encode(img_data).decode("utf-8")


# save the image into the db
con = sqlite3.connect("testing.db")
con.execute("INSERT INTO Colors VALUES (?,?,?)", (formatFile, S_encoded, G_encoded,))
con.commit()
con.close()


# retrieve the image

app = Flask(__name__)


@app.route("/")
def root():
    con = sqlite3.connect("testing.db")
    con.row_factory = sqlite3.Row
    cur = con.execute("SELECT DateTime FROM Colors")
    rows = cur.fetchall()
# d_rows = []
# for row in rows:
# d_row = []
# for col_i in range(len(row)):
# if col_i != 0:
# decoded_img = base64.b64decode(row[col_i])
# d_row.append(decoded_img)
# else:
# d_row.append(row[col_i])
# d_rows.append(d_row)
    con.close()
    return render_template("display.html", data=rows)


@app.route("/<name>")
def display(name):
    con = sqlite3.connect("testing.db")
    row = con.execute("SELECT * from Colors WHERE DateTime=?", (name,)).fetchone()
    con.close()
    b_spectrum = bytes(row[1], 'ascii')
    encoded = b_spectrum.decode('ascii')
    mime = "image/jpg"
    s_uri = "data:%s;base64,%s" % (mime, encoded)
    b_graph = bytes(row[2], 'ascii')
    encoded = b_graph.decode('ascii')
    mime = "image/jpg"
    g_uri = "data:%s;base64,%s" % (mime, encoded)
    return render_template("results.html", spectrum=s_uri, graph=g_uri, entry=row[0])


@app.route("/delete/<name>")
def delete(name):
    con = sqlite3.connect("testing.db")
    con.execute("DELETE FROM Colors WHERE DateTime=?", (name,))
    con.commit()
    con.close()
    return redirect("/")


@app.route("/rename/<name>", methods=["GET", "POST"])
def rename(name):
    con = sqlite3.connect("testing.db")
    newname = request.form['newname']
    print(newname)
    con.execute("UPDATE Colors SET DateTime=? WHERE DateTime=? ", (newname, name))
    con.commit()
    con.close()
    return redirect("/")


webbrowser.open_new("http://127.0.0.1:5000")
app.run()
