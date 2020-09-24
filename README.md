# ai_in_wheels

Python 3.7
## Carla setup:
download carla for windows from here: https://github.com/carla-simulator/carla/releases/tag/0.9.9 (0.9.9.4) and extract the file.
More info here: https://carla.readthedocs.io/en/latest/start_introduction/

while you can operate from the PythonAPI folder, I perfer it installed globally. So, you can find the python egg inside CARLA_0.9.9.4\WindowsNoEditor\PythonAPI\carla\dist and put it inside C:\Users\%username%\AppData\Local\Programs\Python\Python37\Lib\site-packages and extract it there. If this doesnt work, use easy_install to install the egg file.

Running carla in server mode: CarlaUE4.exe -ResX=420 -ResY=280 -carla-server -fps=10 -carla-world-port=7878 -quality-level=Low
port is changed since it dint work for me, you can use a different port and connect via PythonAPI using the same.


 
 
