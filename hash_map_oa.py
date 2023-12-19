# Name: Leela Townsley
# OSU Email: townslel@oregonstate.edu
# Course: CS261 - Data Structures
# Assignment: 6
# Due Date: 12/2/2022
# Description: Implementation of a HashMap  using  Open Addressing with Quadratic Probing.

from a6_include import (DynamicArray, DynamicArrayException, HashEntry,
                        hash_function_1, hash_function_2)


class HashMap:
    def __init__(self, capacity: int, function) -> None:
        """
        Initialize new HashMap that uses
        quadratic probing for collision resolution
        """
        self._buckets = DynamicArray()

        # capacity must be a prime number
        self._capacity = self._next_prime(capacity)
        for _ in range(self._capacity):
            self._buckets.append(None)

        self._hash_function = function
        self._size = 0

    def __str__(self) -> str:
        """
        Override string method to provide more readable output
        """
        out = ''
        for i in range(self._buckets.length()):
            out += str(i) + ': ' + str(self._buckets[i]) + '\n'
        return out

    def _next_prime(self, capacity: int) -> int:
        """
        Increment from given number to find the closest prime number
        """
        if capacity % 2 == 0:
            capacity += 1

        while not self._is_prime(capacity):
            capacity += 2

        return capacity

    @staticmethod
    def _is_prime(capacity: int) -> bool:
        """
        Determine if given integer is a prime number and return boolean
        """
        if capacity == 2 or capacity == 3:
            return True

        if capacity == 1 or capacity % 2 == 0:
            return False

        factor = 3
        while factor ** 2 <= capacity:
            if capacity % factor == 0:
                return False
            factor += 2

        return True

    def get_size(self) -> int:
        """
        Return size of map
        """
        return self._size

    def get_capacity(self) -> int:
        """
        Return capacity of map
        """
        return self._capacity

    def put(self, key: str, value: object) -> None:
        """
        Updates the key/value pair in the hash map.
        If the given key already exists in the hash map,
        its associated value must be replaced with the new value.
        If the given key is not in the hash map, a new key/value pair must be added.
        """
        # resize to double its current capacity when current load factor
        # of the table is greater than or equal to 0.5.
        if self.table_load() >= 0.5:
            self.resize_table(self._capacity * 2)

        # compute an initial index i-initial
        hash = self._hash_function(key)
        index_initial = hash % self._capacity

        # If the given key already exists in the hash map, its associated value must be replaced with the new value.
        if self.contains_key(key):
            pair = self._buckets.get_at_index(index_initial)
            if pair.key == key:
                pair.value = value
            else:
                for j in range(1, self._capacity):
                    index = (index_initial + j ** 2) % self._capacity
                    pair = self._buckets.get_at_index(index)
                    if pair and pair.key == key:
                        pair.value = value
                        return
            return


        # create the new entry to enter
        new_entry = HashEntry(key, value)

        # If array at index initial is empty, insert the element there and stop.
        if self._buckets[index_initial] is None:
            self._buckets.set_at_index(index_initial, new_entry)
            self._size += 1
            return

        # compute the next index i in the probing sequence until find empty bucket and add
        index = self.probing_seq(index_initial)
        self._buckets.set_at_index(index, new_entry)
        self._size += 1

    def probing_seq(self, initial) -> int:
        """
        Returns the next empty index.
        """
        # have it start at 0 to catch tombstones
        for j in range(0, self._capacity):
            index = (initial + j ** 2) % self._capacity
            pair = self._buckets.get_at_index(index)
            if pair is None:
                return index
            if pair.is_tombstone is True:
                return index


    def table_load(self) -> float:
        """
        Returns the current hash table load factor.
        """
        return float(self._size / self._capacity)

    def empty_buckets(self) -> int:
        """
        Returns the number of empty buckets in the hash table.
        """
        counter = 0  # counts empty buckets

        for i in range(self._buckets.length()):
            if self._buckets.get_at_index(i) is None:
                counter += 1

        return counter

    def resize_table(self, new_capacity: int) -> None:
        """
        Changes the capacity of the internal hash table.
        All existing key/value pairs must remain in the new hash map,
        and all hash table links must be rehashed.

        """
        if new_capacity < self._size:
            return

        if not self._is_prime(new_capacity):
            new_capacity = self._next_prime(new_capacity)

        # hold the old values
        holder = self._buckets

        # reset the array
        self._buckets = DynamicArray()
        self._capacity = new_capacity
        self._size = 0
        for _ in range(self._capacity):
            self._buckets.append(None)

        # iterate through array
        for index in range(holder.length()):
            if holder[index] is not None:
                key = holder[index].key
                value = holder[index].value
                self.put(key, value)

    def get(self, key: str) -> object:
        """
        Returns the value associated with the given key.
        If the key is not in the hash map, the method returns None.

        """
        # compute an initial index i-initial
        hash = self._hash_function(key)
        index_initial = hash % self._capacity

        # check initial index
        pair = self._buckets.get_at_index(index_initial)
        if pair and pair.is_tombstone is False and pair.key == key:
            return pair.value

        # use the probe seq to find next index
        for j in range(1, self._capacity):
            index = (index_initial + j ** 2) % self._capacity
            pair = self._buckets.get_at_index(index)
            if pair and pair.is_tombstone is False and pair.key == key:
                return pair.value

        return None

    def contains_key(self, key: str) -> bool:
        """
        Returns True if the given key is in the hash map.
        Otherwise it returns False.
        An empty hash map does not contain any keys.
        """
        if self._size == 0:
            return False

        # run through array
        for index in range(self._capacity):
            if self._buckets[index] is not None:
                pair = self._buckets.get_at_index(index)
                if pair.is_tombstone is False and pair.key == key:
                    return True

        return False

    def remove(self, key: str) -> None:
        """
        Removes the given key and its associated value from the hash map.
        If the key is not in the hash map, the method does nothing (no exception needs to be raised).
        """
        # if key is not in the hash map
        if not self.contains_key(key):
            return

        # run through array
        for index in range(self._capacity):
            if self._buckets[index] is not None:
                pair = self._buckets.get_at_index(index)
                if pair.key == key:
                    pair.is_tombstone = True
                    self._size -= 1


    def clear(self) -> None:
        """
        Clears the contents of the hash map.
        It does not change the underlying hash table capacity.
        """
        self._buckets = DynamicArray()

        for _ in range(self._capacity):
            self._buckets.append(None)

        self._size = 0

    def get_keys_and_values(self) -> DynamicArray:
        """
        Returns a dynamic array where each index contains a tuple of a key/value pair
        stored in the hash map. The order of the keys in the dynamic array does not matter.

        """
        tuple_arr = DynamicArray()

        # iterate through array
        for index in range(self._buckets.length()):
            if self._buckets[index] is not None:  # if the bucket isn't empty
                pair = self._buckets.get_at_index(index)
                if pair.is_tombstone is False:
                    tuple_arr.append((pair.key, pair.value))

        return tuple_arr

    def __iter__(self):
        """
        Enables the hash map to iterate across itself.
        Implement this method in a similar way to the example in the Exploration: Encapsulation and Iterators.
        """
        self._index = 0

        return self

    def __next__(self):
        """
        Returns the next item in the hash map, based on the current location of the iterator.
        Implement this method in a similar way to the example in the Exploration: Encapsulation and Iterators.
        It will need to only iterate over active items.
        """
        try:
            while self._buckets[self._index] is None:
                self._index += 1
            value = self._buckets.get_at_index(self._index)
        except DynamicArrayException:
            raise StopIteration

        self._index = self._index + 1
        return value


# ------------------- BASIC TESTING ---------------------------------------- #

if __name__ == "__main__":

    print("\nPDF - put example 1")
    print("-------------------")
    m = HashMap(53, hash_function_1)
    for i in range(150):
        m.put('str' + str(i), i * 100)
        if i % 25 == 24:
            print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - put example 2")
    print("-------------------")
    m = HashMap(41, hash_function_2)
    for i in range(50):
        m.put('str' + str(i // 3), i * 100)
        if i % 10 == 9:
            print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - table_load example 1")
    print("--------------------------")
    m = HashMap(101, hash_function_1)
    print(round(m.table_load(), 2))
    m.put('key1', 10)
    print(round(m.table_load(), 2))
    m.put('key2', 20)
    print(round(m.table_load(), 2))
    m.put('key1', 30)
    print(round(m.table_load(), 2))

    print("\nPDF - table_load example 2")
    print("--------------------------")
    m = HashMap(53, hash_function_1)
    for i in range(50):
        m.put('key' + str(i), i * 100)
        if i % 10 == 0:
            print(round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - empty_buckets example 1")
    print("-----------------------------")
    m = HashMap(101, hash_function_1)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key1', 10)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key2', 20)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key1', 30)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key4', 40)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())

    print("\nPDF - empty_buckets example 2")
    print("-----------------------------")
    m = HashMap(53, hash_function_1)
    for i in range(150):
        m.put('key' + str(i), i * 100)
        if i % 30 == 0:
            print(m.empty_buckets(), m.get_size(), m.get_capacity())

    print("\nPDF - resize example 1")
    print("----------------------")
    m = HashMap(23, hash_function_1)
    m.put('key1', 10)
    print(m.get_size(), m.get_capacity(), m.get('key1'), m.contains_key('key1'))
    m.resize_table(30)
    print(m.get_size(), m.get_capacity(), m.get('key1'), m.contains_key('key1'))

    print("\nPDF - resize example 2")
    print("----------------------")
    m = HashMap(79, hash_function_2)
    keys = [i for i in range(1, 1000, 13)]
    for key in keys:
        m.put(str(key), key * 42)
    print(m.get_size(), m.get_capacity())

    for capacity in range(111, 1000, 117):
        m.resize_table(capacity)

        if m.table_load() > 0.5:
            print(f"Check that the load factor is acceptable after the call to resize_table().\n"
                  f"Your load factor is {round(m.table_load(), 2)} and should be less than or equal to 0.5")

        m.put('some key', 'some value')
        result = m.contains_key('some key')
        m.remove('some key')

        for key in keys:
            # all inserted keys must be present
            result &= m.contains_key(str(key))
            # NOT inserted keys must be absent
            result &= not m.contains_key(str(key + 1))
        print(capacity, result, m.get_size(), m.get_capacity(), round(m.table_load(), 2))

    print("\nPDF - get example 1")
    print("-------------------")
    m = HashMap(31, hash_function_1)
    print(m.get('key'))
    m.put('key1', 10)
    print(m.get('key1'))

    print("\nPDF - get example 2")
    print("-------------------")
    m = HashMap(151, hash_function_2)
    for i in range(200, 300, 7):
        m.put(str(i), i * 10)
    print(m.get_size(), m.get_capacity())
    for i in range(200, 300, 21):
        print(i, m.get(str(i)), m.get(str(i)) == i * 10)
        print(i + 1, m.get(str(i + 1)), m.get(str(i + 1)) == (i + 1) * 10)

    print("\nPDF - contains_key example 1")
    print("----------------------------")
    m = HashMap(11, hash_function_1)
    print(m.contains_key('key1'))
    m.put('key1', 10)
    m.put('key2', 20)
    m.put('key3', 30)
    print(m.contains_key('key1'))
    print(m.contains_key('key4'))
    print(m.contains_key('key2'))
    print(m.contains_key('key3'))
    m.remove('key3')
    print(m.contains_key('key3'))

    print("\nPDF - contains_key example 2")
    print("----------------------------")
    m = HashMap(79, hash_function_2)
    keys = [i for i in range(1, 1000, 20)]
    for key in keys:
        m.put(str(key), key * 42)
    print(m.get_size(), m.get_capacity())
    result = True
    for key in keys:
        # all inserted keys must be present
        result &= m.contains_key(str(key))
        # NOT inserted keys must be absent
        result &= not m.contains_key(str(key + 1))
    print(result)

    print("\nPDF - remove example 1")
    print("----------------------")
    m = HashMap(53, hash_function_1)
    print(m.get('key1'))
    m.put('key1', 10)
    print(m.get('key1'))
    m.remove('key1')
    print(m.get('key1'))
    m.remove('key4')

    print("\nPDF - clear example 1")
    print("---------------------")
    m = HashMap(101, hash_function_1)
    print(m.get_size(), m.get_capacity())
    m.put('key1', 10)
    m.put('key2', 20)
    m.put('key1', 30)
    print(m.get_size(), m.get_capacity())
    m.clear()
    print(m.get_size(), m.get_capacity())

    print("\nPDF - clear example 2")
    print("---------------------")
    m = HashMap(53, hash_function_1)
    print(m.get_size(), m.get_capacity())
    m.put('key1', 10)
    print(m.get_size(), m.get_capacity())
    m.put('key2', 20)
    print(m.get_size(), m.get_capacity())
    m.resize_table(100)
    print(m.get_size(), m.get_capacity())
    m.clear()
    print(m.get_size(), m.get_capacity())

    print("\nPDF - get_keys_and_values example 1")
    print("------------------------")
    m = HashMap(11, hash_function_2)
    for i in range(1, 6):
        m.put(str(i), str(i * 10))
    print(m.get_keys_and_values())

    m.resize_table(2)
    print(m.get_keys_and_values())

    m.put('20', '200')
    m.remove('1')
    m.resize_table(12)
    print(m.get_keys_and_values())

    print("\nPDF - __iter__(), __next__() example 1")
    print("---------------------")
    m = HashMap(10, hash_function_1)
    for i in range(5):
        m.put(str(i), str(i * 10))
    print(m)
    for item in m:
        print('K:', item.key, 'V:', item.value)

    print("\nPDF - __iter__(), __next__() example 2")
    print("---------------------")
    m = HashMap(10, hash_function_2)
    for i in range(5):
        m.put(str(i), str(i * 24))
    m.remove('0')
    m.remove('4')
    print(m)
    for item in m:
        print('K:', item.key, 'V:', item.value)
