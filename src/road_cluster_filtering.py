import numpy as np
import sys
import cv2
import matplotlib.pyplot as plt
from .road_cluster_identification import *

sys.setrecursionlimit(20000)

# Appyling dialation and erosion
def morphological_operations(img, k_d=2, itr_d=1, k_e=2, itr_e=1):
    image = np.array(img, dtype=np.uint8)
    kernel_e = np.ones((k_e,k_e), np.uint8)
    output_img = cv2.erode(image, kernel_e, iterations=itr_e)
    kernel_d = np.ones((k_d,k_d), np.uint8)
    output_img = cv2.dilate(output_img, kernel_d, iterations=itr_d)
    return output_img


# Removing non-road areas

#Function for 2Pass alogorithm 
#Input: Image for the dilation process or any image which has only 2 unique either
# foreground(1) or background(0)
#Output: Image after 2 pass alogrithm
def two_pass_algo(nodes_list,fly):
    r = len(nodes_list)
    c = len(nodes_list[0])
    dict_1 = {}
    labels = 0
    two_pass_arr = []
    for i in range(r):
        two_pass_temp = []
        for j in range(c):
            if(nodes_list[i][j] == 0):
                two_pass_temp.append(0)
            else:
                val_1 = 0
                val_2 = 0
                if((i-1)>=0):
                    val_1 = two_pass_arr[i-1][j]
                if((j-1)>=0):
                    val_2 = two_pass_temp[j-1]
                
                if(val_1 == 0 and val_2 == 0):
                    labels += 1
                    two_pass_temp.append(labels)
                elif(val_1 == val_2):
                    two_pass_temp.append(val_1)
                elif(val_1 == 0):
                    two_pass_temp.append(val_2)
                elif(val_2 == 0):
                    two_pass_temp.append(val_1)
                else:
                    two_pass_temp.append(min(val_1,val_2))
                    key_dict =  max(val_1,val_2)
                    value_dict = min(val_1,val_2)
                    if(key_dict in dict_1.keys()):
                        if(value_dict < dict_1[key_dict]):
                            dict_1[key_dict] = value_dict
                    elif(value_dict in dict_1.keys()):
                        dict_1[key_dict] = dict_1[value_dict]
                    else:
                      dict_1[key_dict] = value_dict
           
        two_pass_arr.append(two_pass_temp)
    
    for i in range(r):
        for j in range(c):
            key_1 =  two_pass_arr[i][j]
            if key_1 in dict_1.keys():
                two_pass_arr[i][j] =  dict_1[key_1]
    
    #print(len(np.unique(two_pass_arr)))

    dict_keys_two_pass_arary = {}
    
    for i in range(len(two_pass_arr)):
      for j in range(len(two_pass_arr[0])):
        if(two_pass_arr[i][j] != 0):
          if(two_pass_arr[i][j] not in dict_keys_two_pass_arary.keys()):
            dict_keys_two_pass_arary[two_pass_arr[i][j]] = 1
          else:
            dict_keys_two_pass_arary[two_pass_arr[i][j]] += 1
    
    #print(len(dict_keys_two_pass_arary.keys()))
    dict_keys_two_pass_arary = dict(sorted(dict_keys_two_pass_arary.items(), key=lambda item: item[1]))
    #print(dict_keys_two_pass_arary)
    key_dict_sorted = list(dict_keys_two_pass_arary.keys())
    #print(len(key_dict_sorted))
    len_keys = len(key_dict_sorted)
    
    final_keys = []
    for i in range(fly):
      #print(str(i))
      index = len_keys - i
      final_keys.append(key_dict_sorted[index-1])
    
    for i in range(len(two_pass_arr)):
      for j in range(len(two_pass_arr[0])):
        if(two_pass_arr[i][j] in final_keys):
          two_pass_arr[i][j] = 255
        else:
          two_pass_arr[i][j] = 0
      
    return two_pass_arr



def remove_nonroad_areas(dilated_image, num_clusters=2):
    r,c = dilated_image.shape
    dummy_v = []
    for i in range(r):
        t = []
        for j in range(c):
            if(dilated_image[i][j] == 255):
                t.append(1)
            else:
                t.append(0)
        dummy_v.append(t)
    #print(np.unique(dummy_v))
    #Call the solve method with clustered segemneted images as input
    ans = two_pass_algo(dummy_v,num_clusters)
    #plt.imshow(ans,cmap="gray", vmin=0, vmax=255)
    return ans
