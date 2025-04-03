import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

import cv2
import tkinter as tk
from tkinter.filedialog import askopenfilename


max_counts = 15     # Estimated value beyond which there are no events due to thermal noise

exposure = 1        # Value that the picture has been artificially multiplied by



##########################
## Select image



root = tk.Tk()
root.withdraw()
print('Select the image to estimate thermal noise')
path = askopenfilename(title='Select the image to estimate thermal noise')
image = cv2.imread(path, 0)
max_intensity = np.max(image)
print(max_intensity)
image_color = cv2.imread(path, cv2.IMREAD_COLOR) * int(255 / max_intensity)


height, width = np.shape(image)

for i in range(width):
    for j in range(height):
        image[i][j] = int(round(image[i][j]/exposure))

x0, y0 = 0, 0
x1, y1 = width - 1, height - 1

pressed = False

def mouse_drawing(event, x, y, flags, params):
    global x0, y0
    global x1, y1
    global pressed
    global image_color
    if event == cv2.EVENT_LBUTTONDOWN:
        pressed = True
        x0, y0 = x, y

    if event == cv2.EVENT_LBUTTONUP:
        pressed = False
        if 0 <= x and x < width and 0 <= y and y <= height: 
            cv2.destroyWindow("select_area")
        else:
            image_color = cv2.imread(path, cv2.IMREAD_COLOR) * int(255 / max_intensity)
        

    if event == cv2.EVENT_MOUSEMOVE and pressed:
        x1, y1 = x, y
        image_color = cv2.imread(path, cv2.IMREAD_COLOR) * int(255 / max_intensity)
        cv2.rectangle(image_color, (x0, y0), (x1, y1), (0, 0, 192), 1)

cv2.namedWindow("select_area", cv2.WINDOW_NORMAL)
cv2.setWindowTitle("select_area", "Select area containing only background")
cv2.setMouseCallback("select_area", mouse_drawing)
cv2.resizeWindow("select_area", width, height)

display = True
while display:
    cv2.imshow("select_area", image_color)
    key = cv2.waitKey(1) & 0XFF
    if key == 27 or key == 13 or cv2.getWindowProperty('select_area',cv2.WND_PROP_VISIBLE) < 1: # Close if pressed 'ESC', 'ENTER', or closed window
        display = False

x0, x1 = min(x0, x1), max(x0, x1)
y0, y1 = min(y0, y1), max(y0, y1)



##########################
## Count the distribution of events in the data

counts = np.zeros(256)


for x in range(x0, x1+1):
    for y in range(y0, y1+1):
        counts[image[y, x]] += 1

probabilities = counts/np.sum(counts)
index = np.array([i for i in range(256)])
plt.bar(index[:max_counts] - 0.2, probabilities[:max_counts], width=0.4, label = 'Background picture measurement')




# i = 2
# sigma_guess = 1/np.sqrt(np.log(probabilities[i+1]**2/(probabilities[i]*probabilities[i+2])))
# mu_guess = i + 0.5 + sigma_guess**2*np.log(probabilities[i+1]*probabilities[i])
# print(mu_guess)
# print(sigma_guess)

##########################
## Fit the data to gaussian noise

def normal(n, mu, sigma):
    '''Probability P(X=n) following a Gaussian distribution'''
    pref = 1/np.sqrt(2*np.pi*sigma**2)
    exp = np.exp(-(n-mu)**2/(2*sigma**2))
    return(pref*exp)

def func(n, mu, sigma):
    '''Probability P(X=n) following a Gaussian distribution, with the exception of negative values being set to 0.'''
    return((n>0)*normal(n, mu, sigma) + (n==0)*np.sum([normal(i, mu, sigma) for i in range(-255, 1)]))

xdata = index[:max_counts]
ydata = probabilities[:max_counts]

initial_guess = [0, 1]                                       # Initial guess mu = 0 and sigma = 1
popt, pcov = curve_fit(func, xdata, ydata, initial_guess)    # Optimizing mu and sigma to fit the data
mu, sigma = popt

##########################
## Plotting

print("________________________________________")

print('Fitted data: mu = {:.2f}, sigma = {:.2f}'.format(mu, sigma))

total_counts = np.sum(image)
average_count_number = np.sum([index*probability for index, probability in enumerate(probabilities)])
print("Average thermal count number per pixel: {:.3f}".format(average_count_number))
print("Total counts: {:.0f}".format(total_counts))
print("Estimated counts not attributed to thermal noise (assuming uniform distribution): {:.0f}".format(total_counts - average_count_number*width*height))
print("")


negative_probabilities = [normal(i, mu, sigma) for i in range(-255, 1)]
probability_model = [normal(i, mu, sigma) for i in index]
probability_model[0] = np.sum(negative_probabilities)


# expected_count_number = np.sum([index*probability for index, probability in enumerate(probability_model)])


plt.bar(index[:max_counts] + 0.2, probability_model[:max_counts], width=0.4, label = 'Gaussian distribution model, mu = {:.2f}, sigma = {:.2f}'.format(mu, sigma))

plt.title("Noise probability distribution")
plt.xlabel("Number of counts")
plt.ylabel("Probability")
plt.legend()

plt.show()
