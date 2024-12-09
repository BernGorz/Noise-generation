import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

import cv2
import tkinter as tk
from tkinter.filedialog import askopenfilename


max_counts = 15     # Estimated value beyond which there are no events due to thermal noise


##########################
## Select image

root = tk.Tk()
root.withdraw()
print('Select the image to estimate thermal noise')
path = askopenfilename(title='Select the image to estimate thermal noise')
image = cv2.imread(path, 0)


##########################
## Count the distribution of events in the data

counts = np.zeros(256)

n, m = np.shape(image)
for i in range(n):
    for j in range(m):
        counts[image[i, j]] += 1

probabilities = counts/np.sum(counts)
index = np.array([i for i in range(256)])
plt.bar(index[:max_counts] - 0.2, probabilities[:max_counts], width=0.4, label = 'Background picture measurement')


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

print('Fitted data: mu = {:.2f}, sigma = {:.2f}'.format(mu, sigma))


##########################
## Plotting

negative_probabilities = [normal(i, mu, sigma) for i in range(-255, 1)]
probability_model = [normal(i, mu, sigma) for i in index]
probability_model[0] = np.sum(negative_probabilities)


plt.bar(index[:max_counts] + 0.2, probability_model[:max_counts], width=0.4, label = 'Gaussian distribution model, mu = {:.2f}, sigma = {:.2f}'.format(mu, sigma))

plt.title("Noise probability distribution")
plt.xlabel("Number of counts")
plt.ylabel("Probability")
plt.legend()

plt.show()
