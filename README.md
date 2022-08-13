# Image-Processing
This is an ongoing project of developing novel approaches to color image segmentation and feature extraction. 
![image](https://user-images.githubusercontent.com/61387934/184516228-291fb10d-53ae-4c15-bb1b-92b4010c851c.png)


# Palletization & Color Layer Separation

The first steps in this project involve palletizing the base image and separating pixels into individual layers based on their RGB color value. 

The base image is divided into subregions, where pixel RGB values are pooled and averaged to yield a mean RBG value for the region. The color is then plotted into an RGB space color cube and the euclidian distance is tested to existing colors. 

If the minimum euclidian distance is less than a defined threshold (in this case, 10) the indexes (i,j) of the pixel are grouped with the closest color. If the minimum euclidian distance is greater than the threshold, a new color point is added to the model and a new color layer class object is created.

![image](https://user-images.githubusercontent.com/61387934/184516261-7929a523-6c55-45d1-b00e-0009cf100d94.png)

![image](https://user-images.githubusercontent.com/61387934/184516280-b70f3df9-4bcf-4c45-b068-0af857409f39.png)

# Separated Color Layers

The palletized image is separated into distinct color layers contained in class objects. This graphic visualizes the separated layers. The Z value of each layer is determined by the grayscale value of the layers RGB values.

![image](https://user-images.githubusercontent.com/61387934/184516301-3a234cfb-9c01-47f2-875e-46c7e80cf92b.png)


