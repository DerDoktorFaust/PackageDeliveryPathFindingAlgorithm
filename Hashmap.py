'''Hashmap class used to load, store, and use data on packages'''


class Hashmap:
    def __init__(self, initial_size):
        '''Initializes the hashmap, creating 1.4 times the buckets
        needed to store initial loaded data. This provides some growth
        room, but the hashmap also contains a resize function in the
        event that a larger data set is loaded.'''
        self.map_size = int(initial_size * 1.4)
        self.map = [None] * self.map_size
        self.number_of_items = 0
        # create a list to track which packages are left during truck loading
        self.remaining_packages = [i for i in range(1, 41)]

    def compute_hash(self, key):
        '''Computes a hash value for a given key (based on package ID). The formula and size
        of the hashtable should prevent the hash from ever creating collisions. A hash
        value of a string can also be computed with this function. This exists in case
        the hashmap is used in the future for other kinds of data--the package IDs are
        all hashed as integers.'''
        hash_value = 0
        if isinstance(key, int):
            return hash(key) % self.map_size
        if isinstance(key, str):
            for character in key:
                hash_value = hash_value + ord(character)
            return hash_value % self.map_size

    def insert(self, key, value):
        """First checks to see if the hashmap if close to full or every bucket is actually full.
        If so, it calls resize(). It then checks if the bucket is empty. If so, it places the
        key,value into the bucket. If an item is already in the bucket, it appends the new
        key,value as another list in that bucket."""
        bucket = self.compute_hash(key)
        key_value = [key, value]

        if self.number_of_items == self.map_size:
            self.resize()

        if self.map[bucket] is None:
            self.map[bucket] = list([key_value])
            self.number_of_items += 1
            return True
        else:
            for each_pair in self.map[bucket]:
                if each_pair[0] == key:
                    each_pair[1] = value
                    return True
            self.map[bucket].append(key_value)
            self.number_of_items += 1
            return True

    def get(self, key):
        '''Function to be called from outside the class to get values of packages. A package ID
        is supplied to this function and the return value is all package data in the form of a
        list. If the key provided does not exist, None is returned. '''
        bucket = self.compute_hash(key)

        if self.map[bucket] is not None:
            for each_pair in self.map[bucket]:
                if each_pair[0] == key:
                    return each_pair[1]

        return None

    def delete(self, key):
        '''Can be used to delete a key from the hashmap. Returns false is key provided
        does not exist.'''
        bucket = self.compute_hash(key)

        if self.map[bucket] is None:
            return False

        for x in range(len(self.map[bucket])):
            if self.map[bucket][x][0] == key:
                self.map[bucket].remove(x)
                self.number_of_items -= 1  # keep track of number of items in hashmap
                # remove value for truck loading purposes
                self.remaining_packages.remove(x)
                return True

    def resize(self):
        """Will resize the hashmap if it ever fills up. Resizes to double and then maps keys,values."""
        larger_map = Hashmap(self.map_size * 2)

        for key, value in self.map:
            larger_map.insert(key, value)

        self.map = larger_map
