"""
Author: Liam Murray, murrayla@student.unimelb.edu.au
Descrption: this sript produces numpy arrays of essential node and element data 
            retuired for openCMISS iron from gMSH.
Input: gMSH file in .msh format
Output: n_n: number of nodes
        n_el: number of elements
        n_id: list of node indexes
        n_xyz: node coordinates (x, y, z) that correspond to the node indices
        ele_map: numpy array of nodes mapped to each element
        ele_idx: list of element indexes associated with each mapping
    
    *** DISCLAIMER ***
    This code maps nodes to elements in the SAME ORDER THAT GMSH PRODUCES.
    This ordering may NOT be appropriate for every use. For example, tetrahedron
        mapping needs to be reordered from GMSH to Iron usage. This is easily done,
        but please refer here: https://gmsh.info/doc/texinfo/gmsh.html#Node-ordering 
        to note your specific element needs.
"""

import numpy as np

dim = 3

# From https://gmsh.info/doc/texinfo/gmsh.html#MSH-file-format
types = {
    2: "3-node-triangle", 3: "4-node-quadrangle", 4: "4-node-tetrahedron",
    5: "8-node-hexahedron",  9: "6-node-second-order-triangle",
    10: "9-node-second-order-quadrangle",  11: "10-node-second-order-tetrahedron",
    12: "27-node-second-order-hexahedron"
}

def nodes_and_elements(file_path, file_name, type_num):
    
    # Setup
    msh_file = open(file_name, 'r')
    br_container = dict()
    n_list = list()
    e_list = list()
    n_check = 0
    e_check = 0

    # Iterate
    for i, line in enumerate(msh_file):
        # Store break information
        if line[0][0] == '$':
            br_container[line[1:-1]] = i
        # Store information
        if n_check:
            n_list.append(line[:-1])
        if e_check:
            e_list.append(line[:-1])
        # Checks on if we are in the right section
        if line[1:-1] == 'Nodes':
            n_check = 1
            continue
        elif line[1:-1] == 'EndNodes':
            n_check = 0
            continue
        elif line[1:-1] == 'Elements':
            e_check = 1 
            continue
        elif line[1:-1] == 'EndElements':
            e_check = 0
            continue

    # Remove the last value of each list to compensate for the title added
    n_list.pop()
    e_list.pop()

    # $$$$ Nodes $$$$ #

    # Create a file to write to: gmsh2iron.node
    save_name = file_path + file_name.split('gmsh_')[1].split('.msh')[0]
    n_file = open(save_name + '_cvtMSH.nodes', 'w')
    n_file.write(n_list[0] + "\n")

    # Loop through nodes and blocks
    n_pos = dict()
    count = 1
    for i, block in enumerate(n_list):
        if count:
            count -= 1
            continue
        for j in range(int(block.split(" ")[3])):
            n_pos[int(n_list[i+j+1])] = (
                float(n_list[int(block.split(" ")[3])+i+j+1].split(" ")[0]), 
                float(n_list[int(block.split(" ")[3])+i+j+1].split(" ")[1]), 
                float(n_list[int(block.split(" ")[3])+i+j+1].split(" ")[2])
            )
            n_file.write(n_list[i+j+1]+"\t")
            n_file.write(
                n_list[int(block.split(" ")[3])+i+j+1].split(" ")[0] + "\t" +
                n_list[int(block.split(" ")[3])+i+j+1].split(" ")[1] + "\t" +
                n_list[int(block.split(" ")[3])+i+j+1].split(" ")[2] + "\n"
            )
            count +=2

    # $$$$ Elements $$$$ #

    # Create a file to store the element information: gmsh2iron.ele
    e_file = open(save_name + '_cvtMSH.ele', 'w')
    e_file.write(e_list[0] + "\n")

    # Set Element Types
    types = {type_num: types[type_num].strip()}

    # Loop through nodes and blocks
    count = 1
    for i, block in enumerate(e_list):
        if count:
            count -= 1
            continue
        for j in range(int(block.split(" ")[3])):
            count +=1
            if int(block.split(" ")[2]) in types.keys():
                e_file.write(types[int(block.split(" ")[2])] + "\t")
                e_file.write(block.split(" ")[1] + "\t")
                for value in e_list[i+j+1].split():
                    e_file.write(value + "\t")
                e_file.write("\n")
            else:
                continue

def cvt2Numpy(file_path, test_name, elem_type):
    # Inputing Files
    e_file = open(file_path + test_name + '_cvtMSH.ele', 'r')
    n_file = open(file_path + test_name + '_cvtMSH.nodes', 'r')

    e_file_list = e_file.readlines()
    n_file_list = n_file.readlines()
    e_nodes = []

    for i, line in enumerate(e_file_list):
        e_file_list[i] = line.strip()
        if e_file_list[i].split()[0] == elem_type:
            e_nodes.extend(e_file_list[i].split()[3:])
            if i == 1:
                n_el_n = len(e_nodes)

    e_nodes = set(e_nodes)

    for i, line in enumerate(n_file_list):
        n_file_list[i] = line.strip()
        if n_file_list[i].split()[0] in e_nodes or i == 0:
            continue
        else:
            n_file_list.pop()

    # As formatted to gmsh documentation
    # numEntityBlocks(size_t) numNodes(size_t) minNodeTag(size_t) maxNodeTag(size_t)
    _, n_n, _, _ = np.array(n_file_list[0].split()).astype(np.int32)
    n_id = np.zeros(n_n)
    n_xyz = np.zeros((n_n, dim))

    # Reading details from node file
    for i in range(n_n):
        hold = n_file_list[i + 1].split()
        n_id[i] = int(hold[0])
        n_xyz[i, :] = np.array(hold[1:]).astype(np.float64)

    # Closing the file
    n_file.close()

    e_type = []
    for i, line in enumerate(e_file_list):
        if line.split()[0] in types.values():
            e_type.append(line.split()[0])

    e_set = set(e_type)
    n_type = list(map(lambda x: e_type.count(x), e_set))
    e_br = dict(zip(e_set, list(n_type)))

    n_el = e_br[elem_type]
    # Creating variable to store the element map
    ele_map = np.zeros((n_el, n_el_n))
    # Element indexes
    ele_idx = np.zeros(n_el)
    for idx, line in enumerate(e_file_list[1:]):
        ele_map[idx, :] = np.array(line.split()[3:]).astype(np.int32)
        ele_idx[idx] = int(idx + 1)

    # Closing the file
    e_file.close()

    return n_n, n_el, n_id, n_xyz, ele_map, ele_idx

def main():
    test_name = 'oneTetTest'
    file_path = "/Users/murrayla/Documents/main_PhD/Project_Dino/"
    type_num = 11
    # Usage example
    nodes_and_elements(file_path, "gmsh_" + test_name + ".msh", type_num)
    n_n, n_el, n_id, n_xyz, ele_map, ele_idx = cvt2Numpy(file_path, test_name, types[11])
    print(n_n, n_el, n_id, n_xyz, ele_map, ele_idx)

if __name__ == '__main__':
    main()
