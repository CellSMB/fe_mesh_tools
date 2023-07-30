#Author: Vijay Rajagopal, adopted from Joshua Chung on 28 Jul 2023
#print("Extracts relevant mesh info from .msh --> .vtu")
# -------------------------------------------------------------------------------------------------
# LOAD MODULES

# -------------------------------------------------------------------------------------------------
import os
import numpy as np
import gmsh
import meshio
import argparse

#set up arguments and options here.
argparser = argparse.ArgumentParser("A python program to convert gmsh files into vtu files for paraview.")
argparser.add_argument("fromfile")
argparser.add_argument("tofile")
args = argparser.parse_args()

os.environ['KMP_DUPLICATE_LIB_OK']='True'
# Specify input and output files here:
print("Setting directories...")
InputFile = args.fromfile
OutputFile = args.tofile
VTKType = "hexahedron"

# Set the names of all input files here:
#MeshFileName = "FileName.msh"
#MeshFilePath = InputDir + MeshFileName

# -------------------------------------------------------------------------------------------------
# READ & EXTRACT MESH FILE DATA
# -------------------------------------------------------------------------------------------------
print("Reading & extracting data from Mesh file...")
gmsh.initialize()
gmsh.open(InputFile)
nDim = gmsh.model.getDimension()
NodeTags, NodeCoords, _ = gmsh.model.mesh.getNodes()

# pre-process mesh arrays
NodeCoords = NodeCoords.reshape(-1,nDim)
_, ElemTags, ElemNodeTags = gmsh.model.mesh.getElements(dim=nDim)
nNodesPerElem = np.size(gmsh.model.mesh.getElement(ElemTags[0][0])[1])
ElemTags = ElemTags[0] - ElemTags[0][0]+1
ElemNodeTags = ElemNodeTags[0].reshape(-1,nNodesPerElem)

gmsh.finalize()
print("Mesh file closed...")

# -------------------------------------------------------------------------------------------------
# OUTPUT FOR VTK FILES (.vtu)
# -------------------------------------------------------------------------------------------------
ElemNodeTags = [(VTKType,ElemNodeTags-1)]
meshio.write_points_cells(OutputFile,NodeCoords,ElemNodeTags)
