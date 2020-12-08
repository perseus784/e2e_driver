import os

# settings
IM_W, IM_H, IM_C = (240, 200, 3)
AC_IM_W, AC_IM_H = 480,400
CARLA_PORT = 7878
TOWN = "Town02"
EPOCHS = 50
waypoint_buffer_size = 5
watchout_distance = 10 
waypoint_resolution = 2.0 
EGO_SPEED = 45
batch_size = 32
save_path ='data'
max_sample_size = 1024
data_max_sample_size = 2048

tensorlogs = os.path.join(save_path, 'logs')
model_save_folder = os.path.join(save_path,'trained_models','model_checkpoints{}')
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
number_env_vehicles = 50

data_collection_path = os.path.join(ROOT_DIR, save_path, 'data_collection' )
processed_data_path = os.path.join(ROOT_DIR, save_path, 'final_processed' )
train_path = os.path.join(ROOT_DIR, save_path, 'train_data' )
test_path = os.path.join(ROOT_DIR, save_path, 'test_data' )

if not os.path.exists(os.path.join(data_collection_path)):
    os.makedirs(data_collection_path)