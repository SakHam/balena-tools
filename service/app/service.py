from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from init import WAIT_SECONDS,status,ports,event
import socket
import os
import time, threading
import commands

API_KEY = "F6PWd6lsPzNnjsRbqtGuJQfXPUcbwVb6"


app = Flask(__name__)

#3 options, load, start and stop the new service 
@app.route('/service/',methods = ['POST'])
def service():

  service = request.args.get('service','')
  path = request.args.get('path','')
  #Start the new service that we loaded before. Its hardcoded the name of that service
  if service == "start":
    cmd = 'curl --header "Content-Type:application/json" "http://127.0.0.1:48484/v2/applications/1/start-service?apikey=' + API_KEY + '" -d \'{"serviceName": "edgex-device-virtual"}\''
    os.system(cmd)
    return "start ok"
  #Stop the new service that we loaded before. Its hardcoded the name of that service
  elif service == "stop":
    cmd = 'curl --header "Content-Type:application/json" "http://127.0.0.1:48484/v2/applications/1/stop-service?apikey=' + API_KEY + '" -d \'{"serviceName": "edgex-device-virtual"}\''
    os.system(cmd)
    return "stop ok"	
  #Load the new service that we upload before the tar file, using the unix-socket
  elif service == "load":
    os.system('curl --verbose --unix-socket /var/run/balena.sock --request POST --header "Content-Type: application/x-tar" --data-binary @'+ path + ' http://localhost/images/load')	
    return "load ok"	
  else:
    os.system("echo not valid args")
    return "not valid args"

#Upload the new service in tar file format
@app.route('/upload1',methods = ['POST'])
def upload_tar():
  global ports
  global event

  file1 = request.files['img']
  
  file1.save("device-virtual.tar")

  os.system("echo load command sent")
  return "tar files successfully saved"

#Upload a txt file with 2 settings ip that want to check as event and ports of the new service
@app.route('/upload2',methods = ['POST'])
def upload_conf():
  global ports
  global event

  file2 = request.files['conf']
  file2.save("conf.txt")

  fp=open('/python_balena/conf.txt','r')
  for x in fp.readlines():
    if x[0:5] == "ports":
      ports = x[6:]
      print(ports)
    elif x[0:6]=="events":
      event = x[7:]
      print(event)

  fp.close()

  return "conf files successfully saved"

#get the status of the services
@app.route('/status',methods = ['GET'])
def get_status():
  status = commands.getoutput('curl "http://127.0.0.1:48484/v2/state/status?apikey="' + API_KEY )
  return status

#Function that check if Ip tis online(every 10 seconds). If its not online, open the target-state file, modify the ports of the new service
#and set the target-state that points to all services that needed to run
def check():
  global status
  global event
  global ports
  print("checking Event") 
  if len(event) > 4:
    response = os.system("ping -c 1 " + event)
    if response == 0 and status == "0":
      print('is up!')
      print("ip is online")
      print("Global ip is")
      print(event)
    else:
      print('is down!')
      print(event)
      print("ip is offline")
      
      #add the ports to target
      fp1=open('target_start.sh','r+')

      y=str(fp1.read())
      sub_index0 = y.find('edgex-device-virtual')
      sub_index1 = y[sub_index0:].find('internalStart')
      x2=y[0:sub_index0+sub_index1+len("internalStart")+2] + ports + y[sub_index0+sub_index1+len("internalStart")+2:]
      x02 = x2.find('edgex-device-virtual')
      sub_index2 = x2[x02:].find('internalEnd')
      x3=x2[0:x02+sub_index2+len("internalEnd")+2] + ports + x2[x02+sub_index2+len("internalEnd")+2:]
      x03 = x3.find('edgex-device-virtual')
      sub_index3 = x3[x03:].find('externalStart')
      x4=x3[0:x03 + sub_index3+len("externalStart")+2] + ports + x3[x03+sub_index3+len("externalStart")+2:]
      x04 = x4.find('edgex-device-virtual')
      sub_index4 = x4[x04:].find('externalEnd')
      x5=x4[0:x04+sub_index4+len("externalEnd")+2] + ports + x4[x04+sub_index4+len("externalEnd")+2:]
      fp1.seek(0)
      fp1.write(x5)
      fp1.close()
	  
      os.system('chmod +x target_start.sh')
      os.system('./target_start.sh')
      os.system('curl --header "Content-Type:application/json" "http://127.0.0.1:48484/v2/applications/1/restart-service?apikey="' + API_KEY + ' -d \'{"serviceName": "app"}\'')

  
  threading.Timer(WAIT_SECONDS, check).start()
  return "check Event OK"
    
    
check()



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
