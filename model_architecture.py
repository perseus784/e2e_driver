import tensorflow as tf
import numpy as np
from config import *

class My_Network(tf.keras.Model):

    def __init__(self):
        super(My_Network, self).__init__()
        self.l1 = self.dense_layer(4)
        self.l2 = self.dense_layer(4)
        self.l3 = self.dense_layer(2, activation=None)

    def dense_layer(self, number_of_units, activation='relu'):
        return tf.keras.layers.Dense(number_of_units, activation=activation)

    def time_distributed_layer(self, x):
        pass

    def CNN(self):
        pass
    
    def op_layer(self):
        pass

    def call(self, x):
        #print(x)
        #x = self.flatten(x)
        #print('flatten', x.shape)
        x = self.l1(x)
        x = self.l2(x)
        x = self.l3(x)
        #print('final',x.shape)
        return x

model = My_Network()
model.build(input_shape=(None, 5))
model.summary()
