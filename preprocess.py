import cv2
import numpy as np
import os,sys,random,time
from config import *
import shutil

all_files = os.listdir(data_collection_path)
data_queue = []

def store_data(n , data_queue, direction):

    data_queue = list(zip(*data_queue))
    save_path = os.path.join('data',"processed",'{}','{}.npz')
    np.savez(save_path.format(direction,str(n)), image=np.array(data_queue[0], dtype=np.uint8), controls=np.array(data_queue[1], dtype=np.float32))

def clean_data():
    left_queue, right_queue, center_queue = [],[],[]
    for n, j in enumerate(all_files):
        np_data = np.load(os.path.join(data_collection_path, j), allow_pickle=True)
        images = np_data["image"]
        controls = np_data["controls"]
        steer_counter = [0,0,0]

        for i in range(data_max_sample_size):
            if controls[i][1]>0.1:
                steer_counter[2] = steer_counter[2]+1
                flipped_image = cv2.flip( images[i][0], 1 )
                flipped_sem = cv2.flip( images[i][1], 1)
                flipped_controls = [controls[i][0], -controls[i][1],controls[i][2]]
                right_queue.append([images[i], controls[i]])
                left_queue.append([[flipped_image,flipped_sem],flipped_controls])
            elif controls[i][1]<-0.1:
                steer_counter[0] = steer_counter[0]+1
                flipped_image = cv2.flip( images[i][0], 1 )
                flipped_sem = cv2.flip( images[i][1], 1 )
                flipped_controls = [controls[i][0], -controls[i][1],controls[i][2]]
                left_queue.append([images[i], controls[i]])
                right_queue.append([[flipped_image,flipped_sem],flipped_controls])

            elif -0.01<controls[i][1]<0.01:
                steer_counter[1] = steer_counter[1]+1
                if i%3==0:
                    center_queue.append([images[i], controls[i]])

            if len(right_queue)==max_sample_size:
                store_data(n,right_queue,"right")
                right_queue=[]
            if len(center_queue)==max_sample_size:
                store_data(n,center_queue,"center")
                center_queue=[]
            if len(left_queue)==max_sample_size:
                store_data(n,left_queue,"left")
                left_queue=[]

def shuffle_data():
    left_files = os.listdir(os.path.join('data',"processed",'left'))
    right_files = os.listdir(os.path.join('data',"processed",'right'))
    center_files = random.sample(os.listdir(os.path.join('data',"processed",'center')), len(left_files))
    counter = 0
    for left, center, right in zip(left_files, center_files, right_files):

        l_np_data = np.load(os.path.join('data',"processed",'left',left), allow_pickle=True)
        l_images = l_np_data["image"][:,0] #remove [:,0] for getting semantic too
        l_controls = l_np_data["controls"]

        r_np_data = np.load(os.path.join('data',"processed",'right',right), allow_pickle=True)
        r_images = r_np_data["image"][:,0]
        r_controls = r_np_data["controls"]

        c_np_data = np.load(os.path.join('data',"processed",'center',center), allow_pickle=True)
        c_images = c_np_data["image"][:,0]
        c_controls = c_np_data["controls"]

        all_images = np.concatenate([l_images,r_images,c_images])
        all_controls = np.concatenate([l_controls,r_controls,c_controls])
        indices = np.arange(all_images.shape[0])
        np.random.shuffle(indices)
        all_images = all_images[indices]
        all_controls = all_controls[indices]
        print(all_images.shape)
        np.savez(os.path.join('data','final_processed','{}.npz').format(str(counter)), image=np.array(all_images, dtype=np.uint8), controls=np.array(all_controls, dtype=np.float32))

        counter+=1

def split_data():
    processed_files = os.listdir(processed_data_path)
    random.shuffle(processed_files)
    split = int(len(processed_files)*0.85)
    train_files = processed_files[:split]
    test_files = processed_files[split:]
    for i in train_files:
        shutil.copy2(os.path.join(processed_data_path,i), train_path)
    for j in test_files:
        shutil.copy2(os.path.join(processed_data_path,j), test_path)

'''
clean_data()
shuffle_data()
split_data()
'''



