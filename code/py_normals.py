import cv2
import sys
import numpy as np
import scipy.io

def depth_to_world(D):
    imh = D.shape[0]
    imw = D.shape[1]
    center = [imh/2, imw/2]
    constant = 570.3

    xgrid = np.ones((imh, 1)) * np.arange(0, imw) - center[1]
    ygrid = np.mat(np.arange(0, imh)).T * np.ones((1, imw)) - center[0]
    
    pcloud = np.zeros((imh, imw, 3))
    pcloud[:, :, 0] = np.multiply(xgrid, D)/constant
    pcloud[:, :, 1] = np.multiply(ygrid, D)/constant
    pcloud[:, :, 2] = D

    return pcloud

def pc_normal(pcloud):
    threshold = 0.01
    win = 6
    mindata = 3
    imh = pcloud.shape[0]
    imw = pcloud.shape[1]
    normals = np.zeros((imh, imw, 3))

    for i in range(0, imh):
        for j in range(0, imw):
            minh = np.maximum(i-win, 0)
            maxh = np.minimum(i+win, imh-1)
            minw = np.maximum(j-win, 0)
            maxw = np.minimum(j+win, imw-1)

            pcdis = pcloud[minh:maxh, minw:maxw, 2] - pcloud[i, j, 2]
            pcdis = np.sqrt(np.multiply(pcdis, pcdis))
            pcij = np.sqrt(np.sum( np.multiply(pcloud[i, j, :], pcloud[i, j, :]) ))

            index = pcdis < pcij*threshold
            if np.sum(index) > mindata and pcij>0:
                wpc = pcloud[minh:maxh, minw:maxw, :]
                subwpc = wpc[index, :]
                subwpc = subwpc-np.mean(subwpc, axis=0)
                w,v = np.linalg.eig(np.mat(subwpc.T)*np.mat(subwpc))

                # Sort to find the smallest eigenvalue and its associated eigenvector
                idx = w.argsort()
                vSort = v[:, idx]
                normals[i, j, :] = vSort[:, 0].flatten()

    dd = np.sign(np.sum(np.multiply(pcloud, normals), axis=2))
    normals[:, :, 0] = np.multiply(normals[:, :, 0], dd)
    normals[:, :, 1] = np.multiply(normals[:, :, 1], dd)
    normals[:, :, 2] = np.multiply(normals[:, :, 2], dd)

    return normals


def get_normals(pcloud):
    N = pc_normal(pcloud)
    return N, 0

im = cv2.imread('/Users/bdol/Dropbox/dframes/depth_00019.png', -1)
im[im>489] = 0

pcloud = depth_to_world(im)
normals, valid = get_normals(pcloud)

