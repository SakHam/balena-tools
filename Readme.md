# Exploring useful Balena Tools


In this project  we use an example to show some of the useful tools of Balena like Balena Supervisor API, balena cli etc. Use BalenaOs which is installed in a RaspberryPi3 device (see https://www.balena.io/docs/learn/getting-started/raspberrypi3/nodejs/#adding-your-first-device).
Use balena device in local mode (see https://www.balena.io/docs/learn/develop/local-mode/). I implemented a service in python that communicate outside the HostOS through an API and uses the Balena tools  to upload Load and run a dockerized service automatically. 


# Getting Started

In our case, as services we choose some of edgexFoundry Microservices.
So before use the "service" its necessary to have already uploaded the images of EdgeXFoundry Microservices that we will use, inside the balena docker engine.
In our case we have already uploaded the images : volume:0.8.0, consul:1.4, edgex-core-config-seed:0.7.1, edgex-mongo:0.8.0, edgex-support-logging:0.7.1, edgex-support-notifications:0.7.1, edgex-core-metadata:0.7.1,edgex-core-data:0.7.1,edgex-core-command:0.7.1 from https://hub.docker.com/u/edgexfoundry/ by pulling them from inside Balena HOST using "balena pull" command or by pushing the edgex compose-file (https://github.com/edgexfoundry/developer-scripts/tree/master/releases/edinburgh/compose-files) directly to 
balena device and deleting only the running containers (see https://www.balena.io/docs/reference/cli/). After that remain only the images inside the balena docker engine.
We have also pull an edgex Microservice (in this case the device-virtual) to another place, not in balena device, and save it as tar file(e.g. in our computer)
Additional we use a conf.txt file to define some very basic settings. These two files are in folder "Upload".
The idea is that using our "service", we can POST some commands to balena device using our own API and depends on that settings the service can load a new service automatically
For testing the functions of that service need the balena device be in local mode and a computer in same network with balena device.
Using balena cli we can run the command "balena local scan",from our computer, to see the ip of the device (Device_IP)
After that cd to directory where contains the folder "service" and run the  command "balena push Device_IP".
If you go to balena terminal of your device you will see running a new container. This is our  service
From your computer, using any tool you want (i use Postman),  you can make some POST from your pc to balena device service.
Before pushing the service to balena-engine you have to replace inside the file "service.py" the API_KEY of your device. You also mush change the field "hostname" inside the docker-compose.yml file. You should use your device hostname 
## Testing the functions of the service
### POST upload tar file (http://Device_IP:5000/upload2)

Using key name "img" and selecting the value as file the tar file of the service we want(here the device-virtual.tar), upload the tar file to the central service.

### POST load the image of the new service (http://Device_IP:5000/service/?service=load&path=device-virtual.tar)

We use two arguments to that Post.The first with key name "service" set it as "load" and the second with key name "path" set it as the name of the file we uploaded
before ("device-virtual.tar). The load of the image from the tar file happens through the balena unix:socket which is exposed using specific labels to our compose-file 
(see https://www.balena.io/docs/learn/develop/multicontainer/)

### POST upload configuration file (http://Device_IP:5000/upload2)

Using key name "conf" and select value as file the "conf.txt" file. In our case this file containes only two parameters.
The Ip that we will check if is online or offline and the Ports that it runs the service we uploaded before. In our case is the port 4990.
Of course this is only an example. Anyone can load more configuration settings to this file and processing them as need inside the service.

### POST: stop/start the service (http:// Device_IP:5000/service/?service=stop or http:// Device_IP:5000/service/?service=start)
You can use these 2 commands (stop and start) after the new service start to runs. 
## Functionality

After the upload of conf.txt file the "service" is checking every 10 seconds if the IP that is inside the conf.txt file is online or offline(just use the
output of the ping IP). 
If the IP is offline it opens the file(raget_state.sh) where we  save the set target-state command (see Set a target state to https://www.balena.io/docs/reference/supervisor/supervisor-api/) and writes the "ports" thats are in conf.txt file, to specific fields, that shows the "ports" that uses the new service that we want to run.
By this command we point which images (services) will start running and some basic configuration of the parapeters of these services (containers) like the Ports (internal and external), network_mode, entrypoints etc.
In our user case all the parameters are hardcoded except the ports of the new service that we load before (device-virtual).
So depends on which services you want to start using the set target-state, you have to change a lot of parameters. For example in the field "image":"YourImageName" you can set the image name that you want to run (YourImageName). Be careful cause the field "image" should have the image name exactly as it is in your balena image list.
So after that if you go to terminal of HostOs of your device and run the comand "balena -ps -a", you will see running all the services that that points the set target-state that we used.
