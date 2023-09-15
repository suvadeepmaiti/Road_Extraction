import cv2
import numpy as np
from .kmeans_clustering import image_cluster

def run_roadId(fname,fg):
    im = cv2.imread(fname)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    # im = cv2.resize(im, (200,200))
    r,c = im.shape[:2]

    # check if any area is marked manually
    if len(fg)==0:
        return image_cluster(im,3)
    else:
        mask = im.copy()
        mask_val = (0,255,0)
        clip_val = c - 1
        for y1, x1, y2, x2 in fg:
            if x1==x2:
                mask[x1:x1+5, min(y1, y2):max(y1, y2)+1, :] = mask_val
            else:
                k = (y1 - y2) / (x1 - x2)
                x, y = (x1, y1) if x1 < x2 else (x2, y2)
                while True:
                    mask[x:x+5, y:y+5, :] = mask_val
                    x = x+1
                    y = np.clip(int(round(y+k)), 0, clip_val)
                    if x > max(x1, x2):
                        break
        return image_cluster(mask,3)
