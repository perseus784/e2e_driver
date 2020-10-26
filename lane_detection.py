import os, sys, random, time
import carla
import numpy as np
import cv2
from config import *

# create main carla objects
client = carla.Client('localhost', 7878)
client.set_timeout(5)
world = client.get_world()
#print(world.get_settings())
blueprint_library = world.get_blueprint_library()
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(os.path.join('data' , 'man360grey.avi'), fourcc, 10.0, (IM_W, IM_H))
kernel = np.ones((2, 1), np.uint8)

class Carla_session:

    def __init__(self):
        self.actors = []
        self.counter = 0
        self.collision_flag = False
        self.episode_images = []
        self.env_actors = []
        self.lane_angle = 0
        self.blank = np.zeros((IM_H, IM_W, 1), np.uint8)
        mask_shape = np.array([[ [IM_W-int(IM_W*.35), int(IM_H*0.2)], [0+int(IM_W*.35),int(IM_H*0.2)], [0+int(IM_W*.18),IM_H], [IM_W-int(IM_W*.18), IM_H]]])
        self.mask = cv2.fillPoly(self.blank[:], [mask_shape], (255, 255, 255))

    def add_vehicles(self):
        env_vehicles_bp = blueprint_library.filter('vehicle.*')
        env_vehicles_bp = [x for x in env_vehicles_bp if int(x.get_attribute('number_of_wheels')) == 4]
        env_vehicles_bp = [x for x in env_vehicles_bp if not x.id.endswith('isetta')]
        env_vehicles_bp = [x for x in env_vehicles_bp if not x.id.endswith('carlacola')] 
        spawn_points = world.get_map().get_spawn_points()      
        SpawnActor = carla.command.SpawnActor
        SetAutopilot = carla.command.SetAutopilot
        FutureActor = carla.command.FutureActor
        self.env_actors = []
        for n, transform in enumerate(spawn_points):
            if n >= number_env_vehicles:
                break
            env_vehicle_bp = random.choice(env_vehicles_bp)
            if env_vehicle_bp.has_attribute('color'):
                env_vehicle_bp.set_attribute('color', random.choice(env_vehicle_bp.get_attribute('color').recommended_values))
            env_vehicle_bp.set_attribute('role_name', 'autopilot')
            env_vehicle = world.spawn_actor(env_vehicle_bp, transform)
            env_vehicle.set_autopilot(True)
            self.env_actors.append(env_vehicle)

    def add_actors(self):

        #start_point = random.choice(world.get_map().get_spawn_points())
        start_point = carla.Transform(carla.Location(x=83.276306, y=-79.507767, z=8.305596), carla.Rotation(pitch=0.000000, yaw=-87.975883, roll=0.000000))
        #set vehicle
        vehicle_bp = blueprint_library.find('vehicle.tesla.cybertruck')
        self.vehicle = world.spawn_actor(vehicle_bp, start_point)
        #self.vehicle.set_autopilot(True)

        #get and set sensors
        collision_sensor_bp = blueprint_library.find('sensor.other.collision')
        lane_invasion_sensor_bp = blueprint_library.find('sensor.other.lane_invasion')
        camera_sensor_bp = blueprint_library.find('sensor.camera.rgb')
        camera_sensor_bp.set_attribute('image_size_x', str(IM_W))
        camera_sensor_bp.set_attribute('image_size_y', str(IM_H))
        #camera_sensor_bp.set_attribute('sensor_tick',str(time_step))
        camera_sensor_bp.set_attribute('fov', str(100))

        sensor_location = carla.Transform(carla.Location(x=4, y=0, z=2.5))
        self.camera = world.spawn_actor(camera_sensor_bp, sensor_location, attach_to=self.vehicle)
        self.collision_sensor = world.spawn_actor(collision_sensor_bp, sensor_location, attach_to=self.vehicle)
        #self.lane_invasion_sensor = world.spawn_actor(lane_invasion_sensor_bp, sensor_location, attach_to = self.vehicle)
        self.actors.extend([self.vehicle, self.camera, self.collision_sensor])
        self.camera.listen(lambda image: self.add_image(image))
        #self.collision_sensor.listen(lambda collision: self.end_seq(collision, 'collision'))  

        #self.lane_invasion_sensor.listen(lambda lane_inv: self.end_seq(lane_inv,'crossed lane'))

    def start_new_seq(self):
        self.add_actors()
        self.collision_flag = False
        print('starting new seq')
        self.counter = 0
        time.sleep(30)

    def process_angle(self, image):
        pass

    def line_intersection(self, line1, line2):
        xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)
        if div == 0:
            raise False

        d = (det(*line1), det(*line2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        return x, y

    def lane_detection(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bitwise_and(gray, self.mask) # apply mask
        _, th = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)
        opening = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)
        blurred = cv2.medianBlur(opening, 1) #smoothening
        edges = cv2.Canny(blurred, 10, 250, apertureSize=7)# edge detection
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 80, np.array([]), 40, 100) #hough probalistic
        image = np.array(image)
        cv2.imshow('mask', self.mask)
        cv2.imshow('gray', gray)
        cv2.imshow('th', th)
        cv2.imshow('edges', edges)
        blank = np.zeros((IM_H, IM_W, 1), np.uint8)
        #imaginary_lines = [[[0,i],[w,i]] for i in range(0,h,30)]
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.line(blank, (x1, y1), (x2, y2), (255, 255, 255), 2)
        #self.process_angle(blank)
        #cv2.imshow('blank', blank)
        return image

    def add_image(self, image):
        self.counter += 1
        img = np.reshape(image.raw_data, (IM_H, IM_W, 4))
        img = img[:, :, :3][:]
        #self.episode_images.append(img)
        
        #cv2.imwrite(os.path.join(image_save_path,str(self.n_seq),'{}.png'.format(self.counter)),img)
        '''if self.counter%15 == 0:
            self.n_seq += 1
            self.counter = 0
            if not os.path.exists(os.path.join(image_save_path,str(self.n_seq))):
                os.makedirs(os.path.join(image_save_path,str(self.n_seq)))'''

        #out.write(img)
        cv2.imshow("lane", self.lane_detection(img))
        cv2.imshow("live", img)
        cv2.waitKey(1)

    def save_images(self):
        #print(os.path.join(image_save_path,str(self.n_seq),'{}.png'.format(self.counter)))
        for ind, img in enumerate(self.episode_images[-seq_len:]):
            cv2.imwrite(os.path.join(image_save_path, str(self.n_seq), '{}.png'.format(ind)), img)
    
    def end_seq(self, cause_obj, cause):
        self.destroy_actors()
        self.collision_flag = True
        print("collision happened")
        #self.delete_images()

    def destroy_actors(self):
        for actor in self.actors:
            print(actor)
            actor.destroy()

        #self.save_images()
        self.actors = []
        #self.episode_images =[]
    
    def get_directions(self):
        thr = random.choice([0.8, 0.7, 0.6])
        steer = random.choice([-0.3, 0.0, 0.0, 0.0, 0.3, 0.1, -0.1])
        return carla.VehicleControl(0.3, 0.0)  
        
    def drive_around(self, episodes):
        try:
            self.start_new_seq()
            for j in range(200):
                self.vehicle.apply_control(self.get_directions())
                time.sleep(0.1)

                '''if self.collision_flag:
                    break'''
            #out.release()   
            self.destroy_actors()

        except Exception as e:
            print(e)

        '''for i in self.env_actors:
            i.destory()
        self.env_actors =[]'''


c = Carla_session()
c.drive_around(10)