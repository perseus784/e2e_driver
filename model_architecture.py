import tensorflow as tf
import numpy as np
from config import *

class My_Network(tf.keras.Model):

    def __init__(self):
        super(My_Network, self).__init__()
        self.in1 = tf.keras.layers.Input(shape=(None, IM_W, IM_H, IM_C))
        self.in2 = tf.keras.layers.Input(shape=(None, waypoint_buffer_size))
        self.cnn = self.CNN()
        self.rnn1 =self.RNN(True)
        self.rnn2 =self.RNN(False)
        self.global_pooling = tf.keras.layers.GlobalAveragePooling2D()
        self.l1 = self.dense_layer(256)
        self.l2 = self.dense_layer(512)
        self.l3 = self.dense_layer(512)
        self.acceleration = self.dense_layer(1, 'sigmoid')
        self.steer = self.dense_layer(1, 'tanh')
        self.brake = self.dense_layer(1, 'sigmoid')

    def dense_layer(self, number_of_units, activation='relu'):
        return tf.keras.layers.Dense(number_of_units, activation=activation)

    def time_distributed_layer(self, x):
        pass

    def CNN(self):
        cnn = tf.keras.applications.EfficientNetB0(input_shape=(IM_W,IM_H,IM_C), include_top=False)
        return cnn
    
    def RNN(self, return_sequences):
        gru = tf.keras.layers.GRU(units=waypoint_buffer_size, return_sequences=return_sequences, dropout=0.5,recurrent_dropout=0.5)
        return gru

    def call(self, x):
        x_cnn = self.cnn(x[0])
        x_cnn = self.global_pooling(x_cnn)
        x_rnn = self.rnn1(x[1])
        x_rnn = self.rnn2(x_rnn)
        x_rnn = self.l1(x_rnn)
        combined_network = tf.concat([x_cnn, x_rnn], axis=1)
        combined_network = self.l2(combined_network)
        combined_network = self.l3(combined_network)
        return [self.acceleration(combined_network), self.steer(combined_network), self.brake(combined_network)]

'''
model = My_Network()
model.build(input_shape=[(None, IM_W,IM_H,IM_C), (None, 5, 3)])
model.summary()
'''