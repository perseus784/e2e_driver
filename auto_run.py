import os,sys,random,time
import carla
import numpy as np
import cv2
from config import *

#create main carla objects
client = carla.Client('localhost',CARLA_PORT)
client.set_timeout(5)
world = client.load_world(TOWN)
blueprint_library = world.get_blueprint_library()

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
        from carla_route_finder.global_route_planner_dao import GlobalRoutePlannerDAO
        from carla_route_finder.global_route_planner import GlobalRoutePlanner
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
            world.debug.draw_string(point[0].transform.location,'O', color=carla.Color(r=255, g=0, b=0), life_time=120.0, persistent_lines=True)

    def calculate_waypoints(self):
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

    def add_env_vehicles(self):
        env_vehicles_bp = blueprint_library.filter('vehicle.*')
        env_vehicles_bp = [x for x in env_vehicles_bp if int(x.get_attribute('number_of_wheels')) == 4]
        env_vehicles_bp = [x for x in env_vehicles_bp if not x.id.endswith('isetta')]
        env_vehicles_bp = [x for x in env_vehicles_bp if not x.id.endswith('carlacola')] 
        spawn_points = world.get_map().get_spawn_points()      
        self.env_actors = []
        for n, transform in enumerate(spawn_points):
            if n >= number_env_vehicles:
                break
            env_vehicle_bp = random.choice(env_vehicles_bp)
            if env_vehicle_bp.has_attribute('color'):
                env_vehicle_bp.set_attribute('color', random.choice(env_vehicle_bp.get_attribute('color').recommended_values))
            env_vehicle_bp.set_attribute('role_name', 'autopilot')
            env_vehicle = world.spawn_actor(env_vehicle_bp,transform)
            env_vehicle.set_autopilot(True)
            self.env_actors.append(env_vehicle)

    def random_world_setter(self):
        pass

    def conditional_world_setter(self):
        pass

    def add_agent(self):
        start_point = random.choice(world.get_map().get_spawn_points())
        vehicle_bp = blueprint_library.find('vehicle.audi.a2')
        self.vehicle = world.spawn_actor(vehicle_bp,start_point)
        camera_sensor_bp = self.add_camera()
        sensor_location = carla.Transform(carla.Location(x=0,y=0,z=2.5))
        self.camera = world.spawn_actor(camera_sensor_bp, sensor_location, attach_to = self.vehicle)
        self.camera.listen(lambda image: self.add_image(image))
        self.agent_actors.extend([self.vehicle, self.camera])

    def add_image(self, image):
        self.counter += 1
        img = np.reshape(image.raw_data,(IM_H,IM_W,4))
        img = img[:,:,:3][:]
        cv2.imshow("live",img)
        cv2.waitKey(1)

    def add_sensors(self):
        pass
    
    def start_new_sequence(self):
        pass

    def destroy_actors(self, actors):
        print("destroing actors")
        for actor in actors:
            actor.destroy()

    def get_controls(self):
        pass
    
    def drive(self):
        #self.add_env_vehicles()
        self.add_agent()

        #find_route
        self.find_route(self.vehicle.get_location(), self.get_destination())


        self.vehicle.set_autopilot(True)
        time.sleep(60*2)
        map(self.destroy_actors, [self.env_actors,self.agent_actors])


cs = CarlaSession()
cs.drive()




