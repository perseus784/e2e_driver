import numpy as np
import tensorflow as tf
from model_architecture import My_Network
from config import *
from utils import data_tools
import json
import os
from tqdm import tqdm

gpu_devices = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(gpu_devices[0], True)

class Train_Class:

    def __init__(self):
        self.learning_rates = [1e-3, 1e-4, 1e-5]
        self.model = My_Network().create_network()
        self.optimizer = tf.keras.optimizers.Adam(learning_rate=1e-5)
        self.tf_writer = tf.summary.create_file_writer(tensorlogs)

        #self.tensorboard_callback.set_model(self.model)
        #self.model_save_callback.set_model(self.model)

    @tf.function
    def train_step(self, images, labels):
        with tf.GradientTape() as tape:
            predictions = self.model(images)
            loss = tf.keras.losses.mean_squared_error(labels, predictions)
        gradients = tape.gradient(loss, self.model.trainable_variables)
        #gradients = [tf.clip_by_norm(gradient, 10) for gradient in gradients]
        self.optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))
        return loss

    def train_model(self):
        counter = 0
        #lr_counter = 0
        for epoch in tqdm(range(EPOCHS)):
            epoch_loss = []
            epoch_test_loss = []
            train_generator = data_tools(train_path).batch_dispatch()
            '''if epoch%(EPOCHS//3)==0:
                if lr_counter>len(self.learning_rates):
                    ln_rate = self.learning_rates[-1]
                else:
                    ln_rate = self.learning_rates[lr_counter]
                self.optimizer = tf.keras.optimizers.Adam(learning_rate=ln_rate)
                lr_counter+=1
            with self.tf_writer.as_default():
                    tf.summary.scalar("learning_rate", data=ln_rate, step = counter)'''
            for n, i in tqdm(enumerate(train_generator)):
                images, labels = i
                loss = tf.reduce_mean(self.train_step(images, labels))
                epoch_loss.append(loss)
                with self.tf_writer.as_default():
                    tf.summary.scalar("batch/train_loss", data=loss, step = counter)
                if counter%200 ==0:
                    test_avg_loss = []
                    test_generator = data_tools(test_path).batch_dispatch()
                    for nn, j in enumerate(test_generator):
                        test_images, test_labels = j
                        test_predictions = self.model(test_images)
                        test_loss = tf.keras.losses.mean_squared_error(test_labels, test_predictions)
                        test_avg_loss.append(test_loss)
                        if nn==4:
                            break
                    all_test_loss = tf.reduce_mean(test_avg_loss)
                    epoch_test_loss.append(all_test_loss)
                    with self.tf_writer.as_default():
                        tf.summary.scalar("batch/test_loss", data=all_test_loss, step = counter)
                counter += 1

            with self.tf_writer.as_default():
                tf.summary.scalar("epoch/train_loss", data=tf.reduce_mean(epoch_loss), step = epoch)
            with self.tf_writer.as_default():
                tf.summary.scalar("epoch/test_loss", data=tf.reduce_mean(epoch_test_loss), step = epoch)  

            self.model.save_weights(model_save_folder.format(epoch))
            
c = Train_Class()
c.train_model()


