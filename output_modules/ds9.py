#!/usr/bin/python
# -*- coding:  cp1251 -*-
import random as random_number
import sys
import math
import numpy as np
from scipy import stats
import scipy as sp
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.patches as patches
import matplotlib.path as path
from matplotlib.ticker import NullFormatter
from numpy import *
from pylab import *
import os
import shutil
#import subprocess
import signal


import subprocess as sub


# Function to create png files using ds9

def ds9_image(image):
	sub.call("ds9 %s[1] -colorbar no -scale log -cmap Grey -cmap invert yes -export jpeg galaxy.jpeg -exit" % (image), shell=True, close_fds=False)
	sub.call("ds9 %s[2] -colorbar no -scale log -cmap Grey -cmap invert yes -export jpeg model.jpeg -exit" % (image), shell=True, close_fds=False)
	sub.call("ds9 %s[3] -colorbar no -scale sqrt -cmap Grey -cmap invert yes -export jpeg residual.jpeg -exit" % (image), shell=True, close_fds=False)




