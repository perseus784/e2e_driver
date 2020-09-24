import os,sys,random,time
import carla
import numpy as np
import cv2

#settings
IM_W,IM_H = (420,280)
time_step = 1.5
image_save_path ='_data'
seq_len = 15
number_env_vehicles = 35
if not os.path.exists(os.path.join(image_save_path)):
    os.makedirs(os.path.join(image_save_path))
#create main carla objects
client = carla.Client('localhost', 7878)
client.set_timeout(5)
world = client.get_world()

blueprint_library = world.get_blueprint_library()
