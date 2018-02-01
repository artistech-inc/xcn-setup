import zmq
import random
import sys
import time
import subprocess
import Vbs3GetPos_pb2

ip_addr = "127.0.0.1"
if len(sys.argv) > 1:
    ip_addr =  sys.argv[1]
port = "5551"
if len(sys.argv) > 2:
    port =  sys.argv[2]
    int(port)

ids = []
context = zmq.Context()

# Define the socket using the "Context"
sock = context.socket(zmq.SUB)
sock.setsockopt(zmq.SUBSCRIBE, "")
print "Trying to connect to %s:%s" % (ip_addr, port)
sock.connect("tcp://%s:%s" % (ip_addr, port))
last_send_timestamp = time.time()

while True:
  raw_position = sock.recv()
  #print "%s" % raw_position
  position = Vbs3GetPos_pb2.Position()
  position.ParseFromString(raw_position)
  lat_str = position.lat
  lon_str = position.lon
  lat_str = lat_str[1:-1]
  lon_str = lon_str[1:-1]
  [lat, lat_dir] = lat_str.split()
  [lon, lon_dir] = lon_str.split()
  #print "lat value = %f; direction = %s" % ( float(lat), lat_dir )
  #print "lon value = %f; direction = %s" % ( float(lon), lon_dir )
  #print "id: %s; x = %s, y = %s, z = %s, dir = %s, lat = %s, lon = %s" % (position.id, position.x, position.y, position.z, position.dir, lat_str, lon_str)
  #print "\n\n"
  if position.id not in ids:
    ids.append(position.id)
  
  node_id = ids.index(position.id)+1

  if time.time() - last_send_timestamp > 1:
    print "time: %s" % time.time()
    print "Calling ./set_location.sh %i %s %s" % ( node_id, lat, lon )
    print "\n\n"
    subprocess.call( ["./set_location.sh", "%i" % node_id , "%s" % lat, "%s" % lon] )
    last_send_timestamp = time.time()
  #time.sleep(1);
