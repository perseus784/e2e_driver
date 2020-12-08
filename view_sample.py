import numpy as np
import cv2
import os
from config import *


np_data = np.load(os.path.join('data',"processed",'right','32.npz'), allow_pickle=True)
images = np_data["image"]
controls = np_data["controls"]

for i in range(max_sample_size):
    cv2.imshow("live", images[i][0])
    cv2.imshow("sem", images[i][1])
    cv2.waitKey(1)
    print(i, np_data["controls"][i])



