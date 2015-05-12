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

import rospy
import sys
import time

from rapp_platform_ros_communications.srv import (  
  AudioProcessingDenoiseSrv, 
  AudioProcessingDenoiseSrvResponse,
  AudioProcessingSetNoiseProfileSrv,
  AudioProcessingSetNoiseProfileSrvResponse
  )

from rapp_platform_ros_communications.srv import (
  fetchDataSrv,
  fetchDataSrvRequest
  )

from std_msgs.msg import ( 
  String 
  ) 

class AudioProcessing:
 
  # Constructor performing initializations
  def __init__(self):    

    self.set_noise_profile_topic = rospy.get_param(\
            "rapp_audio_processing_set_noise_profile_topic")
    self.denoise_topic = \
        rospy.get_param("rapp_audio_processing_denoise_topic")
 
    if(not self.set_noise_profile_topic):
      rospy.logerror("Audio processing noise profiling topic param not found")
    if(not self.denoise_topic):
      rospy.logerror("Audio processing denoise topic param not found")
 
    self.set_noise_profile_service = rospy.Service(self.set_noise_profile_topic, \
        AudioProcessingSetNoiseProfileSrv, self.setNoiseProfile)
    self.denoise_service = rospy.Service( \
        self.denoise_topic, AudioProcessingDenoiseSrv, \
        self.denoise)
 
  # Service callback for setting noise profile 
  def setNoiseProfile(self, req):
    res = AudioProcessingSetNoiseProfileSrvResponse()

    cleanup = []
    #-------------------------Check with database-------------------------#
    if self.use_db_authentication == True:
      req_db = fetchDataSrv()
      req_db.req_cols=[String(data="username")]
      entry1=[String(data="username"),String(data=req.user)]
      req_db.where_data=[StringArrayMsg(s=entry1)]

      resp = self.authentication_service(req_db.req_cols, req_db.where_data)
      print resp
      if resp.success.data != True or len(resp.res_data) == 0: 
        res.success = "Non authenticated user"
        return total_res

    directory = "/tmp/rapp_platform_files/audio_processing/" + req.user
    if not os.path.isdir(directory):
      os.makedirs(directory)
      directory += "/noise_profile/"
      os.makedirs(directory)

    noise_profile_file = directory
    new_audio = req.noise_audio_file

    # Making audio compatible to sphinx4
    if req.audio_file_type == 'nao_ogg':
      new_audio += ".wav"
      os.system("sox " + req.noise_audio_file + " " + new_audio)
      cleanup.append(new_audio)
    elif req.audio_file_type == "nao_wav_1_ch":
      pass
    elif req.audio_file_type == "nao_wav_4_ch":
      new_audio += "_1ch.wav"
      os.system("sox " + req.noise_audio_file + " -c 1 -r 16000 " + new_audio)
      cleanup.append(new_audio)
    else:
      res.success = "Non valid noise audio type"
      self.cleanup(cleanup)
      return total_res

    noise_profile_uri = directory + "noise_profile_" + req.audio_file_type
    # Extract noise_profile
    os.system("sox " + new_audio + " -t null /dev/null trim 0.5 2.5 noiseprof "\
            + noise_profile_uri)

    res.success = "true"
    self.cleanup(cleanup)
    return res

  # Service callback for handling denoising
  def denoise(self, req):     
    res = AudioProcessingDenoiseSrvResponse()
    directory = "/tmp/rapp_platform_files/audio_processing/" + req.user
    
    if  audio_type != "nao_ogg" and\
        audio_type != "nao_wav_1_ch" and\
        audio_type != "nao_wav_4_ch":
      res.success = "Wrong audio type"
      return res
    
    noise_profile = directory + "/noise_profile/noise_profile_" + audio_type
    if not os.path.isfile(noise_profile):
      res.success = "No noise profile for the " + audio_type + " type exists"
      return res
    
    command = "sox " + req.audio_file + " " + req.denoised_audio_file +\
            " noisered " + noise_profile + " " + str(scale)
    os.system(command)
    res.success = "true"
    return res

  # Cleanup method
  def cleanup(self, clean):
    for f in clean:
      command = "rm " + f
      os.system(command)

# Main function
if __name__ == "__main__": 
  rospy.init_node('AudioProcessing')
  AudioProcessingNode = AudioProcessing()
  rospy.spin()
