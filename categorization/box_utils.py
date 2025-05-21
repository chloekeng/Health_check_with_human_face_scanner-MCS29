import cv2
import numpy as np
from pathlib import Path 
from augment.face_org import faceCascade, detector, predictor, FACIAL_LANDMARKS_IDXS
from augment.face_org import readAndResize, resizeImages, getDominantColor, extractFeatures

def get_face_boxes(path_to_img):
    stem = Path(path_to_img).stem   # e.g. "capture"
    status = "tmp"

    # 1) load + optionally resize
    if resizeImages:
        img = readAndResize(path_to_img)
    else:
        img = cv2.imread(path_to_img)
        if img is None or img.size == 0:
            raise RuntimeError("Image load failed")

    # 2) detect face
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, 1.3, 3, minSize=(200,200))
    if not len(faces):
        raise RuntimeError("No face found")
    x,y,w,h = faces[0]
    face_crop = img[y:y+h, x:x+w]

    # 3) get landmarks exactly like extractFace does
    dominant_color = getDominantColor(face_crop)
    shapeFeatures = extractFeatures(
        face_crop,
        detector,
        predictor,
        dominant_color,
        status,
        stem
    )
    if shapeFeatures is None:
        raise RuntimeError("Landmark extraction failed")

    # 4) build boxes
    boxes = {"face": (x, y, w, h)}
    for region, idxs in FACIAL_LANDMARKS_IDXS.items():
        pts = shapeFeatures[idxs]
        xs, ys = pts[:,0], pts[:,1]
        min_x, max_x = int(xs.min()), int(xs.max())
        min_y, max_y = int(ys.min()), int(ys.max())
        boxes[region] = (x+min_x, y+min_y, max_x-min_x, max_y-min_y)
    return boxes
