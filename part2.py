#NEFELI-ELENI KATSILEROU 4385
import math
import heapq
import sys
import re

#Load the R-tree
def load_Rtree(filepath):
    nodes = {}  # Dictionary to store nodes
    with open(filepath, 'r') as file:
        root_node_id = file.readline().strip()  #read the Id of the roor from the first line
        root_node_id = int(root_node_id)
        for line in file:
            split_line = line.split(', ', 3)  #Split the line ito its components
            node_id = int(split_line[0])
            total_records = split_line[1]
            node_type = int(split_line[2])
            node_records = split_line[3]
            parsed_records = parse_node_records(node_records)
            nodes[node_id] = (parsed_records, node_type) 
    return nodes, root_node_id

#Parse node records from a string
def parse_node_records(node_records):
    rec_pattern = r'\((\d+),\s*(\[[^\]]+\]|\([^\)]+\))\)'
    parsed_records = []
    matches = re.findall(rec_pattern, node_records) #find all matched of the pattern to match records
    for match in matches:

        record_id = match[0]  #extract record id
        coords_str = match[1]  #extract coordinates as string
        
        # Extracting the coordinates as strings
        coord_strings = re.findall(r'\d+\.\d+', coords_str.strip('[]()'))

        # Converting the coordinate strings to floats
        coord_floats = [float(x) for x in coord_strings]

        # Creating a tuple from the float coordinates
        coords = tuple(coord_floats)

        record_id_int = int(record_id)
        record_tuple = (record_id_int, coords)
        parsed_records.append(record_tuple)

    return parsed_records

#Calculate the min distance between a query point and coordinates
def mindist(q, coordinates):
    result = 0
    if len(coordinates) == 4:
        q_x = q[0]
        q_y = q[1]
        min_x, min_y, max_x, max_y = coordinates
        coord_min_x = min_x - q_x
        coord_max_x = q_x - max_x
        coord_min_y = min_y - q_y
        coord_max_y = q_y - max_y
        d_x = max(coord_min_x, 0, coord_max_x)
        d_y = max(coord_min_y, 0, coord_max_y)
        result = math.sqrt(d_x**2 + d_y**2)
    else:
        q_x = q[0]
        q_y = q[1]
        p_x, p_y = coordinates
        dist_x = q_x - p_x
        dist_y = q_y - p_y
        result = math.sqrt(dist_x**2 + dist_y**2)
    return result 

def incremental_nearest_neighbors(nodes, root_node_id, query_point, k):
    heap = []  #store distances and id
    nearest_neighbors = [] #store nearest neighbors
    heap_empty = True #flag to indicate if heap is empty
    
    root_records, root_type = nodes[root_node_id]
    for rec in root_records:
        #Calculate distance between query point and record coordinates
        euclidean1_dist = mindist(query_point, rec[1])
        tmp1_id = rec[0] 
        tmp1_coord = rec[1] 
        heapq.heappush(heap, (euclidean1_dist, tmp1_id, tmp1_coord, root_type))
        heap_empty = False #set false since heap is not empty

    while not heap_empty and len(nearest_neighbors) < k:
        distance, node_id, geos, leaf = heapq.heappop(heap) #pop distance and id from the heap
        if leaf == 0: #if node is a leaf
            nearest_neighbors.append((node_id, distance, geos)) #add node id,distance and coordinates to nearest neighbors list
        else:
            node_records, node_type = nodes[node_id] #get records and type of non-leaf node
            for rec in node_records:
                euclidean2_dist = mindist(query_point, rec[1])
                tmp2_id = rec[0]
                tmp2_coord = rec[1]
                heapq.heappush(heap, (euclidean2_dist, tmp2_id, tmp2_coord, node_type))

        #Check if heap is empty
        if len(heap) == 0:
            heap_empty = True

        print(f"Current heap: {heap}")  # Print the current heap
    
    return nearest_neighbors


tree_file, query_x, query_y, k = sys.argv[1:5]
query_point = (float(query_x), float(query_y))
k = int(k)

nodes, root_node_id = load_Rtree(tree_file)
nearest_neighbors = incremental_nearest_neighbors(nodes, root_node_id, query_point, k)

nearest_neighbors = incremental_nearest_neighbors(nodes, root_node_id, query_point, k+1)
nearest_neighbors = incremental_nearest_neighbors(nodes, root_node_id, query_point, k+2)
    
print(f"Printing the {k} nearest neighbors:")
for rec_id, distance, coords in nearest_neighbors[:k]:
    print(f"({rec_id},{coords}), Distance: {distance}")

print(f"\nPrinting the {k+1} and {k+2} nearest neighbors:")
for rec_id, distance, coords in nearest_neighbors[k:]:
    print(f"({rec_id},{coords}), Distance: {distance}")
