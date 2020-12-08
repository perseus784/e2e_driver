import numpy as np
import os
import random
from config import *


class data_tools:
    def __init__(self,data_folder):
        self.data_folder = data_folder
        self._data = os.listdir(self.data_folder)

    def batch_dispatch(self):
        counter = 0
        random.shuffle(self._data)
        while counter<=len(self._data):
            np_data = np.load(os.path.join(self.data_folder,self._data[counter]), allow_pickle=True)
            images_ = np_data["image"]
            controls_ = np_data["controls"]
            images_ = (images_/127.5)-1.0
            counter += 1
            for i in range(0 , max_sample_size, batch_size):
                images = images_[i:i+batch_size]
                #semantic = images_[i:i+batch_size,1]
                #waypoints = np_data['waypoints'][i:i+batch_size]
                controls =  controls_[i:i+batch_size]
                yield images, controls
            if counter>=len(self._data):
                break
'''
dt = data_tools(os.path.join('data','final_processed'))
train_generator = dt.batch_dispatch()
for n, i in enumerate(train_generator):
    images, semantic, labels = i
    print(images.shape, semantic.shape, labels.shape)
'''
'''
class Train_Class:

    def __init__(self):
        self.model = My_Network()
        self.optimizer = tf.keras.optimizers.Adam()
        self.tf_writer = tf.summary.create_file_writer(tensorlogs)

        #self.tensorboard_callback.set_model(self.model)
        #self.model_save_callback.set_model(self.model)

    def calculate_loss(self, ground_truth, prediction):
        acc_loss = tf.keras.losses.mean_squared_error(ground_truth[:, 0], prediction[0])
        steer_loss = tf.keras.losses.mean_squared_error(ground_truth[:, 1], prediction[1])
        brake_loss = tf.keras.losses.mean_squared_error(ground_truth[:, 2], prediction[2])
        loss = tf.reduce_sum([acc_loss, steer_loss, brake_loss])

        return loss

    @tf.function
    def train_step(self, images, labels):
        with tf.GradientTape() as tape:
            predictions = self.model(images)
            loss = self.calculate_loss(labels, predictions)
        gradients = tape.gradient(loss, self.model.trainable_variables)
        gradients = [tf.clip_by_norm(gradient, 10) for gradient in gradients]
        self.optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))
        return loss

    @tf.function
    def train_model(self):

        for epoch in tqdm(range(EPOCHS)):
            epoch_loss = []
            train_generator = data_tools(data_collection_path).batch_dispatch()

            for n, i in enumerate(train_generator):
                images, labels = i
                loss = tf.reduce_mean(self.train_step(images, labels))
                epoch_loss.append(loss)
                with self.tf_writer.as_default():
                    tf.summary.scalar("batch loss", data=loss, step = n)

            with self.tf_writer.as_default():
                tf.summary.scalar("epoch loss", data=tf.reduce_mean(epoch_loss), step = epoch)

            if epoch%30 ==0:
                self.model.save_weights(model_save_folder.format(epoch))


'''