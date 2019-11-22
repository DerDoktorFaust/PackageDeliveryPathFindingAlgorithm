'''Truck class to provide main functionality of loading trucks and picking routes.'''

#from main import *
from Graph import *
from Hashmap import *
import re


class Truck:

    def __init__(self, name):
        '''Initializes an instance of Truck'''
        self.name = name
        self.average_speed = 0.3  # miles per minute, i.e. 18 mph
        self.max_capacity = 16  # max number of packages on a truck
        self.time = '08:00 AM'  # default is the starting time for the day
        self.mileage = 0

    def load_truck(self, packages, graph):
        '''Uses heuristic measurements to load truck. Constantly calls update function to
        remove loaded packages from the tracker in the Hashmap class. This tracker is
        a main basis for the system to decide if a package is available to load.'''
        loaded_packages = []  # list to keep track of the packages loaded during each iteration of the load_truck function
        # counts amount of early delivery packages in order to spread among
        # both trucks
        early_delivery_load = 0

        # Following packages required to be on truck 2, so "reserve" them from
        # being selected for other trucks further down
        if self.name == 'truck2':
            loaded_packages.append(3)
            loaded_packages.append(6)
            loaded_packages.append(18)
            loaded_packages.append(36)
            loaded_packages.append(38)
            # Package originally had wrong address, changed at 10:20 AM
            packages.get(9)[0] = '410 S State St'
            loaded_packages.append(9)

        # Truck 1 is loaded first; so, packages reserved for truck 2 must not
        # go into truck 1
        truck2_reserved_list = [3, 6, 18, 36, 38, 9]
        for package in truck2_reserved_list:  # now remove any packages that were previously loaded onto other trucks
            if package in packages.remaining_packages:
                packages.remaining_packages.remove(package)

        if self.name == 'truck1':  # all of these packages must be delivered with each other, so they are marked for truck 1
            loaded_packages.append(13)
            loaded_packages.append(14)
            loaded_packages.append(15)
            loaded_packages.append(16)
            loaded_packages.append(19)
            loaded_packages.append(20)
        # Like for truck 2, truck 1 needs a "reserved" list
        truck1_reserved_list = [13, 14, 15, 16, 19, 20]
        for package in truck1_reserved_list:  # now remove any packages that were previously loaded onto other trucks
            if package in packages.remaining_packages:
                packages.remaining_packages.remove(package)

        # Section checks for packages with early deliveries and spreads them
        # between trucks
        for i in range(packages.number_of_items):
            if packages.get(i) and (
                    i in packages.remaining_packages):  # check to see if it is an empty bucket
                if packages.get(i)[4] != 'EOD' and 'Delayed' not in packages.get(i)[
                        6]:  # check if it has an early delivery time
                    loaded_packages.append(i)
                    early_delivery_load += 1

        self.update_remaining_packages(loaded_packages, packages)

        if self.name == 'truck3':  # this is first truck and needs to go out first to take care of early packages, but be back early so truck 2 can go out
            # with all of the 9:05 arriving packages
            # Load packages until full (but skip packages that are only for
            # truck 2 for other trucks)
            for i in range(packages.number_of_items + 1):
                if i not in packages.remaining_packages:
                    continue
                if packages.get(i):
                    loaded_packages.append(i)
                if len(loaded_packages) == self.max_capacity:
                    break

            self.update_remaining_packages(loaded_packages, packages)

            package_addresses = self.convert_package_number_to_address(
                packages, loaded_packages)  # convert to string addresses

            # call function to sort distances for all packages loaded
            self.sort_distances(
                '4001 South 700 East',
                loaded_packages,
                package_addresses,
                graph,
                packages)  # starting point is hub location
            return  # this is truck 3, so leave function early -- it can't take many packages with it

        # add packages that have the same address as those already loaded
        for i in range(len(loaded_packages)):
            for x in range(packages.number_of_items):
                if packages.get(x) and packages.get(loaded_packages[i]):
                    if packages.get(loaded_packages[i])[0] == packages.get(x)[0] and (
                            i in packages.remaining_packages):  # can't use .get(i), need actual value from loaded_packages
                        loaded_packages.append(x)

        # check just to make sure there are no duplicates
        loaded_packages = list(set(loaded_packages))

        # another periodic update to tracker
        self.update_remaining_packages(loaded_packages, packages)

        # Load packages that don't have strict requirements until truck
        # capacity is reached.
        for i in range(packages.number_of_items + 1):
            if i not in packages.remaining_packages:
                continue
            if packages.get(i):
                loaded_packages.append(i)
            if len(loaded_packages) == self.max_capacity:
                break

        self.update_remaining_packages(
            loaded_packages, packages)  # another update to tracker

        package_addresses = self.convert_package_number_to_address(
            packages, loaded_packages)  # convert package IDs to street addresses

        # last check to make sure no duplicates; most of the other set calls to remove duplicates were
        # extraneous, but provided an easy error check just in case. This one is actually required
        # because it will remove duplicate physical street addresses after package IDs were converted in
        # the line above.
        loaded_packages = list(set(loaded_packages))

        # Run distance calculator to find route and run it; starting place is
        # hub
        self.sort_distances(
            '4001 South 700 East',
            loaded_packages,
            package_addresses,
            graph,
            packages)

    def convert_package_number_to_address(self, packages, numeric_list):
        '''To compute distances, graph requires street addresses rather than package numbers.
        This function will take the packages loaded onto the truck and convert them to
        a street address.'''
        converted_list = [
        ]  # need a new list or "numeric_list" (actually "loaded_packages") will be overwritten with text
        for i in range(len(numeric_list)):
            converted_list.append(packages.get(numeric_list[i])[0])
        return converted_list

    def update_remaining_packages(self, loaded_packages, packages):
        '''Provides an easy function call to update the hashmap class tracker periodically.
        The tracker is used extensively to see if a package has already been loaded previously.'''
        for package in loaded_packages:  # now remove any packages that were previously loaded onto other trucks
            if package in packages.remaining_packages:
                packages.remaining_packages.remove(package)

    def calculate_and_stamp_time(
            self,
            distance,
            loaded_packages,
            current_location,
            locations,
            packages):
        '''Function calculates the elapsed time from one location to another and adds this to
        the actual time. This actual time is then submitted to the packages hashmap to
        update delivery time. Distance is the incremental distance from the last stop. All data
        comes from sort_distances function as it progresses on the path.'''

        # time passed in minutes
        time_passed = int(distance / self.average_speed)

        # Times throughout program are given as strings. The following converts parts of the strings
        # to generate pieces that can be used to actually calculate data.
        # splits by colon and a space, making [hour, minute, AM/PM]
        list_time = re.split(r'[: ]', self.time)
        # convert the numbers to integers for calculations
        list_time[0] = int(list_time[0])
        list_time[1] = int(list_time[1])

        # If/elif section to add elapsed time to get new clock time
        if list_time[1] + time_passed < 60:
            list_time[1] += time_passed
        # elif (and not simply if) so this doesn't run list_time[1] calculation again
        elif list_time[1] + time_passed > 60:
            list_time[0] += 1
            list_time[1] = int((list_time[1] + time_passed) % 60)
            if list_time[0] >= 12:
                list_time[2] = 'PM'
        if list_time[1] < 10:
            list_time[1] = f"0{list_time[1]}"

        # Updates in string format the truck's time
        self.time = f"{list_time[0]}:{list_time[1]} {list_time[2]}"

        # Next section updates delivery time and status on the actual packages
        # in the hashmap
        for i in range(1, packages.number_of_items + 1):
            if i in loaded_packages and packages.get(i)[0] == current_location:
                packages.get(i)[7] = 'Delivered'
                packages.get(i)[8] = self.time

    def sort_distances(
            self,
            current_location,
            loaded_packages,
            locations,
            graph,
            packages):
        '''Function uses basic Nearest Neighbor algorithm to move along the graph/map.
        Initial location is supplied by calling function and is always the hub.
        It finds the next stop that has a deliverable package that is closest to the current
        location. It then moves along the graph, delivers, and then recursively calls itself
        to get to the next location. Once it delivers all packages, it adds the hub
        onto the list of destinations and goes home. The only truck that returns home
        in the calculations is the very first truck, truck 3. Truck 1 never has another
        load and the driver of truck 3 takes truck 2 when he arrives back at the hub.
        Truck 2's return to the hub is also not calculated. This is based on the fact
        that once the final package is delivered, mileage stops. The same applies to
        truck 1 by extension--the driver can simply hang around at the final stop until
        truck 2 finishes delivering the final package. In any case, even if truck 1 and
        truck 2 are required to come back to the hub before final distance is calculated,
        the final distance would be within optimization parameters (basically adding
        about 15-20 miles total, based on tests).'''

        # Create places to store data
        distances = {}
        unsorted_locations = locations.copy()
        sorted_locations = []

        # Build data table of distances between locations based on packages
        # loaded
        for i in range(len(unsorted_locations)):
            distances[(current_location, unsorted_locations[i])] = graph.get_distance(
                current_location, unsorted_locations[i])

        # selects location based on sorting by smallest distance
        current_location = sorted(
            distances.items(),
            key=lambda x: x[1])[0][0][1]
        # keeps track of mileage on the truck
        self.mileage += float(sorted(distances.items(),
                                     key=lambda x: x[1])[0][1])
        iterated_distance = round(
            float(
                sorted(
                    distances.items(),
                    key=lambda x: x[1])[0][1]),
            1)  # keeps track of the iterated distance for calculations
        self.calculate_and_stamp_time(
            iterated_distance,
            loaded_packages,
            current_location,
            locations,
            packages)  # calculate delivery times and post results
        # keep track of the location that was selected for recursion
        sorted_locations.append(current_location)
        # remove the location from list to continue sorting because it has
        # already been visited
        unsorted_locations = [
            x for x in unsorted_locations if x != current_location]

        # Make sure that truck either returns to hub if it needs to (truck 3)
        # or does not if it doesn't need to (trucks 1 and 2)
        if len(
                unsorted_locations) == 0:  # check to either exit the recursion or return to hub
            if self.name == 'truck1' or self.name == 'truck2':
                return sorted_locations
            # this will exit the loop, it means truck already went to hub
            if(current_location == '4001 South 700 East'):
                return sorted_locations
            # if the above if fails, it means last delivery occurred, now
            # return to hub
            unsorted_locations.append('4001 South 700 East')

        # recursive call
        self.sort_distances(
            current_location,
            loaded_packages,
            unsorted_locations,
            graph,
            packages)

        return sorted_locations
