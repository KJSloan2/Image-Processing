from PIL.ExifTags import TAGS
import time
from datetime import datetime
import os
from os import listdir
from os.path import isfile, join
from PIL import Image as pilIm
from PIL.ExifTags import TAGS
from exif import Image
import numpy as np
import imageio.v2 as imageio
import math
import csv
import regex as re

now = datetime.now()
# dd/mm/YY H:M:S
dt_string = now.strftime("%d-%m-%Y_%H-%M-%S_")
print("date and time =", dt_string)


def decimal_coords(coords, ref):
	decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
	if ref == "S" or ref == "W":
		decimal_degrees = -decimal_degrees
	return decimal_degrees


propKeys = [
	"orientation", "x_resolution", "y_resolution", "resolution_unit",
	"datetime", "datetime_original", "datetime_digitized",
	"shutter_speed_value", "aperture_value", "brightness_value",
	"exposure_bias_value", "focal_length", "pixel_x_dimension",
	"pixel_y_dimension", "exposure_mode", "focal_length_in_35mm_film",
	"gps_altitude_ref", "gps_altitude", "gps_speed_ref", "gps_speed",
	"gps_img_direction_ref", "gps_img_direction", "gps_dest_bearing_ref",
	"gps_dest_bearing", "gps_coords"
]


dirPath_images2process = r'PATH TO IMAGE DIRECTORY'
items_in_dir = os.listdir(dirPath_images2process)
store_subFolders = []
for item in items_in_dir:
	split_item = item.split(".")
	if len(split_item) == 1:
		store_subFolders.append(item)
subFolders2make = ["Data_Output","Images_Reformated"]
for subFolderName in subFolders2make:
	if subFolderName not in store_subFolders:
		os.mkdir(os.path.join(dirPath_images2process, subFolderName))

dirPath_output = str("%s%s%s" % (dirPath_images2process,"//",subFolders2make[0]))
dirPath_imageReformated = str("%s%s%s" % (dirPath_images2process,"//",subFolders2make[1]))

PALLETIZE = True
write_imagePalletized = None
writer_imagePalletized = None
if PALLETIZE == True:
	write_imagePalletized = open("%s%s%s" %(dirPath_output,"//","images_palletized.csv"),'w',newline='')
	writer_imagePalletized = csv.writer(write_imagePalletized)
	#writer_imagePalletized.writerow(["docId_long","docId_short","pubDate","docTopic","docTitle","docUrl"])
pi = math.pi

def PointsInCirc(cx, cy, r, n):
	basePoints = [[math.cos(2 * pi / n * x) * r,math.sin(2 * pi / n * x) * r] for x in range(0, n + 1)]
	points = []
	for pt in basePoints:
		points.append([pt[0] + cx, pt[1] + cy])
	return points

sampleWindowSize = [3, 3]
CC_DELTA_MAX = 5
store_img_md = []
store_ImObjs = []
class ImageObj:
	def __init__(self,io0,io1,io2,io3,io4):
		self.id = io0
		self.rgb = io1
		self.grayscale = io2
		self.cords3d = io3
		self.meta_data = io4

files = [f for f in listdir(dirPath_images2process) if isfile(join(dirPath_images2process, f))]
accepted_extensions = ["jpg", "jpeg"]
coordsDefault = [1, 1]
for f in range(len(files)):
	file = files[f]
	fileName = str(dirPath_images2process) + "%s" % (file)
	split_fileName = file.split(".")
	image_name = split_fileName[0]
	is_acceptedExt = str(split_fileName[1]).lower() in accepted_extensions
	if is_acceptedExt == True:
		path_image = "%s%s" % (dirPath_images2process, file)
		store_img_md.append([])
		store_img_md[-1].append("A")
		store_img_md[-1].append(image_name)
		#I'm fixing this...
		'''with open(path_image, "rb") as src:
			img = Image(src)
			if img.has_exif:
				md_lables = img.list_all()
				for propKey in propKeys:
					if propKey == "gps_coords":
						try:
							img.gps_longitude
							coords = (decimal_coords(
								img.gps_latitude,
								img.gps_latitude_ref),
								decimal_coords(img.gps_longitude,img.gps_longitude_ref))
							coord_str = ",".join([str(coords[0]),str(coords[1])])
							store_img_md[-1].append(coord_str)
						except AttributeError:
							store_img_md[-1].append("")
					else:
						try:
							get_prop = (getattr(img, propKey))
							store_img_md[-1].append(str(get_prop))
						except AttributeError:
							store_img_md[-1].append("0")
			else:
				for propKey in propKeys:
					if propKey == "gps_coords":
						store_img_md[-1].append(coordsDefault)
					store_img_md[-1].append(0)
		src.close()'''

		if PALLETIZE == True:
			imageReductionCoef = .7
			src = pilIm.open(path_image)
			image_reformat = src.resize((int(src.size[0] * imageReductionCoef), int(src.size[1] * imageReductionCoef)),pilIm.ANTIALIAS)
			fPath_imRfmt = "%s%s%s%s" % (dirPath_imageReformated,"//",image_name,".jpg")
			image_reformat.save(fPath_imRfmt)
			image = imageio.imread(fPath_imRfmt)

			(palX,palY) = (int(src.size[0] * imageReductionCoef / sampleWindowSize[0]),int(src.size[1] * imageReductionCoef / sampleWindowSize[1]))
			#nPixles = int(image_width) * int(image_height)
			(poolX, poolY) = (sampleWindowSize[0],sampleWindowSize[1])
			iLen = palX + 2
			jLen = palY + 2
			rgb_array = []
			for i in range(iLen):
				rgb_array.append([])
				for j in range(jLen):
					rgb_array[i].append([])
			ImObj = ImageObj(
				0,
				rgb_array,
				np.zeros((iLen, jLen), dtype=int),
				np.zeros((iLen, jLen), dtype=int),
				[]
			)
			with open(path_image, "rb") as src:
				img = Image(src)
				if img.has_exif:
					md_lables = img.list_all()
					for propKey in propKeys:
						if propKey == "gps_coords":
							try:
								img.gps_longitude
								coords = (decimal_coords(
									img.gps_latitude,
									img.gps_latitude_ref),
									decimal_coords(img.gps_longitude,img.gps_longitude_ref))
								coord_str = ",".join([str(coords[0]),str(coords[1])])
								store_img_md[-1].append(coord_str)
							except AttributeError:
								store_img_md[-1].append("")
						else:
							try:
								get_prop = (getattr(img, propKey))
								store_img_md[-1].append(str(get_prop))
							except AttributeError:
								ImObj.meta_data.append("0")
				else:
					for propKey in propKeys:
						if propKey == "gps_coords":
							ImObj.meta_data.append(coordsDefault)
						ImObj.meta_data.append(0)
			src.close()

			for i in range(1, palX - 1, 1):
				x = int(i * poolX)
				for j in range(1, palY - 1, 1):
					y = int(j * poolY)
					pool = image[x:int(x + poolX),y:int(y + poolY), :]
					(pool_r, pool_g, pool_b) = ([], [], [])
					for subArray in pool:
						list(map(lambda rgb: pool_r.append(rgb[0]),subArray))
						list(map(lambda rgb: pool_g.append(rgb[1]),subArray))
						list(map(lambda rgb: pool_b.append(rgb[2]),subArray))

					if len(pool_r) > -0:
						mean_r = int(np.mean(pool_r))
						mean_g = int(np.mean(pool_g))
						mean_b = int(np.mean(pool_b))
						#ImObj.rgb[i][j] = [mean_r*0.0001,mean_g*0.0001,mean_b*0.0001]
						ImObj.rgb[i][j] = [mean_r,mean_g,mean_b]
						ImObj.grayscale[i][j] = round((((mean_r*0.298)+(mean_g*0.587)+(mean_b*0.114))),2)
						
		store_ImObjs.append(ImObj)

import matplotlib.pyplot as plt

pi = math.pi
def construct_circ(r, n):
	return [[math.cos(2 * pi / n * x) * r, math.sin(2 * pi / n * x) * r] for x in range(0, n + 1)]

n_circPts = 36
ref_circPts = []
for v in range(0, n_circPts, 1):
	ref_circPts.append(v)

pp_x = []
pp_y = []
pp_z = []
greyscale_scaled = []
_rgba = []

for i in range(len(store_ImObjs)):
	ImObj = store_ImObjs[i]
	cxy = [0,0]
	#print(md)
	bearing = 0
	delta = []
	for rcp in ref_circPts:
		delta.append(abs(rcp - bearing))
	idx_minDelta = delta.index(min(delta))
	cx = float(cxy[0])
	cy = float(cxy[1])
	circ = construct_circ(0.000003, 36)
	#pt0 = circ[idx_minDelta]
	pta = circ[idx_minDelta + 1]
	ptb = circ[idx_minDelta - 1]
	pta = [pta[0] + cx, pta[1] + cy]
	ptb = [ptb[0] + cx, ptb[1] + cy]
	vec0 = [pta, ptb]
	vd = math.sqrt((int(pta[0]) - int(ptb[0]))**2 + (int(pta[1]) - int(ptb[1]))**2)
	#sin_ab = pta[0]-ptb[0]/vd
	deltaX = pta[0] - ptb[0]
	deltaY = pta[1] - ptb[1]
	shape = ImObj.grayscale.shape
	#cz = shape[1]*.5
	midIncriment = int(int(shape[1]-1)*.5)
	cz = math.sqrt((cx-float(pta[0] + (deltaX * midIncriment)))**2 + (cy-float(pta[1] + (deltaY * midIncriment)))**2)*.25
	zScaler = 0.0000001
	for j in range(1,int(shape[1]-1),1):
		incriment = (1 / shape[1]) * j
		ppX = float(ptb[0] + (deltaX * incriment))
		ppY = float(ptb[1] + (deltaY * incriment))
		for k in range(1,int(shape[0]-1),1):
			rgb = ImObj.rgb[k][j]
			if len(rgb) == 3:
				gs = round((ImObj.grayscale[k][j]/255),2)
				_rgba.append((rgb[0]/255,rgb[1]/255,rgb[2]/255,gs))
				ppZ = k*zScaler
				gsScaler = gs+.05
				pp_x.append(float(cx+(ppX-cx)*gsScaler))
				pp_y.append(float(cy+(ppY-cy)*gsScaler))
				pp_z.append(float(cz+(ppZ-cz)*gsScaler))
				#greyscale_scaled.append(round((gs/255),2))
				greyscale_scaled.append(gs*2)
				
				#print([float(cx+(cx-ppX)*gsVal),float(cy+(cy-ppY)*gsVal),float(cz+(cz-ppZ)*gsVal)],",")


# Creating figure
fig = plt.figure(figsize = (500, 500))
ax = plt.axes(projection ="3d")

#ax.scatter3D(pp_x, pp_y, pp_z,c=_rgba, s=greyscale_scaled)

ax.scatter3D(pp_x, pp_y, pp_z,c=_rgba,marker='o',edgecolors='none',s=greyscale_scaled)
plt.title("Imag")

ax.set_facecolor('black')

ax.grid(True) 
ax.xaxis.pane.fill = False
ax.yaxis.pane.fill = False
ax.zaxis.pane.fill = False

# Now set color to white (or whatever is "invisible")
ax.xaxis.pane.set_edgecolor('b')
ax.yaxis.pane.set_edgecolor('b')
ax.zaxis.pane.set_edgecolor('b')

# Bonus: To get rid of the grid as well:
ax.grid(False)
# show plot
plt.show()
