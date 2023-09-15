import numpy as np
import random

#function for total residual error between the old and new centriods
def error_l2_norm(x,y,k):
  error = 0
  for i in range(k):
    error += np.linalg.norm(x[i,:]-y[i,:], ord=None)
  return error

def image_cluster(im,k):
  clustered_im = im  
  centroids = np.zeros([k,3]).astype(int)
  new_centroids = np.zeros([k,3])
  for i in range(k):
    centroids[i,:] = [random.randint(0,256),random.randint(0,256),random.randint(0,256)]
    new_centroids[i,:] = ['inf','inf','inf']
  
  cluster_color_id = np.zeros([k,3]).astype(int)
  cluster_color_id[:,0] = np.linspace(0, 255 , num=k)
  cluster_color_id[:,1] = np.linspace(255, 0 , num=k)
  cluster_color_id[0:int((k+1)/2),2] = cluster_color_id[int(k/2):k,0]
  cluster_color_id[int((k+1)/2):k,2] = cluster_color_id[0:int(k/2),0]
  
  n = 0
  dictionary = {}
  while error_l2_norm(centroids,new_centroids,k) >= 0.01 * k:
    centroids = new_centroids
    if n == 0:
      new_centroids = np.zeros([k,3])
      n += 1
    dist = np.zeros([k])
    
    points_in_centroid = np.zeros([k])
    for i in range(im.shape[0]):
      for j in range(im.shape[1]):
        for m in range(k):
          dist[m] = np.linalg.norm(im[i][j]-centroids[m,:], ord=None)
        min_dist = np.argmin(dist)
        dictionary[(i,j)] = min_dist
        points_in_centroid[min_dist] +=1
        new_centroids[min_dist,:] = (new_centroids[min_dist,:] * (points_in_centroid[min_dist] - 1) + im[i][j]) / points_in_centroid[min_dist]
        
  for i in range(im.shape[0]):
    for j in range(im.shape[1]):
      a = dictionary[(i,j)]
      clustered_im[i][j] = cluster_color_id[a,:]

  return clustered_im