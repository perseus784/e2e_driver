import os,sys,random,time
import carla
import numpy as np
import cv2
from config import *
import keyboard as kb
from carla_route_finder.global_route_planner_dao import GlobalRoutePlannerDAO
from carla_route_finder.global_route_planner import GlobalRoutePlanner
from carla_route_finder import misc 
from carla_route_finder.basic_agent import BasicAgent

#create main carla objects
client = carla.Client('localhost',CARLA_PORT)
client.set_timeout(5)
world = client.load_world(TOWN)
settings = world.get_settings()
settings.synchronous_mode = True # Enables synchronous mode
settings.fixed_delta_seconds = 0.01
world.apply_settings(settings)
blueprint_library = world.get_blueprint_library()
tm = client.get_trafficmanager(4040)
tm.set_synchronous_mode(True)

class Carla_Sensors:
    def __init__(self):
        self.sensors=[]

    def add_camera(self):
        camera_sensor_bp = blueprint_library.find('sensor.camera.rgb')
        camera_sensor_bp.set_attribute('image_size_x',str(IM_W))
        camera_sensor_bp.set_attribute('image_size_y',str(IM_H))
        #camera_sensor_bp.set_attribute('sensor_tick',str(time_step))
        camera_sensor_bp.set_attribute('fov',str(100))
        self.sensors.append(camera_sensor_bp)
        return camera_sensor_bp

    def add_lidar(self):
        pass

    def add_collision(self):
        collision_sensor_bp = blueprint_library.find('sensor.other.collision')
        self.sensors.append(collision_sensor_bp)
        return collision_sensor_bp

    def lane_invasion(self):
        lane_invasion_sensor_bp = blueprint_library.find('sensor.other.lane_invasion')
        self.sensors.append(lane_invasion_sensor_bp)
        return lane_invasion_sensor_bp

    def add_depth(self):
        pass
    def add_semantic(self):
        pass
    def add_GNSS(self):
        pass
    def add_IMU(self):
        pass

class Carla_Navigation:
    def __init__(self):
        self.map = world.get_map()
        dao = GlobalRoutePlannerDAO(self.map, waypoint_resolution)
        grp = GlobalRoutePlanner(dao)
        grp.setup()
        self.grp = grp

    def get_destination(self):
        spawn_point = random.choice(self.map.get_spawn_points())    
        return spawn_point

    def find_route(self, current_location, destination_location):
        current_location = self.map.get_waypoint(current_location)
        destination_location = self.map.get_waypoint(destination_location.location)
        route_waypoints = self.grp.trace_route(current_location.transform.location, destination_location.transform.location)
        for point in route_waypoints:
            world.debug.draw_string(point[0].transform.location,'O', color=carla.Color(r=255, g=0, b=0), life_time=10.0, persistent_lines=True)
        waypoints, road_options = zip(*route_waypoints)
        return waypoints, road_options

    def check_actors_in_course(self,current_location, env_actors):

        '''crr = carla.Location(x=current_location.x, y=current_location.y, z=current_location.z)
        world.debug.draw_string(crr,'x', color=carla.Color(r=0, g=255, b=0), life_time=10.0, persistent_lines=True)
        '''
        for actor in env_actors:
            loc = actor.get_transform()
            angle, check = misc.is_within_distance_ahead(loc, current_location, watchout_distance)
            if check:
                return check
            '''difference = np.array([loc.x-current_location.x, loc.y-current_location.y, loc.z-current_location.z])
            distance = np.linalg.norm(difference)
            if distance<10:
                return True
            else:
                return False'''
        return False

        
    def calculate_speed(self, ideal_speed, current_speed):

        pass
    def calculate_steer(Self):
        pass
    def find_new_control(self):
        pass

class CarlaSession(Carla_Sensors, Carla_Navigation):

    def __init__(self):
        Carla_Sensors.__init__(self)
        Carla_Navigation.__init__(self)
        self.agent_actors = []
        self.counter = 0
        self.env_actors = []   
        self.save = [] 

    def add_env_vehicles(self):
        env_vehicles_bp = blueprint_library.filter('vehicle.*')
        env_vehicles_bp = [x for x in env_vehicles_bp if int(x.get_attribute('number_of_wheels')) == 4]
        env_vehicles_bp = [x for x in env_vehicles_bp if not x.id.endswith('isetta')]
        env_vehicles_bp = [x for x in env_vehicles_bp if not x.id.endswith('carlacola')] 
        spawn_points = world.get_map().get_spawn_points()    
        random.shuffle(spawn_points)
        
        self.env_actors = []
        for n, transform in enumerate(spawn_points):
            if n >= number_env_vehicles:
                break
            env_vehicle_bp = random.choice(env_vehicles_bp)
            if env_vehicle_bp.has_attribute('color'):
                env_vehicle_bp.set_attribute('color', random.choice(env_vehicle_bp.get_attribute('color').recommended_values))
            env_vehicle_bp.set_attribute('role_name', 'autopilot')
            env_vehicle = world.spawn_actor(env_vehicle_bp,transform)
            env_vehicle.set_autopilot(True, tm.get_port())
            self.env_actors.append(env_vehicle)

    def random_world_setter(self):
        pass

    def conditional_world_setter(self):
        pass
    

    def add_agent(self):
        start_point = random.choice(world.get_map().get_spawn_points())
        vehicle_bp = blueprint_library.find('vehicle.audi.a2')
        self.vehicle = world.spawn_actor(vehicle_bp,start_point)
        self.vehicle.set_location(start_point.location)
        camera_sensor_bp = self.add_camera()
        sensor_location = carla.Transform(carla.Location(x=0,y=0,z=2.5))
        self.camera = world.spawn_actor(camera_sensor_bp, sensor_location, attach_to = self.vehicle)
        self.agent_actors.extend([self.vehicle, self.camera])
 
    def add_image(self, image):
        self.counter += 1

        img = np.reshape(image.raw_data,(IM_H,IM_W,4))
        self.camera_image = img[:,:,:3][:]
         
        '''cv2.imshow("live",img)
        cv2.waitKey(1)'''

    def add_sensors(self):
        pass
    
    def start_new_sequence(self):
        pass

    def destroy_actors(self, actors):
        print("destroying actors")
        for actor in actors:
            actor.destroy()
        return ""

    def get_controls(self, current_point, next_point):
        thr = random.choice([0.8,0.7,0.6])
        steer = random.choice([-0.3,0.0,0.0,0.0,0.3,0.1,-0.1])
        return throttle, steer, brake

    def store_data(self, data_queue):
        data_queue = list(zip(*data_queue))
        save_path = os.path.join(data_collection_path,'{}.npz'.format(self.counter))
        np.savez(save_path, image=data_queue[0], wayopints=data_queue[1], controls=[2])

    def drive(self):
        #self.add_env_vehicles()
        self.add_agent()
        world.tick()
        time.sleep(2)
        self.camera.listen(lambda image: self.add_image(image))
        world.tick()
        b_agent = BasicAgent(self.vehicle, 20, world)
        destination = self.get_destination()
        route_waypoints, road_options = self.find_route(self.vehicle.get_location(), destination)
        b_agent.set_destination(destination)
        data_queue=[]
        while True:
            if b_agent.done():
                print("Reached destination")
                break
            control, _waypoints = b_agent.run_step()
            waypoints =[[wp[0].transform.location.x,wp[0].transform.location.y,wp[0].transform.location.z]  for wp in _waypoints]
            data_queue.append([self.camera_image, waypoints, [control.throttle, control.steer, control.brake]])
            if len(data_queue)==32:
                self.store_data(data_queue)
                data_queue=[]
            cv2.imshow("live",self.camera_image)
            cv2.waitKey(1)
            self.vehicle.apply_control(control)
            world.tick()


        '''
        #find_route
        route_waypoints, road_options = self.find_route(self.vehicle.get_location(), self.get_destination())
        #print(route_waypoints)
        continue_loop = True
        thr, steer, brake, reverse = 0, 0, 0, 0
        while continue_loop:
            world.tick()
            if 
            
            try:
                if kb.is_pressed('w'):
                    thr = random.choice([0.3, 0.4])
                    steer = 0
                elif kb.is_pressed('a'):
                    steer = -0.2
                    thr = 0.3
                elif kb.is_pressed('d'):
                    steer = 0.2   
                    thr = 0.3
                elif kb.is_pressed('x'):
                    steer = 0
                    thr = 0   
                    brake = 1  
                elif kb.is_pressed('r'):
                    thr = 0.5   
                    reverse =1
                elif kb.is_pressed('l'):
                    continue_loop=False

            except:
                pass     


            if current_point == next_point:
                continue_loop = False
                break
            close_vehicles = self.check_actors_in_course(self.vehicle.get_transform(), self.env_actors)
            if close_vehicles:
                brake=1'''                
            
            #throttle, steer, brake = self.get_controls()
            #check for red flags in the env like cars or traffic lights before you in a certain distance
            #hhow???????


        list(map(self.destroy_actors, [self.env_actors,self.agent_actors]))


cs = CarlaSession()
cs.drive()




