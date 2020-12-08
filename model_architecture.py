import tensorflow as tf
import numpy as np
from config import *

'''
class My_Network(tf.keras.Model):

    def __init__(self):
        super(My_Network, self).__init__()
        self.in1 = tf.keras.layers.Input(shape=(None, IM_W, IM_H, IM_C )
        self.in2 = tf.keras.layers.Input(shape=(None, waypoint_buffer_size )
        self.cnn = self.CNN()
        self.rnn1 =self.RNN(True)
        self.rnn2 =self.RNN(False)
        self.global_pooling = tf.keras.layers.GlobalAveragePooling2D()
        self.l1 = self.dense_layer(256)
        self.l2 = self.dense_layer(1024)
        self.l3 = self.dense_layer(1024)
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
        x_cnn = self.cnn(x)
        x_cnn = self.global_pooling(x_cnn)
        x_rnn = self.rnn1(x[1])
        x_rnn = self.rnn2(x_rnn)
        x_rnn = self.l1(x_rnn)
        combined_network = tf.concat([x_cnn, x_rnn], axis=1)
        combined_network = self.l2(x_cnn)
        combined_network = self.l3(combined_network)
        return [self.acceleration(combined_network), self.steer(combined_network), self.brake(combined_network)]

model = My_Network()
model.build(input_shape=[(None, IM_W,IM_H,IM_C), (None, 5, 3)])
model.summary()
'''

class My_Network():

    def __init__(self):
        pass        

    def CNN(self, input_):
        conv_model =  tf.keras.layers.Conv2D(64, (7,7), padding='same', activation='relu')(input_)
        conv_model =  tf.keras.layers.BatchNormalization()(conv_model)
        conv_model =  tf.keras.layers.MaxPool2D(pool_size=(3,3), padding='SAME',strides=(2,2))(conv_model)

        conv_model =  tf.keras.layers.Conv2D(192, (3,3), padding='same', activation='relu')(conv_model)
        conv_model =  tf.keras.layers.BatchNormalization()(conv_model)
        conv_model =  tf.keras.layers.MaxPool2D(pool_size=(3,3), padding='SAME',strides=(2,2))(conv_model) 
        conv_model = tf.keras.layers.Dropout(0.2)(conv_model)

        conv_model = self.inception_module(conv_model,128,128,192,32,96,64)
        conv_model =  tf.keras.layers.MaxPool2D(pool_size=(3,3), padding='SAME',strides=(2,2))(conv_model) 
        conv_model = tf.keras.layers.Dropout(0.3)(conv_model)

        conv_model = self.inception_module(conv_model,256,160,320,32,128,128)
        conv_model =  tf.keras.layers.MaxPool2D(pool_size=(3,3), padding='SAME',strides=(2,2))(conv_model)
        conv_model = tf.keras.layers.Dropout(0.3)(conv_model)

        conv_model = self.inception_module(conv_model,384,192,384,48,128,128)
        conv_model =  tf.keras.layers.MaxPool2D(pool_size=(3,3), padding='SAME',strides=(2,2))(conv_model)
        conv_model = tf.keras.layers.Dropout(0.3)(conv_model)

        conv_model =  tf.keras.layers.Flatten()(conv_model)
        return conv_model

    def inception_module(self, conv_model, filter1, filter2_1, filter2_2, filter3_1, filter3_2, filter4):
        conv_1 = tf.keras.layers.Conv2D(filter1, (1,1), padding='same', activation='relu')(conv_model)
        conv_1 = tf.keras.layers.BatchNormalization()(conv_1)

        conv_3_1 = tf.keras.layers.Conv2D(filter2_1, (1,1), padding='same', activation='relu')(conv_model)
        conv_3_2 = tf.keras.layers.Conv2D(filter2_2, (3,3), padding='same', activation='relu' )(conv_3_1)
        conv_3_2 = tf.keras.layers.BatchNormalization( )(conv_3_2)

        conv_5_1 = tf.keras.layers.Conv2D(filter3_1, (1,1), padding='same', activation='relu' )(conv_model)
        conv_5_2 = tf.keras.layers.Conv2D(filter3_2, (5,5), padding='same', activation='relu' )(conv_5_1) 
        conv_5_2 = tf.keras.layers.BatchNormalization()(conv_5_2)

        pooling_layer = tf.keras.layers.MaxPool2D(pool_size=(3,3), padding='SAME',strides=(1,1))(conv_model)

        conv_pooling = tf.keras.layers.Conv2D(filter4, (1,1), padding='same', activation='relu')(pooling_layer) 
        conv_pooling = tf.keras.layers.BatchNormalization()(conv_pooling)

        module = tf.keras.layers.Concatenate(axis = -1)([conv_1,conv_3_2,conv_5_2,conv_pooling])
        return module

    def RNN(self, return_sequences):
        gru = tf.keras.layers.GRU(units=waypoint_buffer_size, return_sequences=return_sequences, dropout=0.5,recurrent_dropout=0.5)
        return gru

    def create_network(self):
        input_ = tf.keras.layers.Input(shape = (IM_H//2, IM_W, IM_C))
        x = self.CNN(input_)
        '''x = tf.keras.layers.Dense(512, 'relu')(x)
        x = tf.keras.layers.Dropout(0.5)(x)'''
        x = tf.keras.layers.Dense(256, 'elu')(x)
        x = tf.keras.layers.Dropout(0.5)(x)
        x = tf.keras.layers.Dense(32, 'elu')(x)
        x = tf.keras.layers.Dropout(0.5)(x)
        x = tf.keras.layers.Dense(3, 'linear')(x)
        my_network = tf.keras.Model(input_, x)
        return my_network

'''
mn = My_Network()
model = mn.create_network()
model.summary()
'''