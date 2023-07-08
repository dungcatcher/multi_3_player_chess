import math


first_segment_points = [
    (169, 683), (262, 629), (353, 576), (447, 522), (541, 468), (635, 522), (729, 576), (820, 629), (913, 683),
    (200, 737), (284, 697), (369, 656), (456, 616), (541, 576), (626, 616), (713, 656), (798, 697), (882, 737),
    (230, 790), (306, 765), (384, 738), (463, 711), (541, 684), (619, 711), (698, 738), (776, 765), (852, 790),
    (262, 844), (327, 832), (398, 817), (470, 802), (541, 788), (612, 802), (684, 817), (755, 832), (820, 844),
    (293, 898), (350, 898), (413, 898), (476, 898), (541, 898), (606, 898), (669, 898), (732, 898), (789, 898)
]


def rotate_origin(origin, point, degrees):
    angle = math.radians(degrees)

    ox, oy = origin
    px, py = point

    qx = round(ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy))
    qy = round(oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy))
    return qx, qy


def gen_polygons():
    segment_polygons = []  # [segment: [polygon], ...]

    for segment in range(3):
        degrees = 120 * segment
        rotated_segment_points = []
        rotated_segment_polygons = []

        for point in first_segment_points:
            new_point = rotate_origin((541, 468), point, degrees)
            rotated_segment_points.append(new_point)

        for row in range(4):
            for col in range(8):
                index = row * 9 + col
                poly = [
                    rotated_segment_points[index], rotated_segment_points[index + 1],
                    rotated_segment_points[index + 10], rotated_segment_points[index + 9]
                ]
                rotated_segment_polygons.append(poly)

        segment_polygons.append(rotated_segment_polygons)

    return segment_polygons


def resize_polygons(polygons, scale, topleft):
    new_polygons = []
    for segment in polygons:
        new_segment = []
        for poly in segment:
            new_poly = []
            for vertex in poly:
                new_poly.append((vertex[0] * scale + topleft[0], vertex[1] * scale + topleft[1]))
            new_segment.append(new_poly)
        new_polygons.append(new_segment)

    return new_polygons





