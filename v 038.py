import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
from shapely.plotting import plot_polygon, plot_points
from scipy.spatial import Voronoi, voronoi_plot_2d
import numpy as np
import shapely.ops as so
from shapely.geometry import MultiPolygon
import matplotlib.collections as mc
import pandas as pd
import geopandas as gpd
import io
from PIL import Image,ImageFilter


def Random_Points_in_Bounds(polygon, number):   
    minx, miny, maxx, maxy = polygon.bounds
    x = np.random.uniform( minx, maxx, number )
    y = np.random.uniform( miny, maxy, number )
    return x, y


# create array of meshgrid over a rectangular region
# range of x: -cn/2, cn/2
# range of y: -rn/2, rn/2
side = 25

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

centres = np.column_stack((x_points,y_points))

vor = Voronoi(centres)
# fig = voronoi_plot_2d(vor)


list_of_area = []
list_of_polygons = []

list_of_circles = []
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
        if np.max(abs(polygon_vertices)) < 1.1*abs(max(x_points)):
        
            #Creating shapely polygon
            poly = Polygon(polygon_vertices)
            #Erosion and dilatation of the polygon for conversion to cell-like shape
            eroded = poly.buffer(-0.2)
            dilated = eroded.buffer(0.1)

            list_of_polygons.append(dilated)

            xs, ys = dilated.exterior.xy
            list_polygons_xs.append(xs)
            list_polygons_ys.append(ys)
        
            #Measuring area
            area_c = dilated.area
            list_of_area.append(area_c)

            #Finding centroid
            polygon_center = poly.centroid

            distance_from_center_to_exterior = dilated.exterior.distance(polygon_center)

            if np.isnan(distance_from_center_to_exterior): #Sometimes distance somehow == nan in this case nucleus insensible small. Someday i will fix it
                distance_from_center_to_exterior = 0.01

            nucleus_r = distance_from_center_to_exterior*np.random.uniform(0.6,0.7)

            circle = polygon_center.buffer(nucleus_r)
            list_of_circles.append(circle)

            xs_center,ys_center = polygon_center.xy
             
            # list_centres_xs.append(xs_center)
            # list_centres_ys.append(ys_center)
            list_centres_xs = np.append(list_centres_xs,xs_center)
            list_centres_ys = np.append(list_centres_ys,ys_center)

            list_of_nucleus_r = np.append(list_of_nucleus_r,nucleus_r)



polygons_cascaded = so.unary_union(list_of_polygons)
# circles_cascaded = so.unary_union(list_of_circles)

#This part create "lysosomes" with random points in random polygons from unioned polygones. From https://www.matecdev.com/posts/random-points-in-polygon.html
gdf_poly = gpd.GeoDataFrame(index=["myPoly"], geometry=[polygons_cascaded])
x,y = Random_Points_in_Bounds(polygons_cascaded, 1000)
df = pd.DataFrame()
df['points'] = list(zip(x,y))
df['points'] = df['points'].apply(Point)
gdf_points = gpd.GeoDataFrame(df, geometry='points')
Sjoin = gpd.tools.sjoin(gdf_points, gdf_poly, predicate="within", how='left')

# Keep points in "myPoly"
pnts_in_poly = gdf_points[Sjoin.index_right=='myPoly']


plt.rcParams["figure.figsize"] = [10, 10]
plt.rcParams["figure.autolayout"] = True

#GREEN
fig, ax = plt.subplots()
ax.set_aspect("equal")
ax.patch.set_facecolor('black')
ax.patch.set_alpha(1.0)

fig.set_facecolor("black")

ax.margins(0)
for p in list_of_polygons:
    x_polygon,y_polygon = p.exterior.xy
    plt.fill(x_polygon,y_polygon, color = "green", alpha=1*np.random.uniform(0.7,1))

x_lim = ax.get_xlim()
y_lim = ax.get_ylim()


plt.draw()
fig.savefig("green.png")

buf_green= io.BytesIO()
plt.savefig(buf_green, format='png')
buf_green.seek(0)

im_green = Image.open(buf_green)

blurImage_green = im_green.filter(ImageFilter.BLUR)
blurImage_green.show()
blurImage_green.save("green.png","PNG")



#BLUE
fig, ax = plt.subplots()
ax.set_aspect("equal")
ax.patch.set_facecolor('black')
ax.patch.set_alpha(1.0)

fig.set_facecolor("black")

ax.margins(0)


for p in list_of_circles:
    x_polygon,y_polygon = p.exterior.xy
    plt.fill(x_polygon,y_polygon, color = "blue", alpha=1*np.random.uniform(0.7,1))

ax.set_xlim(x_lim)
ax.set_ylim(y_lim)

plt.draw()
fig.savefig("blue.png")

buf_blue = io.BytesIO()
plt.savefig(buf_blue, format='png')
buf_blue.seek(0)

im_blue = Image.open(buf_blue)

blurImage_blue = im_blue.filter(ImageFilter.BLUR)
blurImage_blue.show()
blurImage_blue.save("blue.png","PNG")


#RED
fig, ax = plt.subplots()
ax.set_aspect("equal")
ax.patch.set_facecolor('black')
ax.patch.set_alpha(1.0)

fig.set_facecolor("black")

ax.margins(0)

pnts_in_poly.plot(ax=ax, linewidth=1, color="red", markersize=8)

ax.set_xlim(x_lim)
ax.set_ylim(y_lim)
plt.draw()
fig.savefig("red.png")

buf_red = io.BytesIO()
plt.savefig(buf_red, format='png')
buf_red.seek(0)

im_red = Image.open(buf_red)

blurImage_red = im_red.filter(ImageFilter.BLUR)
blurImage_red.show()
blurImage_red.save("red.png","PNG")