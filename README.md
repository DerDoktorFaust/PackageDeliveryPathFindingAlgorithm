# PackageDeliveryPathFindingAlgorithm

Python project that finds an optimized route to deliver packages. 

Project accepts Excel files and parses them for relevant data related to items and delivery locations. Package data 
is stored in a hashmap that I designed and implemented (i.e., constructed with lists rather than using built-in
Python dictionaries). Hashmap begins with enough buckets to grow, but will automatically resize when it gets full.
It resizes to double the hashmap size. Resizing is a notoriously slow process for hashmaps, thus this hashmap 
doubles in size, trading memory space for increased speed.

The path-finding algorithm is based on nearest-neighbor to solve a traveling salesman type problem. It finds an 
optimized solution that comes within 20-25% of a fully optimized solution (though, the problem itself is NP-hard
and an optimal solution would be difficult to verify). Areas of future improvement lie in optimizing
the return to origin or even the entire last half of the journey. With nearest neighbor, short paths are found
when there are many locations left to visit. Thus, the first half (in this program) is short, but gets larger
as it runs.

One possible improvement is implementing Dijkstra's algorithm (or something similar) for the last portion of the
path. The delivery routes are a subset of the entire graph, so for the first portion, nearest neighbor performs
similarly to Dijkstra, but the difference grows as the program continues to run. Implementing Dijkstra
would bring the solution to a nearly fully optimized state.

Other areas of improvement would be an improved note parser. Some packages contain special notes (i.e. must be delivered by 10:30
AM). The note parser could be more fully fleshed out to pick up through natural language processing.

Nevertheless, the main point of the project was to build an abstract data type and implement a path-finding
algorithm, and this program provides optimized solutions for both.
