"""Sample an OpenCV Zoo BlazePose region directly at the model input size."""
import cv2
import numpy as np


def preprocess_pose(model, image, person):
    center, scale_point = person[4:8].reshape(2, 2)
    radius = np.linalg.norm(center - scale_point)
    corners = np.array([center-radius, center+radius], dtype=np.int32)
    origin, end = corners
    width, height = end-origin
    left, top = np.maximum(origin, 0)
    right, bottom = np.minimum(end, image.shape[1::-1])
    if left >= right or top >= bottom:
        return type(model)._preprocess(model, image, person)

    dx, dy = scale_point-center
    angle = np.degrees(np.pi/2 - np.arctan2(-dy, dx))
    angle = (angle+180) % 360 - 180
    rotation = cv2.getRotationMatrix2D(tuple(map(float, center-origin)), float(angle), 1.)

    # Compose the original rotate and resize operations, including resize's
    # pixel-center offset. Keep ROI metadata for Zoo's landmark reprojection.
    affine = rotation.copy()
    affine[:, 2] += rotation[:, :2] @ (np.array([left, top])-origin)
    ratio = model.input_size / np.array([width, height])
    affine *= ratio[:, None]
    affine[:, 2] += (ratio-1)*.5
    model_size = tuple(map(int,model.input_size))
    source = image[top:bottom,left:right]
    if min(ratio) < .75:
        # Area sampling before rotation prevents aliasing on large regions.
        source_size = np.array(source.shape[1::-1])
        reduced_size = np.maximum(1,np.rint(source_size*min(ratio)*1.25)).astype(int)
        source = cv2.resize(source,tuple(reduced_size),interpolation=cv2.INTER_AREA)
        inverse_ratio = source_size/reduced_size
        affine[:,2] += affine[:,:2] @ ((inverse_ratio-1)*.5)
        affine[:,:2] *= inverse_ratio[None,:]
    blob = cv2.warpAffine(source, affine, model_size,
                          flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    blob = cv2.cvtColor(blob,cv2.COLOR_BGR2RGB).astype(np.float32) / 255.
    bounds = np.array([[0,0],[width,height]],dtype=np.int32)
    return blob[None], bounds, angle, rotation, origin
