import numpy as np
import cv2

#Function to give the cluster arrays
#Input: K-Means output image
#Output: Produces k arrays, where in each array the kth cluster pixels will have value 1 and remaining pixels will have value 0

def clusters_segmentation(array_to_be_segmented):
  final_segmented_array = []
  check_value_list = np.unique(array_to_be_segmented)
  #print(check_value_list)
  r = len(array_to_be_segmented)
  c = len(array_to_be_segmented[0])
  for i in  range(len(check_value_list)):
    temp_f = []
    for j in range(r):
      temp_a = []
      for k in range(c):
        if(array_to_be_segmented[j][k] == check_value_list[i]):
          temp_a.append(1)
        else:
          temp_a.append(0)
      temp_f.append(temp_a)
    final_segmented_array.append(temp_f)
  return final_segmented_array


#Function to produce the longest connected component
#Input: Clustered Image
#Output: 2 values: 
# 1) maxi_row which contains maxiumum connected component in each row 
# 2) maxi_col which contains maxiumum connected component in each column
def longest_connected_component(clustered_image):
    
    r = len(clustered_image)
    c = len(clustered_image[0])
 
    maxi_col = []
    temp_count_col = -1

    for j in range(r):
        temp_count  = 0
        for k in range(c-1):
            if(clustered_image[j][k] == 1) and (clustered_image[j][k+1]!=0):
                temp_count += 1
            else:
                temp_count += 1
                if(temp_count > temp_count_col):
                    temp_count_col = temp_count
                    temp_count  = 0 
        maxi_col.append(temp_count_col)
        temp_count_col = 0
  
    maxi_row = []
    temp_count_row = -1
    for j in range(c):
        temp_count = 0
        for k in range(r-1):
            if(clustered_image[k][j] == 1) and (clustered_image[k+1][j]!=0):
                temp_count  += 1
            else:
                temp_count += 1 
                if(temp_count > temp_count_row):
                    temp_count_row = temp_count
                    temp_count  = 0 
        maxi_row.append(temp_count_row)
        temp_count_row=0
    
    maxi_row_count = 0
    max_col_count = 0
    for i in range(len(maxi_row)):
      if(maxi_row[i] > ((r/2))):
        maxi_row_count += 1
    for j in range((len(maxi_col))):
      if(maxi_col[j] > ((c/2))):
        max_col_count += 1


    return maxi_row_count,max_col_count
 

#Function to road cluster segmentation
#Input: List of clustered images after clusters_segmentation()
#Output: Road cluster segmented image
def solve(cluster_images_list):
  final_ans = -1
  final_index = -1

  # print(len(cluster_images_list))
  for i in range(len(cluster_images_list)):
    r_count, c_count = longest_connected_component(cluster_images_list[i])
    if((r_count + c_count) >= final_ans):
      final_ans = (r_count + c_count) 
      final_index = i

  # print(final_index)
  final_clustered_list = cluster_images_list[final_index]
  r =  len(final_clustered_list)
  c =  len(final_clustered_list[0])
  for i in range(r):
    for j in range(c):
      if(final_clustered_list[i][j] == 1):
        final_clustered_list[i][j] = 255
  # plt.imshow(final_clustered_list,cmap="gray", vmin=0, vmax=255)
  # plt.show()
  return final_clustered_list
  #Uncomment these to write the image
  #a = np.array(final_clustered_list)
  #cv2.imwrite('C:/Users/Radha Krishna/final_image_1.png',a)


#Imporivng the intensities for better visualization
def preprocess(clustered_image):
    #Reading the image after k-means clustering

    c_img = cv2.cvtColor(clustered_image, cv2.COLOR_RGB2GRAY) 
    # print(np.unique(clustered_image))
    r,c = c_img.shape
    dummy_v = []
    for i in range(r):
        t = []
        for j in range(c):
            if(c_img[i][j] == 164):
                t.append(255)
            elif(c_img[i][j] == 76):
                t.append(0)
            else:
                t.append(127)
        dummy_v.append(t)
    # plt.imshow(dummy_v,cmap="gray", vmin=0, vmax=255)
    # plt.show()
    return dummy_v


def longest_component_identification(clustered_image):
    # vary intensities for better visualization
    dummy_v = preprocess(clustered_image)
    #Create clusters segmented list
    clusters_segmented_array = clusters_segmentation(dummy_v)
    #Call the solve method with clustered segemneted images as input
    final_clustered_list = solve(clusters_segmented_array)
    return final_clustered_list
