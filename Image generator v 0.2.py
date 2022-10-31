import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
from shapely.plotting import plot_polygon, plot_points
import scipy
from scipy.spatial import Voronoi, voronoi_plot_2d
import numpy as np
import geopandas as gpd


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
cn, rn = 40, 40  # number of columns/rows
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
fig, ax = plt.subplots()

for region in vor.regions:
    
    if (any(i<0 for i in region) == False) and (len(region) > 0):
        polygon_vertices = np.empty([0,2])
        
        for y in region:
            polygon_vertices = np.vstack([polygon_vertices, vor.vertices[y]])
        
        polygon = Polygon(polygon_vertices)
        #Erosion and dilatation of the polygon for conversion in to cell-like shape
        eroded = polygon.buffer(-0.2)
        dilated = eroded.buffer(0.1)
        #Finding the cell center
        Polygon_center = dilated.centroid
        distance_from_center_to_exterior = dilated.exterior.distance(Polygon_center)
        nucleus_r = distance_from_center_to_exterior*0.8

        crutch = 12 #catching out of range polygon's point 

        x_polygon,y_polygon = dilated.exterior.xy
        if (any(abs(i)>crutch for i in x_polygon)==False and any(abs(i)>crutch for i in y_polygon)==False):
            area = dilated.area

            center_x, center_y = polygon.centroid.xy
            #plot cell
            plt.fill(x_polygon,y_polygon, color = "green", alpha=1*np.random.uniform(0.7,1))

            # # plot nucleus
            nucleus = plt.Circle((center_x, center_y), nucleus_r, facecolor='blue', alpha=np.random.uniform(0.8,1))
            plt.gca().add_patch(nucleus)

            # points = Random_Points_in_Polygon(polygon, np.random.randint(0,10))
            # xs = [point.x for point in points]
            # ys = [point.y for point in points]
            # #plot lysosomes
            # plt.scatter(xs, ys,color="red", s = np.random.uniform(5,20))


ax.set_aspect("equal")
ax.patch.set_facecolor('black')
ax.patch.set_alpha(1.0)
fig.set_facecolor("black")

plt.show()