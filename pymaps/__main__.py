#!/usr/bin/python
# coding=utf-8

__author__ = 'Simon Charest'
__copyright__ = 'Copyright 2019, SLCIT inc.'
__credits__ = ['José de Mendoza y Ríos', 'Guido van Rossum']
__email__ = 'simoncharest@gmail.com'
__license__ = 'GPL'
__maintainer__ = 'Simon Charest'
__project__ = 'PyMaps'
__status__ = 'Development'
__version__ = '1.0.0'

import csv
import googlemaps
import simplekml
import urllib.parse
from datetime import datetime
from math import atan2
from math import cos
from math import radians
from math import sin
from math import sqrt
from os import system


def main():
    _ = system('clear')

    # process_address('data/input_address.csv', 'data/output_location')
    # process_location('data/input_location.csv', 'data/output_address')
    # process_location('data/input_location2.csv', 'data/output_address2')
    process_location('data/input_location3.csv', 'data/output_address3')


def process_address(input_csv, output, print_result=False):
    # Get longitudes and latitudes from addresses
    csv_address = read_csv(input_csv)           # Read original data
    location = get_location(csv_address)        # Process data in Google Maps
    write_csv(output + '.csv', location)        # Write results to CSV
    write_point_kml(output + '.kml', location)  # Write results to KML
    if print_result:
        print_array(location)                   # Print results


def process_location(input_csv, output, print_result=False):
    # Get addresses from latitudes and longitudes
    csv_location = read_csv(input_csv)             # Read original data
    address = get_formatted_address(csv_location)  # Process data in Google Maps
    write_csv(output + '.csv', address)            # Write results to CSV
    write_line_kml(output + '.kml', address)       # Write results to KML
    if print_result:
        print_array(address)                       # Print results


def read_csv(file_path):
    with open(file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        array = []
        for row in csv_reader:
            if line_count > 0:
                array += [row]
            line_count += 1
        return array


# TODO: To implement, eventually
def get_position(haystack, needle):
    for position in range(0, len(haystack)):
        if haystack[position] == needle:
            return position
    return False


def get_location(csv_address):
    gmaps = googlemaps.Client(key='AIzaSyCHbO0Iy6UTyfpYo6b_x1xZundGXGeexHM')
    result = []
    result += [['Name', 'Address', 'Latitude', 'Longitude', 'Distance', 'Map Address', 'Map Location']]
    previous_latitude = 0
    previous_longitude = 0
    distance = 0
    count = 0
    for row in csv_address:
        name = row[0]
        address = row[1]
        geocode_result = gmaps.geocode(row[1])
        latitude = geocode_result[0]['geometry']['location']['lat']
        longitude = geocode_result[0]['geometry']['location']['lng']
        if count > 0:
            distance = get_distance([previous_latitude, previous_longitude], [latitude, longitude])
        map_address = 'https://www.google.com/maps/place/%s' % urllib.parse.quote_plus(address)
        map_location = 'https://www.google.com/maps/place/%s,%s' % (latitude, longitude)
        result += [[name, address, latitude, longitude, distance, map_address, map_location]]
        previous_latitude = latitude
        previous_longitude = longitude
        count += 1
    return result


def get_formatted_address(csv_location):
    gmaps = googlemaps.Client(key='AIzaSyCHbO0Iy6UTyfpYo6b_x1xZundGXGeexHM')
    result = []
    result += [['Latitude', 'Longitude', 'Speed', 'Address', 'Distance', 'Calculated Speed', 'Map Location',
                'Map Address']]
    previous_date_time = 0
    previous_latitude = 0
    previous_longitude = 0
    distance = 0
    calculated_speed = 0
    count = 0
    for row in csv_location:
        date_time = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        latitude = float(row[1])
        longitude = float(row[2])
        speed = int(row[3])
        reverse_geocode_result = gmaps.reverse_geocode((latitude, longitude))
        address = reverse_geocode_result[0]['formatted_address']
        map_location = 'https://www.google.com/maps/place/%s,%s' % (latitude, longitude)
        map_address = 'https://www.google.com/maps/place/%s' % urllib.parse.quote_plus(address)
        if count > 0:
            distance = get_distance([previous_latitude, previous_longitude], [latitude, longitude])
            calculated_speed = get_speed(date_time, previous_date_time, distance)
        result += [[date_time, latitude, longitude, speed, address, distance, calculated_speed, map_location,
                    map_address]]
        previous_date_time = date_time
        previous_latitude = latitude
        previous_longitude = longitude
        count += 1
    return result


def get_distance(location1, location2):
    # Haversine formula (https://en.wikipedia.org/wiki/Haversine_formula)
    radius = 6378137  # Earth's radius in meters
    latitude_delta = radians(location1[0] - location2[0])
    longitude_delta = radians(location1[1] - location2[1])
    a = sin(latitude_delta / 2) * sin(latitude_delta / 2) + cos(radians(location1[0])) * cos(radians(location2[0])) * \
        sin(longitude_delta / 2) * sin(longitude_delta / 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = radius * c
    return distance / 1000  # In km


def get_speed(date_time1, date_time2, distance):
    if distance == 0:
        return False
    return distance / abs(date_time1 - date_time2).total_seconds() * 60 * 60  # In km/h


def write_csv(file_path, data):
    with open(file_path, 'w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        for line in data:
            csv_writer.writerow(line)


def write_point_kml(output_kml, data):
    kml = simplekml.Kml()
    count = 0
    for line in data:
        if count > 0:
            kml.newpoint(name=line[0], coords=[(line[3], line[2])])
        count += 1
    kml.save(output_kml)


def write_line_kml(output_kml, data):
    kml = simplekml.Kml()
    linestring = kml.newlinestring(name=output_kml)
    linestring.style.linestyle.color = simplekml.Color.blue
    linestring.style.linestyle.width = 5
    count = 0
    for line in data:
        if count > 0:
            linestring.coords.addcoordinates([(line[2], line[1])])
        count += 1
    kml.save(output_kml)


def print_array(array):
    for row in array:
        print(row)


main()
