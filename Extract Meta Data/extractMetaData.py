import os
from os import listdir
from os.path import isfile, join
from PIL import Image
from PIL.ExifTags import TAGS
from exif import Image

dirPath_images = (r'PATH TO IMAGES')
files = [f for f in listdir(dirPath_images) if isfile(join(dirPath_images, f))]

def decimal_coords(coords, ref):
	decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
	if ref == "S" or ref == "W":
		decimal_degrees = -decimal_degrees
	return decimal_degrees

propKeys = [
	"make","model","orientation","x_resolution","y_resolution","resolution_unit",
	"software","datetime","exposure_time","f_number","exposure_program",
	"photographic_sensitivity","datetime_original","datetime_digitized","shutter_speed_value",
	"aperture_value","brightness_value","exposure_bias_value","metering_mode","flash",
	"focal_length","subject_area","subsec_time_original","subsec_time_digitized",
	"color_space","pixel_x_dimension","pixel_y_dimension","sensing_method",
	"exposure_mode","white_balance","focal_length_in_35mm_film","scene_capture_type",
	"lens_specification","gps_altitude_ref","gps_altitude","gps_speed_ref","gps_speed","gps_img_direction_ref",
	"gps_img_direction","gps_dest_bearing_ref","gps_dest_bearing","gps_datestamp","gps_coords"
	]
accepted_extensions = ["jpg","jpeg"]	
for f in range(len(files)):
	file = files[f]
	fileName = str(dirPath_images)+"%s" % (file)
	split_fileName = file.split(".")
	image_name = split_fileName[0]
	image_ext = str(split_fileName[1]).lower()
	is_acceptedExt = image_ext in accepted_extensions
	if is_acceptedExt == True:
		path_image = "%s%s" % (dirPath_images,file)
		with open(path_image, "rb") as src:
			img = Image(src)
			store_img_md = []
			if img.has_exif:
				md_lables = img.list_all()
				for propKey in propKeys:
					if propKey == "gps_coords":
						try:
							img.gps_longitude
							coords = (decimal_coords(
								img.gps_latitude,img.gps_latitude_ref),
								decimal_coords(img.gps_longitude,
								img.gps_longitude_ref
								))
							coord_str = ",".join([str(coords[0]),str(coords[1])])
							store_img_md.append(coord_str)
						except AttributeError:
							store_img_md.append("")
					else:
						try:
							get_prop = (getattr(img, propKey))
							store_img_md.append(get_prop)
						except AttributeError:
							store_img_md.append("")
			for pk,d in zip(propKeys,store_img_md):
				print(pk,": ",d)
