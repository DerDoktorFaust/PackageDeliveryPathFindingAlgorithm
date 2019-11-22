'''Main entry point into the program. It has four main functions. 1) load data from CSV files (data
originally created in excel_data_parser.py. The data parser must be run separately, this main program
only reads data from CSV files. 2) Print reports that show the status of all packages at any time
selected by the user. 3) Create class instances and do all calls that run the program. 4) Provide
a command line interface for the user to generate custom reports.'''

from Hashmap import *
from Graph import *
from Truck import *
import re


def load_data():
    '''Function opens CSV files generated by excel_data_parser.py. For packages, it reads
    the data and inserts it all into a hashmap called packages_map. For distances between
    locations it inserts them into an instance of the Graph class.'''
    with open('./resources/packages.txt', 'r') as packages_file:
        packages_file.seek(0)
        for line in packages_file:
            # strip all newlines and split into list delimited by commas
            temp_line = line.strip('\n').split(',')
            key = int(temp_line[0])
            value = temp_line[1:]
            packages_map.insert(key, value)
        packages_file.close()

    with open('./resources/distances.txt', 'r') as distances_file:
        distances_file.seek(0)
        data = distances_file.readlines()

        for i in range(0, len(data)):
            data[i] = data[i].strip('\n').split(',')
            graph.add_map_edge(
                data[i][0], data[i][1], float(
                    data[i][2]))  # use float() for the distance

    distances_file.close()


def print_reports(time='05:00 PM'):
    '''Generates a report that prints the status of all packages based on a user's inputted time.
    If no time is provided by the user, the default is 5:00 PM.'''

    print(f"Package Status Report as of {time}")

    def check_if_in_transit(package_delivery_time):
        '''Checks each package at the report time to decide whether the package is
        at the hub, in transit, or already delivered.'''

        # converts time that user wishes to view from string to integers
        # splits by colon and a space, making [hour, minute, AM/PM]
        report_time = re.split(r'[: ]', time)
        # convert the numbers to integers for calculations
        report_time[0] = int(report_time[0])
        report_time[1] = int(report_time[1])

        # converts delivery time of actual package to do calculations
        delivery_time = re.split(r'[: ]', package_delivery_time)
        delivery_time[0] = int(delivery_time[0])
        delivery_time[1] = int(delivery_time[1])

        # converts start time of truck to do calculations
        start_time = re.split(r'[: ]', '08:00 AM')
        start_time[0] = int(start_time[0])
        start_time[1] = int(start_time[1])

        # following statements compare start and delivery time with the requested report time
        # and returns it's status as of the report time.
        if report_time[0] > start_time[0] and delivery_time[0] > report_time[0]:
            temp_delivery_status = 'In Transit'
            return temp_delivery_status
        elif report_time[0] == delivery_time[0] and report_time[1] < delivery_time[1]:
            temp_delivery_status = 'In Transit'
            return temp_delivery_status
        if report_time[0] < 8 and report_time[2] == 'AM':
            temp_delivery_status = 'At Hub'
            return temp_delivery_status
        else:
            temp_delivery_status = 'Delivered'
            return temp_delivery_status

    def check_if_delivered():
        '''Takes the results of check_if_in_transit to determine if Delivery Time is N/A (i.e.
        not delivered) or it returns the delivery time if the report time is for after the
        delivery occurred.'''

        if temp_delivery_status != 'Delivered':
            return f"N/A"
        if temp_delivery_status == 'Delivered':
            return packages_map.get(i)[8]

    # Actual printing of the report
    for i in range(1, packages_map.number_of_items + 1):
        temp_delivery_status = check_if_in_transit(packages_map.get(i)[8])
        print(f"Package ID: {i} "
              f"Delivery Address: {packages_map.get(i)[0]} {packages_map.get(i)[1]}, {packages_map.get(i)[2]} {packages_map.get(i)[3]} "
              f"Required Delivery Time: {packages_map.get(i)[4]} "
              f"Package Weight: {packages_map.get(i)[5]} "
              f"Special Notes: {packages_map.get(i)[6]} "
              # calls function to determine status
              f"Delivery Status: {check_if_in_transit(packages_map.get(i)[8])} "
              f"Delivery Time: {check_if_delivered()}")  # calls function to decide between N/A or actual delivery time


# Create class instances and set default values if necessary
packages_map = Hashmap(40)
graph = Graph()
load_data()
truck1 = Truck('truck1')
truck2 = Truck('truck2')
truck3 = Truck('truck3')
# truck 3 needs to finish deliveries quickly and return to hub so driver
# can switch trucks
truck3.max_capacity = 8

# Call functions to load trucks
truck3.load_truck(packages_map, graph)
truck1.load_truck(packages_map, graph)
# driver of truck 3 drives truck 2 as soon as he returns to hub
truck2.time = truck3.time
truck2.load_truck(packages_map, graph)

# Calculate the total distance to deliver all packages
total_distance = round(truck1.mileage + truck2.mileage + truck3.mileage, 1)


# Code for command line interface
quit = False  # variable for CLI loop

while quit == False:
    print("\n\nPlease select from the following menu: ")
    print("[1] See Final Delivery Report (05:00 PM")
    print("[2] Input Custom Time Report")
    print("[3] Check Final Distance for Delivery of All Packages")
    print("[4] Quit Program")
    choice = input("Enter choice ===> ")

    if choice == '1':
        print_reports()
        print(f"\nTotal final distance is===> {total_distance}")
    if choice == '2':
        custom_time = input("Enter Custom Time in Format 00:00 AM/PM====> ")
        print_reports(custom_time)
    if choice == '3':
        print(f"\nTotal final distance is===> {total_distance}")
    if choice == '4':
        quit = True
    else:
        continue