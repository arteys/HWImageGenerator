import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
from shapely.plotting import plot_polygon, plot_points
import scipy
from scipy.spatial import Voronoi, voronoi_plot_2d
import numpy as np
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
side = 15

cn, rn = side, side # number of columns/rows
xs = np.linspace(-cn/2, cn/2, cn)
ys = np.linspace(-rn/2, rn/2, rn)

# meshgrid will give regular array-like located points
Xs, Ys = np.meshgrid(xs, ys)  #shape: rn x cn

# create some uncertainties to add as random effects to the meshgrid
variation = 0.1
mean = (0, 0)
varx, vary = variation, variation  # adjust these number to suit your need 
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



list_of_area = []
list_of_polygons = []

list_of_nucleus_r = np.empty([])

list_polygons_xs = []
list_polygons_ys = []

list_centres_xs = np.empty([])
list_centres_ys = np.empty([])



for region in vor.regions:
    
    if (any(i<0 for i in region) == False) and (len(region) > 0):
        polygon_vertices = np.empty([0,2])
        
        for c in region:
            polygon_vertices = np.vstack([polygon_vertices, vor.vertices[c]])

        #Removing too big polygons, that were created by Voronoi
        if np.max(abs(polygon_vertices)) < 1.2*abs(max(x_points)):
        
            #Creating shapely object
            poly = Polygon(polygon_vertices)
            #Erosion and dilatation of the polygon for conversion to cell-like shape
            eroded = poly.buffer(-0.2)
            dilated = eroded.buffer(0.1)

            xs, ys = dilated.exterior.xy
            list_polygons_xs.append(xs)
            list_polygons_ys.append(ys)
        
            #Measuring area
            area_c = dilated.area
            list_of_area.append(area_c)

            #Finding centroid
            polygon_center = dilated.centroid
            distance_from_center_to_exterior = dilated.exterior.distance(polygon_center)
            nucleus_r = distance_from_center_to_exterior*50

            xs_center,ys_center = polygon_center.xy
             
            # list_centres_xs.append(xs_center)
            # list_centres_ys.append(ys_center)
            list_centres_xs = np.append(list_centres_xs,xs_center)
            list_centres_ys = np.append(list_centres_ys,ys_center)

            list_of_nucleus_r = np.append(list_of_nucleus_r,nucleus_r)

            

p = figure(width=1024, height=1024)

p.background_fill_color = "black"
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
p.patches(list_polygons_xs, list_polygons_ys, color="green")
p.circle(list_centres_xs, list_centres_ys, color="blue", size=list_of_nucleus_r)

show(p)


