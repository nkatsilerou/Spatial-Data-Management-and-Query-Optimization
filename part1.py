#NEFELI-ELENI KATSILEROU 4385
import math
import sys

# Read points data from file
def read_data(datapath):
    with open(datapath, 'r') as file:
        # Read the total number of points from the first line
        first_line = file.readline().strip()
        total_points = int(first_line)
        #Read the points and their coordinates from the subsequent lines
        points = [(i, tuple(float(x) for x in line.strip().split()))
                  for i, line in enumerate(file, start=1)] 
    return total_points, points

# Slice the data points into groups
def slice_points(points, layer_size):
    slices = []
    for i in range(0, len(points), layer_size):
        #Slice the points into layers of a specified size
        end_index = i + layer_size
        if end_index >= len(points):
            end_index = len(points)
        slices.append(points[i:end_index])
    return slices

# Calculate Minimum Bounding Rectangle (MBR)
def calculate_mbr(coordinates): 
    coords_list = []
    if len(coordinates[0]) == 2: #For 2S coordinated calculate MBR
        min_x = min(point[0] for point in coordinates)
        max_x = max(point[0] for point in coordinates)
        min_y = min(point[1] for point in coordinates)
        max_y = max(point[1] for point in coordinates)
    elif len(coordinates[0]) == 4: #For MBR coordinates extract min and max values
        min_x = min(coord[0] for coord in coordinates)
        min_y = min(coord[1] for coord in coordinates)
        max_x = max(coord[2] for coord in coordinates)
        max_y = max(coord[3] for coord in coordinates)

    #Create a list with the MBR coordinates
    coords_list.append(min_x)
    coords_list.append(min_y)
    coords_list.append(max_x)
    coords_list.append(max_y)
    return coords_list
    

# Create leaf nodes
def create_leaf(slices, node_id, n):
    tree_nodes = []
    for slice in slices:
        for k in range(0, len(slice), n):
            #Create leaf nodes with records
            temp_slices = slice[k:k+n]
            records =[]
            for temp_slice in temp_slices:
                records.append((temp_slice[0], temp_slice[1]))
            #Append node details to the tree nodes list
            node = (node_id, records, 0)
            tree_nodes.append(node)
            node_id += 1
    return tree_nodes, node_id

# Create R-Tree
def create_Rtree(slices, node_points, node_id, n):
    tree_nodes, node_id = create_leaf(slices, node_id, n)
    levels = [tree_nodes]

    #Iterate to create tree levels
    while len(levels[-1]) > 1:
        new_level = []
        current_nodes = levels[-1]
        for i in range(0, len(current_nodes), node_points):
            #Create new nodes for the next level
            children = current_nodes[i:i+node_points]
            coords = [calculate_mbr([rec[1] for rec in child[1]]) for child in children]
            new_node = (node_id, [(children[i][0], geo) for (i, geo) in enumerate(coords)], 1)
            new_level.append(new_node)
            node_id += 1
        levels.append(new_level)
    return levels, node_id

# Write tree data to file and print statistics
def write_output(output_file, tree_levels, node_id, n, capacity_size, point_size, id_size, mbr_size):
    with open(output_file, 'w') as file:
        root_id = tree_levels[-1][0][0]
        file.write(f"{root_id}\n")
        total_nodes = node_id
        tree_height = len(tree_levels)
        print(f"\nR-Tree Height: {tree_height}")

        i = 0
        for level in tree_levels:
            node_count = len(level)
            total_area = 0
            for node in level:
                if node[2] == 1:
                    #Calculate total area for non-leaf nodes
                    for rec in node[1]:
                        geo = rec[1]
                        total_area += (geo[2] - geo[0]) * (geo[3] - geo[1])
                
                records_str = ' , '.join([f"({rec[0]},{rec[1]})" for rec in node[1]])
                line = f"{node[0]} , {len(node[1])} , {node[2]} , {records_str}"
                file.write(f"{line}\n")

            if i != 0:
                level_mbr_area = total_area / node_count
                print(f"---- Level {i+1} statistics ---- \nTotal Nodes: {node_count} \nAverage MBR Area: {level_mbr_area}\n")
            else:
                level_mbr_area = 0
                print(f"---- Level {i+1} statistics ---- \nTotal Nodes: {node_count} \nAverage MBR Area: {level_mbr_area}\n")
            i +=1


datapath = "Beijing_restaurants.txt"
total_points, points = read_data(datapath)

#sort the points based on x-coordinate
points = sorted(points, key=lambda point: point[1][0])

capacity_size = 1024  
id_size = 4 
mbr_size = 32 
point_size = 16  
 
 
node_points = math.floor(capacity_size/(mbr_size + id_size))
n = math.floor(capacity_size/(point_size + id_size))
number_of_slides = math.ceil(math.sqrt(math.ceil(total_points/n)))
layer_size = number_of_slides * n

slices = slice_points(points, layer_size)

#sort the points based on y-coordinate
for slice in slices:
    slice.sort(key=lambda point: point[1][1])

tree_levels, node_id = create_Rtree(slices, node_points, 0, n)

output_tree_file = sys.argv[1]
write_output(output_tree_file, tree_levels, node_id, n, capacity_size, point_size, id_size, mbr_size)

