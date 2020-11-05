import numpy as np
import tensorflow as tf
from model_architecture import My_Network
from config import *

class Train_Class:

    def __init__(self):
        self.model = My_Network()
        self.optimizer = tf.keras.optimizers.Adam()
        self.loss = tf.keras.losses.Huber()
        self.tensorboard_callback = tf.keras.callbacks.TensorBoard(os.path.join(save_path, 'logs'), update_freq=1)
        self.model_save_callback = tf.keras.callbacks.TensorBoard(os.path.join(save_path,'model_checkpoints'))
        self.tensorboard_callback.set_model(self.model)
        self.model_save_callback.set_model(self.model)

    def train_step(self):
        pass
    
    def load_data(self, batch_size):
        pass

    def store_model(self):
        pass

    def write_summary(self):
        pass

    def train_model(self, model):
        pass
c = Train_Class()


