#0.0_<import>
import csv
import math
import os
import random
import re
import string
import time
from datetime import datetime
from os import listdir
from os.path import isfile, join
import imageio
import numpy as np
from imageio import imread
from PIL import Image
import PIL
import os
import pandas as pd

now = datetime.now()

dt_string = now.strftime("%d-%m-%Y_%H-%M-%S_")
print("date and time =", dt_string)

imRead_directory = (r'PATH TO IMAGE(S)')

imWrite_directory = (r'PATH TO OUTPUT')
fileNameimWrite = "write_imageDatasegmentation"
write_imageData = open("%s%s%s" % (imWrite_directory,fileNameimWrite,".csv', 'w',newline='')
writer_imageData = csv.writer(write_imageData)

resources_dirPath = r"/Users/kevinsloan/Documents/Python Projects_00/00_Resources/"

UI_SAMPLE_COEF = .85
CC_DELTA_MAX = 5
colors2ignore = [(255,255,255,25),(125,198,135,50)]

def computeHue(r,g,b):
	r_depth = r/255
	g_depth = g/255
	b_depth = b/255
	cMax = max(r_depth,g_depth,b_depth)
	cMin = min(r_depth,g_depth,b_depth)
	delta = (cMax - cMin)+1
	if cMax == r_depth:
		hue = (g_depth - b_depth) / (delta);
	elif cMax == g_depth:
		hue = 2 +(b_depth - r_depth) / (delta);
	elif cMax == b_depth:
		hue = 4 + (r_depth - g_depth) / (delta); 
	if hue > 0:
		hue = (round(hue*60,2))
	else:
		hue = (round(math.floor(360 + hue),2))
	return(hue)

def insertion_sort(vas2insert):
	valsSorted = []
	valFreq = []
	while len(vas2insert) >0:
		valInsert = vas2insert[0]
		vas2insert.remove(vas2insert[0])
		if valInsert != 0:
			if valInsert in valsSorted:
				idx_valInsert = valsSorted.index(valInsert)
				valFreq[idx_valInsert] +=1
			else:
				if len(valsSorted) == 0:
					valsSorted.append(valInsert)
					valFreq.append(1)
				elif len(valsSorted) >= 1:
					deltas = list(map(lambda v: abs(valInsert-v),valsSorted))
					idx_minDelta = deltas.index(min(deltas))
					if valInsert < valsSorted[idx_minDelta]:
						valsSorted.insert(idx_minDelta,valInsert)
						valFreq.insert(idx_minDelta,1)
					elif valInsert > valsSorted[idx_minDelta]:
						valsSorted.insert(idx_minDelta+1,valInsert)
						valFreq.insert(idx_minDelta+1,1)
	return valsSorted,valFreq;

maxGSVal = round((((255*0.298)+(255*0.587)+(255*0.114))),2)
e = 2.718281828459
def sigmoid(z):
	return 1/(1+(e**(-z)))

files = [f for f in listdir(imRead_directory) if isfile(join(imRead_directory, f))]
accepted_extensions = ["jpg","JPG","jpeg","JPEG"]
imPad = 2
fCount = 0
data2plot = []
sampleWindowSize = [3,3]
SEGMENT = True
for f in range(len(files)):
	fCount += 1
	file = files[f]
	fileName = str(imRead_directory)+"%s" % (file)
	split_fileName = file.split(".")
	image_name = split_fileName[0]
	image_ext = split_fileName[1]
	is_acceptedExt = image_ext in accepted_extensions
	if is_acceptedExt == True:
		image2process = Image.open("%s%s" % (imRead_directory,file))
		print("open: ", image_name)
		print(image2process.size[0],image2process.size[1])

		image_reformat = image2process.resize((int(image2process.size[0]*.5),int(image2process.size[1]*.5)), Image.ANTIALIAS)
		image_reformat.save("%s%s%s" % (image_name,"_jpg_",".jpg"))
		image = imageio.imread("%s%s%s" % (image_name,"_jpg_",".jpg"))

		(palX,palY) = (int(image2process.size[0]*.5/sampleWindowSize[0]),int(image2process.size[1]*.5/sampleWindowSize[1]))
		#nPixles = int(image_width) * int(image_height)
		(poolX, poolY) = (sampleWindowSize[0],sampleWindowSize[1])
		
		print(palX,palY)
		print(poolX,poolY)

		class Color_Cube:
			def __init__(self,cc_rgb,cc_hue,cc_gs,cc_ba,cc_fv,cc_ga,cc_edge):
				self.rgb = cc_rgb
				self.hue = cc_hue
				self.gs = cc_gs
				self.binary_array = cc_ba
				self.feature_array = cc_fv
				self.group_array = cc_ga
				self.isEdge_array = cc_edge

		iLen = palX+imPad
		jLen = palY+imPad
		cc_ba = np.zeros((iLen,jLen),dtype=int)
		ColorCubeObjs = []
		for i in range(1,palX-1,1):
			x = int(i*poolX)
			for j in range(1,palY-1,1):
				y = int(j*poolY)
				pool = image[x:int(x+poolX), y:int(y+poolY), :]
				(pool_r,pool_g,pool_b) = ([],[],[])
				for subArray in pool:
					list(map(lambda rgb: pool_r.append(rgb[0]),subArray))
					list(map(lambda rgb: pool_g.append(rgb[1]),subArray))
					list(map(lambda rgb: pool_b.append(rgb[2]),subArray))
				if len(pool_r) >-0:
					mean_r = int(np.mean(pool_r))
					mean_g = int(np.mean(pool_g))
					mean_b = int(np.mean(pool_b))
					mean_gs = round((mean_r*0.298+mean_g*0.587+mean_b*0.114),2)
					mooreNeigborhood = [
						[i-1,j+1],[i,j+1],[i+1,j+1],
						[i-1,j],[i,j],[i+1,j],
						[i-1,j-1],[i,j-1],[i+1,j-1]
						]
					ignoreColor = False
					for cignore in colors2ignore:
						cDist = math.sqrt((int(mean_r)-int(cignore[0]))**2 + (int(mean_b)-int(cignore[2]))**2 + (int(mean_g)-int(cignore[1]))**2)
						if cDist <=  cignore[3]:
							ignoreColor = True
							break
					if ignoreColor == False:
						if len(ColorCubeObjs) == 0:
							new_ccObj = Color_Cube(
								[mean_r,mean_g,mean_b],0,0,
								np.zeros((iLen,jLen),dtype=int),
								np.zeros((iLen,jLen),dtype=int),
								np.zeros((iLen,jLen),dtype=int),
								np.zeros((iLen,jLen),dtype=int)
								)
							new_ccObj.binary_array[i][j]= 1
							ColorCubeObjs.append(new_ccObj)
						else:
							addnew = 0
							for ccObj in ColorCubeObjs:
								ccDelta = math.sqrt((int(mean_r)-int(ccObj.rgb[0]))**2 + (int(mean_b)-int(ccObj.rgb[2]))**2 + (int(mean_g)-int(ccObj.rgb[1]))**2)
								if ccDelta < CC_DELTA_MAX:
									ccObj.binary_array[i][j]= 1
									addnew +=1
									break;
							if addnew == 0:
								new_ccObj = Color_Cube(
									[mean_r,mean_g,mean_b],0,0,
									np.zeros((iLen,jLen),dtype=int),
									np.zeros((iLen,jLen),dtype=int),
									np.zeros((iLen,jLen),dtype=int),
									np.zeros((iLen,jLen),dtype=int)
									)
								new_ccObj.binary_array[i][j]= 1
								ColorCubeObjs.append(new_ccObj)

		for ccObj in ColorCubeObjs:
			rgb = (
				float(ccObj.rgb[0])*.001,
				float(ccObj.rgb[1])*.001,
				float(ccObj.rgb[2])*.001
			)
			idx_nonZeros = np.where(ccObj.binary_array == 1)
			idx_x = list(idx_nonZeros[0])
			idx_y = list(idx_nonZeros[1])
			for x,y in zip(idx_x,idx_y):
				data2plot.append([x,y,rgb])

		if SEGMENT == True:
			#Loop over each collor object
			for ccObj in ColorCubeObjs:
				class Edge_Group:
					def __init__(self,eg_0,eg_1,eg_2,eg_3,eg_4,eg_5,eg_6):
						self.id = eg_0
						self.rgb = eg_1
						self.xy_raw = eg_2
						self.xy_ordered = eg_3
						self.fv_raw = eg_4
						self.fv_ordered = eg_5
						self.viz_color = eg_6

				EdgeGoupObjs = []
				EdgeGoup_ids = []

				pool_groupIds = []
				ref_groupIds = []
				idx_nonZeros = np.where(ccObj.binary_array == 1)
				for i,j in zip(list(idx_nonZeros[0]),list(idx_nonZeros[1])):
					mooreNeigborhood = [
						[i-1,j+1],[i,j+1],[i+1,j+1],
						[i-1,j],[i,j],[i+1,j],
						[i-1,j-1],[i,j-1],[i+1,j-1]
						]
					#ptId = ((i*jLen) + (j-1))
					ptId = str(str(i)+"_"+str(j))
					ref_ptids = []

					def apply_groupIds(groupObject,colorObject,id2apply,neighborhoodCoords):
						for nc in neighborhoodCoords:
							nc_0 = nc[0]
							nc_1 = nc[1]
							colorObject.group_array[nc_0][nc_1] = id2apply
							subGroupCoords = [
								[nc_0-1,nc_1+1],[nc_0,nc_1+1],[nc_0+1,nc_1+1],
								[nc_0-1,nc_1],[nc_0,nc_1],[nc_0+1,nc_1],
								[nc_0-1,nc_1-1],[nc_0,nc_1-1],[nc_0+1,nc_1-1]
								]
							sg_fv = sum(list(map(lambda sgc: colorObject.binary_array[sgc[0]][sgc[1]],subGroupCoords)))
							if 0 < sg_fv < 9:
								groupObject.xy_raw.append([nc_0,nc_1])
								groupObject.fv_raw.append(sg_fv)
						return groupObject

					mn_featurVal = sum(list(map(lambda mn: ccObj.binary_array[mn[0]][mn[1]],mooreNeigborhood)))
					ccObj.feature_array[i][j] = mn_featurVal
					if mn_featurVal == 9:
						ccObj.group_array[i][j] = ptId
						neghborhood_ids = list(map(lambda mn: ccObj.group_array[mn[0]][mn[1]],mooreNeigborhood))
						id_freq = [0]
						id_set = [0]
						for id in neghborhood_ids:
							if id != 0:
								if id not in id_set:
									id_set.append(id)
									id_freq.append(1)
								elif id in id_set:
									id_freq[id_set.index(id)] += 1
						maxFreq = max(id_freq)
						if maxFreq >= 1:
							idx_maxFreq = id_freq.index(maxFreq)
							groupId = id_set[idx_maxFreq]
							#ge_id,ge_rgb,ge_xyRaw,ge_xyOrd,ge_fvRaw,ge_fvOrd
							if groupId not in pool_groupIds:
								pool_groupIds.append(groupId)
								geObj = Edge_Group(groupId,ccObj.rgb,[],[],[],[],[])
								EdgeGoupObjs.append(apply_groupIds(geObj,ccObj,groupId,mooreNeigborhood))
							elif groupId in pool_groupIds:
								idx_geObj = pool_groupIds.index(groupId)
								geObj = EdgeGoupObjs[idx_geObj]
								for mn in mooreNeigborhood:
									i_n = mn[0]
									j_n = mn[1]
									ccObj.group_array[i_n][j_n] = groupId
									subGroupCoords = [
										[i_n-1,j_n+1],[i_n,j_n+1],[i_n+1,j_n+1],
										[i_n-1,j_n],[i_n,j_n],[i_n+1,j_n],
										[i_n-1,j_n-1],[i_n,j_n-1],[i_n+1,j_n-1]
										]
									sg_fv = sum(list(map(lambda sgc: ccObj.binary_array[sgc[0]][sgc[1]],subGroupCoords)))
									if 0 < sg_fv < 9:
										geObj.xy_raw.append([i_n,j_n])
										geObj.fv_raw.append(sg_fv)
						else:
							groupId = ptId
							if groupId not in pool_groupIds:
								pool_groupIds.append(groupId)
								geObj = Edge_Group(groupId,ccObj.rgb,[],[],[],[])
								EdgeGoupObjs.append(apply_groupIds(geObj,ccObj,groupId,mooreNeigborhood))
							elif groupId in pool_groupIds:
								idx_geObj = pool_groupIds.index(groupId)
								geObj = EdgeGoupObjs[idx_geObj]
								for mn in mooreNeigborhood:
									i_n = mn[0]
									j_n = mn[1]
									ccObj.group_array[i_n][j_n] = groupId
									subGroupCoords = [
										[i_n-1,j_n+1],[i_n,j_n+1],[i_n+1,j_n+1],
										[i_n-1,j_n],[i_n,j_n],[i_n+1,j_n],
										[i_n-1,j_n-1],[i_n,j_n-1],[i_n+1,j_n-1]
										]
									sg_fv = sum(list(map(lambda sgc: ccObj.binary_array[sgc[0]][sgc[1]],subGroupCoords)))
									if 0 < sg_fv < 9:
										geObj.xy_raw.append([i_n,j_n])
										geObj.fv_raw.append(sg_fv)

				for EdgeGroupObj in EdgeGoupObjs:
					pool_output = []
					for i in range(len(EdgeGroupObj.xy_raw)):
						xy = EdgeGroupObj.xy_raw[i]
						fv = EdgeGroupObj.fv_raw[i]
						rgb = (
							float(EdgeGroupObj.rgb[0])*.001,
							float(EdgeGroupObj.rgb[1])*.001,
							float(EdgeGroupObj.rgb[2])*.00
						)
						data2plot.append([xy[0],xy[1],rgb])
						pool_output.append(str(xy[0])+","+str(xy[1])+","+str(EdgeGroupObj.id)+","+str(fv))
					join_output  = ";".join(pool_output)
					print(EdgeGroupObj.rgb[0],EdgeGroupObj.rgb[1],EdgeGroupObj.rgb[2],"|",join_output)
					writer_imageData.writerow([EdgeGroupObj.rgb[0],EdgeGroupObj.rgb[1],EdgeGroupObj.rgb[2],"|",join_output])

write_imageData.close()
print("end")
