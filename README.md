Code by Bernard Gorzkowski
Contact: bernard.gorzkowski@gmail.com

### Installation ###

The code has been tested for python v ersion 3.11.7. It requires pillow and tkinter.

Currently, only grayscale .bmp files have been tested.

### Noise generation ###

Simulate a measurement by introducing shot noise (Poisson distribution) and thermal noise (Gaussian distribution) into a grayscale image. The output is an image file simulating what a single photon camera would see for each of its pixels.
You can vary the following parameters:
- Average total number of photons: The expectation value of photons we would get after summing events from all pixels without gaussian noise.
- Gaussian noise mean
- Gaussian noise standard deviation
- Saturation threshold: If any pixel has more events than the threshold value, if will automatically get set to the threshold value. Side note: if any pixel has a value < 0 due to the gaussian distribution, its value will be set to 0.

Parameters can be varied beyond what is allowed by the sliders by modifying the values by hand.

You can generate multiple images at once, in that case they will be saved as [path to file]/[filename]_xxx.[extension]. For example, if we specify the output path as C:/Users/user/test.bmp, the 5th image of a seriess of 100 will be saved as C:/Users/user/test_005.bmp

The code has been tested only on grayscale .bmp files. Works for python version 3.11.7