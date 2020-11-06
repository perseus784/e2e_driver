import numpy as np
import os
import random
from config import *


class data_tools:
    def __init__(self,data_folder,split_name):
        self.data_folder = data_folder
        self._data = os.listdir(self.data_folder)
        if split_name == 'train':
            self.it = int(batch_size/8)
        else:
            self.it = int(32/8)

    def batch_dispatch(self):
        counter = 0
        random.shuffle(self._data)
        while counter<=len(self._data):
            images=np.empty((0, IM_W, IM_H, IM_C))
            waypoints = np.empty((0,waypoint_buffer_size,3))
            controls = np.empty((0, 3))

            for i in range(self.it):
                np_data = np.load(os.path.join(self.data_folder,self._data[counter]))
                images = np.vstack((images,np_data['image']/255))
                waypoints = np.vstack((waypoints,np_data['waypoints']))
                controls =  np.vstack((controls,np_data['controls']))
                counter += 1
                if counter>=len(self._data):
                    counter = 0
                    random.shuffle(self._data)
            yield [images, waypoints, controls]