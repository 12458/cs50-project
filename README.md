# CS50 Final Project: Computer-Vision Powered Spectrometer

*Done by: [Matthew Liang](https://github.com/MattLiangYH), [Kia Jia Han](https://github.com/TheKJH), [Sim Shang En](https://github.com/12458)*

## Video Demo

[<img src="https://img.youtube.com/vi/HLN-EeEsldI/hqdefault.jpg" width="600" height="300"
/>](https://www.youtube.com/embed/HLN-EeEsldI)

## Abstract

This project aims to create a computer-vision-powered spectrometer that can accurately determine the spectral wavelengths in a given spectrum for educational purposes. Currently, a laboratory spectrometer is considered an uncommon laboratory apparatus in high schools, and it is very expensive to obtain (around $1000- $2000 SGD) [[1]](#references). However, it is vital in investigating the spectral power distribution of light sources, making it extremely difficult for students interested in understanding the spectral distribution of light.

Guides on how to make DIY versions of spectrometers are readily available online [[2,3]](#references), and while these DIY spectrometers can successfully split light into its constituent colours, it is unable to calculate the wavelengths that are present, as well as the intensity associated with those wavelengths. Hence, the engineering aims of this project are to be able to create a spectrometer that can calculate the wavelength and intensity of a spectrum to a reasonable degree of accuracy while ensuring that it is as cost-efficient as possible.

For the hardware aspect of this project, medium-density fibreboards (MDFs) were cut into pieces using a laser cutter. These pieces were then spray-painted black and assembled into a box. 3D-printed parts were created to mount the Raspberry Pi camera and the diffraction grating, which are placed in the box.

For the software aspect of this project, a program was created to allow the Raspberry Pi to capture images of the spectrum using a camera whenever a button is pressed. Then, Pillow was used to extract the RGB values of the different pixels in the image. Subsequently, Colour - an open-source Python package - was used to convert these RGB values into wavelengths and intensity values. These values were then plotted using MatPlotLib and the graph was saved as an image. Finally, these images are then saved into a database in a web server.

Our system can capture images of spectra from various light sources like lasers and LEDs, calculate the wavelengths and intensity of the different colours in the spectra to a reasonable degree of accuracy, and save these images into the database successfully. However, it is unable to capture pictures of the spectra of dimly lit sources such as candles, and its accuracy decreases for lower wavelength values in the 400-450nm range due to the inherent limitations of the CIE colour space which is used to calculate the wavelengths from the RGB values.

We believe this system can be used by students who are willing to learn more about the spectral distribution of light as it gives them an affordable and accessible means to understand this concept quantitatively.

## Description of files

`spectrogram_final.py`: The main code that helps to take a picture of the spectrum, calculate the wavelengths in the spectrum and transfer the data into the webserver. It works by first initialising the raspberry pi camera, then capturing an image of the spectrum. Afterwards, it will use functions from the colour module to calculate the wavelengths in the spectrum and use matplotlib to plot the relative intensity vs wavelength graph. The code saves the graph and the spectrum as JPEG images and then stores them into the database. Finally, the flask portion of the code starts the webserver and the user will be directed to the landing page of the web application.

`testing.db`: The database in which the images of the spectra and graphs are stored as BLOBs. The primary key is the DateTime in which the reading was taken

`templates`: Contains the files `display.html` and `results.html`

> `display.html` contains the landing page for the web app, with all the different entries in the database, and when one of the entries is clicked, the user is directed to `results.html`, where the spectrum and its graph are displayed

## References

[1] Spectrometers. element14. (n.d.). [https://sg.element14.com/c/test-measurement/spectrometers](https://sg.element14.com/c/test-measurement/spectrometers) 

[2] A fresh look at Light: Build your own spectrometer. Science in School. (2022, December 15). [https://www.scienceinschool.org/article/2007/spectrometer/](https://www.scienceinschool.org/article/2007/spectrometer/) 

[3] NASA. (2023, April 28). Educator guide: Using light to study planets. NASA. [https://www.jpl.nasa.gov/edu/teach/activity/using-light-to-study-planets/](https://www.jpl.nasa.gov/edu/teach/activity/using-light-to-study-planets/)
