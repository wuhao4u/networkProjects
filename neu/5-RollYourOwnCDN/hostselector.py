import sys
import json
from urllib2 import urlopen
from math import *

'''
ec2-54-167-4-20.compute-1.amazonaws.com Origin server (running Web server on port 8080)
ec2-54-210-1-206.compute-1.amazonaws.com                N. Virginia
ec2-54-67-25-76.us-west-1.compute.amazonaws.com         N. California
ec2-35-161-203-105.us-west-2.compute.amazonaws.com      Oregon
ec2-52-213-13-179.eu-west-1.compute.amazonaws.com       Ireland
ec2-52-196-161-198.ap-northeast-1.compute.amazonaws.com Tokyo
ec2-54-255-148-115.ap-southeast-1.compute.amazonaws.com Singapore
ec2-13-54-30-86.ap-southeast-2.compute.amazonaws.com    Sydney
ec2-52-67-177-90.sa-east-1.compute.amazonaws.com        Sao Paolo
ec2-35-156-54-135.eu-central-1.compute.amazonaws.com    Frankfurt
'''

HOST_INFO = {'54.210.1.206': (39.0481, -77.4729), # N.Virginia
            '54.67.25.76': (37.3388, -121.8914), # N. California
            '35.161.203.105': (45.8696, -119.688), # Oregon
            '52.213.13.179': (53.3389, -6.2595), # Ireland
            '52.196.161.198': (35.6427, 139.7677), # Tokyo
            '54.255.148.115': (1.2855, 103.8565), # Singapore
            '13.54.30.86': (-33.8612, 151.1982), # Sydney
            '52.67.177.90': (-23.5464, -46.6289), # Sao Paolo
            '35.156.54.135': (50.1167, 8.6833)} # Frankfurt

EARTH_RADIUS = 6371

# get_host_by_location : String -> String
# given the client IP address, return the server with closest location
def get_host_by_location(ip):
    rawJson = urlopen("http://freegeoip.net/json/" + ip)
    data = json.load(rawJson)
    clientLatlon = (data['latitude'], data['longitude'])

    print("ip: {}, lat:{}, lon:{}".format(ip, data['latitude'], data['longitude']))

    curMinDis = float("inf")
    res = ''

    for key, value in HOST_INFO.iteritems():
        dis = float(get_distance(clientLatlon, value))
        if dis < curMinDis:
            curMinDis = dis
            res = key

    return res

# get_distances : (double, double) (double,double) -> double
# Using Haversine formula to calculate distance between 2 latlon points
def get_distance(latlon1, latlon2):
    radLatlon1 = (radians(latlon1[0]), radians(latlon1[1]))
    radLatlon2 = (radians(latlon2[0]), radians(latlon2[1]))
    
    latDiff = radLatlon2[0] - radLatlon1[0]
    lonDiff = radLatlon2[1] - radLatlon1[1]
    x = pow(sin(latDiff / 2), 2)
    y = cos(radLatlon1[0]) * cos(radLatlon2[0]) * pow(sin(lonDiff/2), 2)
    z = sqrt(x + y)
    res = 2 * EARTH_RADIUS * asin(z)
    return res

if __name__ == '__main__':
    print sys.argv
    addr = '45.78.13.15'
    if len(sys.argv) > 1:
        addr = sys.argv[1]
    print("Selected Host IP: {}".format(get_host_by_location(addr)))
