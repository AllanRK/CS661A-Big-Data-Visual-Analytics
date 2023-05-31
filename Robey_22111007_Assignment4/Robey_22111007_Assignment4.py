#!/usr/bin/env python
# coding: utf-8

# In[1]:


# import the necessary libraries
import vtk
import random
import numpy as np
import time
from scipy.interpolate import griddata
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk

# Load the 3D scalar field volume dataset
reader = vtk.vtkXMLImageDataReader()
reader.SetFileName("Isabel_3d.vti")
reader.Update()

# Get the volume data and dimensions
volume = reader.GetOutput()
dims = volume.GetDimensions()

# Compute the total number of points in the volume
def get_num_points(dims):
    num_points = dims[0] * dims[1] * dims[2]
    return num_points
total_points =get_num_points(dims)

def simple_random_sampling(sampling_percentage):
    # Computing the number of points to sample based on the sampling percentage
    sampled_points_count = int(total_points * sampling_percentage/100)

    # Creating a set named sampled_points to store the sampled points
    sampled_points = set()
    # Select the eight corner points
    for i in range(2):
        for j in range(2):
            for k in range(2):
                x = i * (dims[0] - 1)
                y = j * (dims[1] - 1)
                z = k * (dims[2] - 1)
                point = (x, y, z)
                sampled_points.add(point)
 
    # Randomly selecting the remaining points
    sampled_indices = np.random.choice(total_points, sampled_points_count, replace=False)
    for index in sampled_indices:
        z = index % dims[2]
        y = ((index - z) // dims[2]) % dims[1]
        x = (((index - z) // dims[2]) - y) // dims[1]
        point = (x, y, z)
        sampled_points.add(point)

        
    # vtkPoints object created to store the sampled point locations
    points = vtk.vtkPoints()

    # vtkDoubleArray object created to store the data values for each selected point
    data = vtk.vtkDoubleArray()
    data.SetName("Data")

    # loop through the sampled points 
    #add them to the vtkPoints and vtkDoubleArray objects
    for point in sampled_points:
        i, j, k = point
        value = volume.GetScalarComponentAsDouble(i, j, k, 0)
        points.InsertNextPoint(i, j, k)
        data.InsertNextTuple1(value)

    # vtkPolyData object created 
    # add the sampled points and data arrays to it
    poly_data = vtk.vtkPolyData()
    poly_data.SetPoints(points)
    poly_data.GetPointData().AddArray(data)
    

    # Write the vtkPolyData object to a VTKPolyData (*.vtp) file
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetInputData(poly_data)
    writer.SetFileName("sampled_points.vtp")
    writer.Write()

sampling_percentage = float(input("Enter the sampling percentage: "))
simple_random_sampling(sampling_percentage)

# Load the Sampled Data

reader1 = vtk.vtkXMLPolyDataReader()
reader1.SetFileName('sampled_points.vtp')
reader1.Update()

poly_data = reader1.GetOutput()

# obtain the number of sample points in the polydata
num_sam_points = poly_data.GetNumberOfPoints()

# the point coordinates and data will be stored in points_arr and data_arr 
points_arr = np.zeros((num_sam_points, 3))
data_arr = np.zeros(num_sam_points)

# Iterate over the points in the polydata 
# and store them in the numpy arrays point_arr and data_arr
for i in range(num_sam_points):
    point = poly_data.GetPoint(i)
    points_arr[i] = point
    data_arr[i] = poly_data.GetPointData().GetArray("Data").GetValue(i)


# Create a grid of points 
# with the same dimensions as the original volume

dims = (250, 250, 50)
x = np.linspace(0, 249, 250)
y = np.linspace(0, 249, 250)
z = np.linspace(0, 49, 50)
xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
grid = np.column_stack((xx.ravel(), yy.ravel(), zz.ravel()))


choice=(input("Enter the reconstruction method: {nearest/linear} ")).lower()
print("Choosen Method for Reconstruction: ",choice )

# Perform nearest neighbor interpolation
if choice == 'nearest':
    start_time1 = time.time()
    grid_data = griddata(points_arr, data_arr, grid, method='nearest')
    end_time1 = time.time()
    time1 = end_time1-start_time1
    print("Time taken for reconstruction using nearest interpolation method:", time1," secs.")
    output_nearest = vtk.vtkImageData()
    output_nearest.SetDimensions(dims)
    output_nearest.SetOrigin(0, 0, 0)
    output_nearest.SetSpacing(1, 1, 1)
    output_nearest.AllocateScalars(vtk.VTK_FLOAT, 1)

    grid_data = np.reshape(grid_data, dims)
    # Set the reconstructed data as the image data scalars
    for k in range(dims[2]):
        for j in range(dims[1]):
            for i in range(dims[0]):
                idx = output_nearest.ComputePointId([i, j, k])
                output_nearest.GetPointData().GetScalars().SetTuple1(idx, grid_data[i, j, k])

    # Save the reconstructed volume data as a .vti file
    file_name = "reconstructed_nearest.vti"
    writer = vtk.vtkXMLImageDataWriter()
    writer.SetFileName(file_name)
    writer.SetInputData(output_nearest)
    writer.Write()

# perform linear interpolation based reconstruction
elif choice == 'linear':
    start_time2 = time.time()

    grid_data = griddata(points_arr, data_arr, grid, method='linear')
    # Replace nan values with nearest neighbor values
    mask = np.isnan(grid_data)
    grid_data[mask] = griddata(points_arr, data_arr, grid[mask], method='nearest')
    end_time2 = time.time()
    time2 = end_time2 - start_time2
    print("Time taken for reconstruction using linear interpolation method:", time2," secs.")
    
    output_linear = vtk.vtkImageData()
    output_linear.SetDimensions(dims)
    output_linear.SetOrigin(0, 0, 0)
    output_linear.SetSpacing(1, 1, 1)
    output_linear.AllocateScalars(vtk.VTK_FLOAT, 1)



    grid_data = np.reshape(grid_data, dims)
    # Set the reconstructed data as the image data scalars
    for k in range(dims[2]):
        for j in range(dims[1]):
            for i in range(dims[0]):
                idx = output_linear.ComputePointId([i, j, k])
                output_linear.GetPointData().GetScalars().SetTuple1(idx, grid_data[i, j, k])

    # Save the reconstructed volume data as a .vti file
    file_name = "reconstructed_linear.vti"
    writer = vtk.vtkXMLImageDataWriter()
    writer.SetFileName(file_name)
    writer.SetInputData(output_linear)
    writer.Write()
else:
    print("PLEASE ENTER PROPER RECONSTRUCTION CHOICE!!")

# method to convert vti file to numy array
def vti_to_numpy(file_name):
    # Load the dataset
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(file_name)
    reader.Update()
    data = reader.GetOutput()
    # Get the point data from the image data object
    point_data = data.GetPointData()

    # Convert the point data to a NumPy array
    numpy_array = vtk.util.numpy_support.vtk_to_numpy(point_data.GetArray(0))
    return numpy_array

#convert reconstructed file and original file to numpy array
reconstructed_array = vti_to_numpy(file_name)
original_array = vti_to_numpy('Isabel_3D.vti')

# method to Compute the SNR
def compute_SNR(arrgt, arr_recon):
    diff = arrgt - arr_recon 
    sqd_max_diff = (np.max(arrgt) - np.min(arrgt)) ** 2 
    snr = 10 * np.log10(sqd_max_diff / np.mean(diff ** 2))
    return snr

# compute and display the corresponding SNR
snr = compute_SNR(original_array,reconstructed_array)
print('Sampling Percentage ',sampling_percentage,' %')
if choice == 'nearest':
    print('Signal-to-Noise (SNR) ratio for reconstructed data using nearest method: ',snr)
elif choice == 'linear':
    print('Signal-to-Noise (SNR) ratio for reconstructed data using linear method: ',snr)


# In[ ]:




