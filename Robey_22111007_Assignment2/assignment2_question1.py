# Assignment 2
# Question 1
# Name - Allan Robey
# Roll No - 22111007

#import modules...
from vtk import *

# load the data.....
reader = vtkXMLImageDataReader()
reader.SetFileName('Data/Isabel_2D.vti')
reader.Update()
data = reader.GetOutput()

# input the value of isovalue....
def get_input():
    c = float(input("Enter the value of c(isovalue): "))
    return c
c = get_input()

# obtain the number of cells....
def get_num_of_cells(data):
    x = data.GetNumberOfCells() 
    return x   
number_of_cells = get_num_of_cells(data)

# obtain the data array
def get_data_array(data):
    y = data.GetPointData().GetArray('Pressure')
    return y
array_of_data = get_data_array(data)

# create points....
def create_points():
    x = vtkPoints()
    return x
points = create_points()

# Create a cell array to store the lines.....
def create_cell_array():
    z = vtkCellArray()
    return z
cells = create_cell_array()

# method to obtain a cell....
def get_cell(data,i):
    cell = data.GetCell(i)
    return cell

# obtain the point ids in anticlockwise order.....
def get_point_id(cell):
    # accessing vertices in anticlockwise order....
    pid1 = cell.GetPointId(0)
    pid2 = cell.GetPointId(1)    
    pid3 = cell.GetPointId(3)   
    pid4 = cell.GetPointId(2)
    return pid1,pid2,pid3,pid4

# method to obtain the value of the vertices of the cell....
def obtain_cell_val(data_arr,p1,p2,p3,p4):
    val1 = data_arr.GetTuple1(p1)
    val2 = data_arr.GetTuple1(p2)
    val3 = data_arr.GetTuple1(p3)
    val4 = data_arr.GetTuple1(p4)
    return val1,val2,val3,val4

# method to obtain the co-ordinates of the points.....
def get_coordinates(data,pid1,pid2,pid3,pid4):
    c1 = data.GetPoint(pid1)
    c2 = data.GetPoint(pid2)
    c3 = data.GetPoint(pid3)
    c4 = data.GetPoint(pid4)
    return c1,c2,c3,c4

# compute the linear interpolation....
def compute_linear_interpolation(c,v1,v2):
    l = ((v1 - c)/(v1 - v2))
    return l

# compute the intersection point....
def compute_intersection(l,px1,py1,pz1,px2,py2,pz2):
    x = l * (px2-px1)+px1
    y = l * (py2-py1)+py1
    z = l * (pz2-pz1)+pz1
    return x,y,z

# iterating through all cells....
for i in range(number_of_cells):

    cell = get_cell(data,i)
    # accessing vertices in anticlockwise order....

    pid1,pid2,pid3,pid4 = get_point_id(cell)
    
    # store the value of the vertices of the cell...

    value_1,value_2,value_3,value_4 = obtain_cell_val(array_of_data,pid1,pid2,pid3,pid4)
    
    # obtain the co-ordinates of the points.....
    coordinate1, coordinate2, coordinate3, coordinate4 = get_coordinates(data,pid1,pid2,pid3,pid4)
    
    x1,y1,z1 = coordinate1[0],coordinate1[1],coordinate1[2]
    x2,y2,z2 = coordinate2[0],coordinate2[1],coordinate2[2]
    x3,y3,z3 = coordinate3[0],coordinate3[1],coordinate3[2]
    x4,y4,z4 = coordinate4[0],coordinate4[1],coordinate4[2]
    
    # conditions are used to determine if the isosurface crosses an edge of the current cell......

    if((value_1<=c and value_2>=c)or(value_1>=c and value_2<=c)):
        # compute the linear interpolation....
        l1 = compute_linear_interpolation(c,value_1,value_2)
        x,y,z = compute_intersection(l1,x1,y1,z1,x2,y2,z2)
        p = [x,y,z]
        # insert the result into points....
        points.InsertNextPoint(p)
   
    if((value_2<=c and value_3>=c) or (value_2>=c and value_3<=c)):
        # compute the linear interpolation....
        l2 = compute_linear_interpolation(c,value_2,value_3)
        x,y,z = compute_intersection(l2,x2,y2,z2,x3,y3,z3)
        p = [x,y,z]
        # insert the result into points....
        points.InsertNextPoint(p)
       
    if((value_3<=c and value_4>=c) or (value_3>=c and value_4<=c)):
        # compute the linear interpolation....
        l3 = compute_linear_interpolation(c,value_3,value_4)
        x,y,z = compute_intersection(l3,x3,y3,z3,x4,y4,z4)
        p = [x,y,z]
        # insert the result into points....
        points.InsertNextPoint(p)
       
    if((value_4<=c and value_1>=c) or (value_4>=c and value_1<=c)):
        # compute the linear interpolation....
        l4 = compute_linear_interpolation(c,value_4,value_1)
        x,y,z = compute_intersection(l4,x1,y1,z1,x4,y4,z4)
        p = [x,y,z]
        # insert the result into points....
        points.InsertNextPoint(p)

# create the polyLine object....
poly_line = vtkPolyLine()
# obtain the number of points....
def get_num_points(points):
    num = points.GetNumberOfPoints()
    return num
num_of_points = get_num_points(points)

for i in range(0,num_of_points,2):
    # adding line segments.....
    number_of_ids = 2
    poly_line.GetPointIds().SetNumberOfIds(number_of_ids)
    poly_line.GetPointIds().SetId(0,i)
    poly_line.GetPointIds().SetId(1,i+1)
    # insert the polyLine....
    cells.InsertNextCell(poly_line)

# create the polyData object ....
poly_data = vtkPolyData()
# Add points and cells to polydata
poly_data.SetPoints(points)
poly_data.SetLines(cells)

# write the polydata to the disk....
writer = vtkXMLPolyDataWriter()
writer.SetFileName("isocontour.vtp")
writer.SetInputData(poly_data)
writer.Write()

# Load the polydata
reader = vtkXMLPolyDataReader()
reader.SetFileName("isocontour.vtp")
reader.Update()

# Create a mapper
mapper = vtkPolyDataMapper()
mapper.SetInputData(reader.GetOutput())

# Create an actor
actor = vtkActor()
actor.SetMapper(mapper)
colors = vtkNamedColors()
actor.GetProperty().SetColor(colors.GetColor3d('blue'))

# Create a renderer
renderer = vtkRenderer()
renderer.AddActor(actor)
renderer.SetBackground(colors.GetColor3d('Grey'))

# Create a render window
render_window = vtkRenderWindow()
render_window.AddRenderer(renderer)

# Create an interactor
interactor = vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Start the interactor
interactor.Initialize()

interactor.Start()