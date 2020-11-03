import os

# settings
IM_W, IM_H = (360, 240)
CARLA_PORT = 7878
TOWN = "Town01"
waypoint_buffer_size = 5
watchout_distance = 10 
waypoint_resolution = 2.0 
EGO_SPEED = 45
batch_size = 8
image_save_path ='data'
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
number_env_vehicles = 50
data_collection_path = os.path.join(ROOT_DIR, 'data_collection')
if not os.path.exists(os.path.join(image_save_path)):
    os.makedirs(os.path.join(image_save_path))