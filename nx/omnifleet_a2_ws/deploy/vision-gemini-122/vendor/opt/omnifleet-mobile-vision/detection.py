"""Image-space detections for the Android click-to-follow interface."""
import math
import cv2
import numpy as np

COLORS = {'red': ((0, 10), (170, 180)), 'green': ((35, 85),),
          'blue': ((90, 135),), 'yellow': ((18, 35),)}
LABELS = {'color': tuple(COLORS), 'shape': ('rectangle', 'circle', 'triangle'),
          'codes': ('QR', 'AprilTag'), 'off': ()}


def contours(mask, image_area):
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    found, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [c for c in found if 180 <= cv2.contourArea(c) <= image_area * .75]


def circle_bbox(cx, cy, radius, width, height):
    x0, y0 = max(0, round(cx-radius)), max(0, round(cy-radius))
    x1, y1 = min(width, round(cx+radius)), min(height, round(cy+radius))
    return [x0, y0, x1-x0, y1-y0]


def circles_from_image(gray):
    # Search arcs directly, including when the target outline touches the background.
    height, width = gray.shape
    if min(width, height) < 16:
        return
    reduced = cv2.resize(gray, None, fx=.5, fy=.5, interpolation=cv2.INTER_AREA)
    circles = cv2.HoughCircles(reduced, cv2.HOUGH_GRADIENT_ALT, 1.2, 9, param1=200,
                               param2=.92, minRadius=4, maxRadius=min(reduced.shape)//2)
    if circles is not None:
        for cx, cy, radius in circles[0] * 2:
            yield {'label': 'circle', 'bbox': circle_bbox(cx, cy, radius, width, height)}


def detect_shapes(image, labels):
    gray = cv2.GaussianBlur(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), (5, 5), 0)
    edges = cv2.Canny(gray, 60, 150)
    if 'rectangle' in labels:
        # A colored face can have a strong color edge and a weak grayscale edge.
        color_edges = cv2.Canny(cv2.GaussianBlur(image, (5, 5), 0), 60, 150)
        yield from shapes_from_edges(gray, edges | color_edges, {'rectangle'}, 7, cv2.RETR_TREE)
    other_labels = labels - {'rectangle'}
    if other_labels:
        circles = list(circles_from_image(gray)) if 'circle' in labels else []
        yield from circles
        for item in shapes_from_edges(gray, edges, other_labels, 3, cv2.RETR_EXTERNAL):
            if item['label'] == 'circle':
                # Keep the contour-based pass for small targets and merge duplicate rings.
                x, y, w, h = item['bbox']
                if any(math.hypot(x+w/2-a-c/2, y+h/2-b-d/2) <= min(w, h, c, d)/4
                       for a, b, c, d in (circle['bbox'] for circle in circles)):
                    continue
            yield item


def shapes_from_edges(gray, edges, labels, close_size, retrieval):
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((close_size, close_size), np.uint8))
    segments = None
    if labels.intersection(('rectangle', 'triangle')):
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 14, minLineLength=12, maxLineGap=8)
        if lines is not None:
            segments = lines.reshape(-1, 2, 2)

    height, width = gray.shape
    found, _ = cv2.findContours(closed, retrieval, cv2.CHAIN_APPROX_SIMPLE)
    rectangles = []
    for contour in found:
        area = cv2.contourArea(contour)
        if not 180 <= area <= width * height * .75:
            continue
        perimeter = cv2.arcLength(contour, True)
        poly = cv2.approxPolyDP(contour, .025 * perimeter, True)
        if not cv2.isContourConvex(poly):
            continue
        x, y, w, h = cv2.boundingRect(contour)
        if len(poly) >= 6 and 'circle' in labels and .8 <= w / h <= 1.25:
            if 4 * math.pi * area / perimeter**2 < .8:
                continue
            radius = min(w, h) / 2
            left, top = max(0, x - 5), max(0, y - 5)
            roi = gray[top:y+h+5, left:x+w+5]
            circles = cv2.HoughCircles(roi, cv2.HOUGH_GRADIENT, 1.2, min(w, h),
                                       param1=150, param2=18, minRadius=max(4, int(radius * .8)),
                                       maxRadius=int(radius * 1.2))
            if circles is not None:
                cx, cy, r = circles[0, 0]
                yield {'label': 'circle', 'bbox': circle_bbox(left+cx, top+cy, r, width, height)}
            continue

        label = {3: 'triangle', 4: 'rectangle'}.get(len(poly))
        if label not in labels or segments is None:
            continue
        points = poly.reshape(-1, 2).astype(float)
        sides = np.roll(points, -1, axis=0) - points
        lengths = np.linalg.norm(sides, axis=1)
        directions = sides / lengths[:, None]
        if label == 'rectangle' and max(abs(np.sum(directions * np.roll(directions, 1, axis=0), axis=1))) >= .35:
            continue
        for point, direction, length in zip(points, directions, lengths):
            offsets = segments - point
            along = offsets @ direction
            away = offsets @ np.array([-direction[1], direction[0]])
            start = np.maximum(along.min(axis=1), 0)
            end = np.minimum(along.max(axis=1), length)
            nearby = np.abs(away).max(axis=1) <= 5
            if np.any(nearby & (end - start >= .45 * length)):
                continue
            if label != 'rectangle':
                break
            # Hough may split a real edge into several collinear segments.
            covered = last = 0.
            intervals = nearby & (end > start)
            for lo, hi in sorted(zip(start[intervals], end[intervals])):
                covered += max(0., hi - max(lo, last))
                last = max(last, hi)
            if covered < .55 * length:
                break
        else:
            bbox = [x, y, w, h]
            if label == 'rectangle':
                # The inside and outside borders of the same edge can both be traced.
                if any(all(abs(a - b) <= 4 for a, b in zip(bbox, previous)) for previous in rectangles):
                    continue
                rectangles.append(bbox)
            yield {'label': label, 'bbox': bbox}


def detect(image, mode, labels=None):
    height, width = image.shape[:2]
    labels = set(LABELS.get(mode, ()) if labels is None else labels)
    if not labels:
        return []
    result = []
    if mode == 'color':
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        for label, ranges in COLORS.items():
            if label not in labels:
                continue
            mask = np.zeros((height, width), np.uint8)
            for low, high in ranges:
                mask |= cv2.inRange(hsv, (low, 85, 55), (high, 255, 255))
            for contour in contours(mask, width * height):
                result.append({'label': label, 'bbox': list(cv2.boundingRect(contour))})
    elif mode == 'shape':
        result.extend(detect_shapes(image, labels))
    elif mode == 'codes':
        if 'QR' in labels:
            from pyzbar.pyzbar import decode, ZBarSymbol
            for code in decode(image, symbols=[ZBarSymbol.QRCODE]):
                rect = code.rect
                result.append({'label': 'QR', 'text': code.data.decode('utf-8', 'replace'),
                               'bbox': [rect.left, rect.top, rect.width, rect.height]})
        if 'AprilTag' in labels:
            aruco = cv2.aruco
            dictionary = aruco.getPredefinedDictionary(aruco.DICT_APRILTAG_36h11)
            if hasattr(aruco, 'ArucoDetector'):
                corners, ids, _ = aruco.ArucoDetector(dictionary, aruco.DetectorParameters()).detectMarkers(image)
            else:
                corners, ids, _ = aruco.detectMarkers(image, dictionary, parameters=aruco.DetectorParameters_create())
            if ids is not None:
                for polygon, identity in zip(corners, ids.flatten()):
                    result.append({'label': 'AprilTag', 'text': str(int(identity)),
                                   'bbox': list(cv2.boundingRect(polygon.astype(np.float32)))})
    return sorted(result, key=lambda item: (item['label'], item['bbox'][0], item['bbox'][1]))[:40]


def select_detection(frames, frame_id, index):
    frame = frames.get(frame_id)
    if frame is None or not isinstance(index, int) or not 0 <= index < len(frame['detections']):
        raise ValueError('检测结果已更新，请再次点击目标')
    return frame['detections'][index]
