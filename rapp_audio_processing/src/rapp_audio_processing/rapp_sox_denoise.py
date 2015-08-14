#!/usr/bin/env python
# -*- encode: utf-8 -*-

#MIT License (MIT)

#Copyright (c) <2014> <Rapp Project EU>

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

# Authors: Manos Tsardoulias
# contact: etsardou@iti.gr

import sys
import time
import os
from pylab import *
from scipy.io import wavfile

class SoxDenoise :
 
  # Service callback for detecting silence
  def soxDenoise(self, user, audio_type, audio_file, denoised_audio_file, scale):     
    if not os.path.isfile(audio_file):
        return [-1, False]

    if scale < 0 or scale > 1:
        return "Invalid scale. Scale must be between [0,1]"

    directory = "/tmp/rapp_platform_files/audio_processing/" + user
    noise_profile = directory + "/noise_profile/noise_profile_" + audio_type
    
    if not os.path.isfile(noise_profile):
        return "No noise profile for the " + audio_type + " type exists"
    
    command = "sox " + audio_file + " " + denoised_audio_file +\
            " noisered " + noise_profile + " " + str(scale)
    com_res = os.system(command)
    
    if com_res != 0:
        return "System sox malfunctioned"
    else:
        return "true"

