import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
from shapely.plotting import plot_polygon, plot_points
import scipy
from scipy.spatial import Voronoi, voronoi_plot_2d
import numpy as np
import geopandas as gpd
from PIL import Image, ImageDraw
from PIL import ImagePath 
import shapely.ops as so
import math
from bokeh.plotting import figure, output_file, show
from matplotlib.collections import PolyCollection
from shapely.geometry import MultiPolygon


def Random_Points_in_Polygon(polygon, number):
    points = []
    minx, miny, maxx, maxy = polygon.bounds
    while len(points) < number:
        pnt = Point(np.random.uniform(minx, maxx), np.random.uniform(miny, maxy))
        if polygon.contains(pnt):
            points.append(pnt)
    return points


# create array of meshgrid over a rectangular region
# range of x: -cn/2, cn/2
# range of y: -rn/2, rn/2
cn, rn = 10, 10  # number of columns/rows
xs = np.linspace(-cn/2, cn/2, cn)
ys = np.linspace(-rn/2, rn/2, rn)

# meshgrid will give regular array-like located points
Xs, Ys = np.meshgrid(xs, ys)  #shape: rn x cn

# create some uncertainties to add as random effects to the meshgrid
mean = (0, 0)
varx, vary = 0.1, 0.1  # adjust these number to suit your need 0.007 0.008
cov = [[varx, 0], [0, vary]]
uncerts = np.random.multivariate_normal(mean, cov, (rn, cn))

x_points = Xs+uncerts[:,:,0]
y_points = Ys+uncerts[:,:,1]
x_points = x_points.flatten()
y_points = y_points.flatten()



#Bug when to big grid size
#Maybe some connetion between cell size and quantitiy of lyzosomes
#Make a visible light picture? Only contour and white/gray background

centres = np.column_stack((x_points,y_points))

vor = Voronoi(centres)
# fig = voronoi_plot_2d(vor)
# plt.show()

x_cells= []
y_cells = []
polygons_c = []
coordinates = np.empty([0,2])
n = 0
x_list, y_list = [],[]
x_polygons = np.array([])

fig, axs = plt.subplots()
verts = []
area_list = []
list_of_polygons = []


for region in vor.regions:
    
    if (any(i<0 for i in region) == False) and (len(region) > 0):
        polygon_vertices = np.empty([0,2])
        
        for y in region:
            polygon_vertices = np.vstack([polygon_vertices, vor.vertices[y]])
        
        #Creating shapely object
        poly = Polygon(polygon_vertices)
        #Erosion and dilatation of the polygon for conversion to cell-like shape
        eroded = poly.buffer(-0.2)
        dilated = eroded.buffer(0.1)
        
        #Measuring area
        area_c = dilated.area
        area_list.append(area_c)

        list_of_polygons.append(dilated)
        multi1 = MultiPolygon(list_of_polygons)

        x_polygon,y_polygon = dilated.exterior.xy 


new_shape = so.cascaded_union(multi1)
fig, axs = plt.subplots()
axs.set_aspect('equal', 'datalim')

for geom in new_shape.geoms:    
    xs, ys = geom.exterior.xy    
    axs.fill(xs, ys, alpha=0.5, fc='r', ec='none')

plt.show()