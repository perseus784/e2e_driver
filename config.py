import os

# settings
IM_W, IM_H = (420, 280)
image_save_path ='data'
number_env_vehicles = 35

if not os.path.exists(os.path.join(image_save_path)):
    os.makedirs(os.path.join(image_save_path))