# -*-coding: utf-8 -*-
"""
    @Author : panjq
    @E-mail : pan_jinquan@163.com
    @Date   : 2021-09-08 16:58:52
"""

import math
import random
import torch
import cv2
import numpy as np


def xyxy2xywh(xyxy: np.ndarray):
    """(xmin,ymin,xmax,ymax)==>(xmin,ymin,w,h)"""
    xywh = xyxy.copy()
    xywh[:, 2] = xywh[:, 2] - xywh[:, 0]  # w=xmax-xmin
    xywh[:, 3] = xywh[:, 3] - xywh[:, 1]  # w=ymax-ymin
    return xywh


def xywh2xyxy(xywh: np.ndarray):
    """(xmin,ymin,w,h)==>(xmin,ymin,xmax,ymax)"""
    xyxy = xywh.copy()
    xyxy[:, 2] = xyxy[:, 0] + xyxy[:, 2]  # xmax=xmin+w
    xyxy[:, 3] = xyxy[:, 1] + xyxy[:, 3]  # ymax=ymin+h
    return xyxy


def xyxy2cxcywh(xyxy: np.ndarray, width=None, height=None, normalized=False):
    """(xmin, ymin, xmax, ymax)==>(cx,cy,w,h)"""
    cxcywh = np.zeros_like(xyxy)
    cxcywh[:, 0] = (xyxy[:, 2] + xyxy[:, 0]) / 2  # cx
    cxcywh[:, 1] = (xyxy[:, 3] + xyxy[:, 1]) / 2  # cy
    cxcywh[:, 2] = (xyxy[:, 2] - xyxy[:, 0])  # w
    cxcywh[:, 3] = (xyxy[:, 3] - xyxy[:, 1])  # h
    if normalized:
        cxcywh = cxcywh / (width, height, width, height)
    return cxcywh


def cxcywh2xyxy(cxcywh: np.ndarray, width=None, height=None, normalized=False):
    """(cx,cy,w,h)==>xmin, ymin, xmax, ymax)"""
    xyxy = np.zeros_like(cxcywh)
    xyxy[:, 0] = cxcywh[:, 0] - cxcywh[:, 2] / 2  # top left x
    xyxy[:, 1] = cxcywh[:, 1] - cxcywh[:, 3] / 2  # top left y
    xyxy[:, 2] = cxcywh[:, 0] + cxcywh[:, 2] / 2  # bottom right x
    xyxy[:, 3] = cxcywh[:, 1] + cxcywh[:, 3] / 2  # bottom right y
    if normalized:
        xyxy = xyxy * (width, height, width, height)
    return xyxy


def extend_xyxy(xyxy: np.ndarray, scale=[1.0, 1.0]):
    """
    :param bboxes: [[xmin, ymin, xmax, ymax]]
    :param scale: [sx,sy]==>(W,H)
    :return:
    """
    cxcywh = np.zeros_like(xyxy, dtype=xyxy.dtype)
    cxcywh[:, 0] = (xyxy[:, 2] + xyxy[:, 0]) / 2  # cx
    cxcywh[:, 1] = (xyxy[:, 3] + xyxy[:, 1]) / 2  # cy
    cxcywh[:, 2] = (xyxy[:, 2] - xyxy[:, 0]) * scale[0]  # w
    cxcywh[:, 3] = (xyxy[:, 3] - xyxy[:, 1]) * scale[1]  # h
    dxyxy = cxcywh2xyxy(cxcywh, width=None, height=None, normalized=False)
    return dxyxy


def extend_xywh(xywh: np.ndarray, scale=[1.0, 1.0]):
    """
    :param bboxes: [[xmin, ymin, xmax, ymax]]
    :param scale: [sx,sy]==>(W,H)
    :return:
    """
    xyxy = xywh2xyxy(xywh)
    xyxy = extend_xyxy(xyxy, scale)
    dxywh = xyxy2xywh(xyxy)
    return dxywh


def get_square_bboxes(boxes, use_max=True):
    """
    将bboxes转换为正方形的bboxes
    :param boxes:
    :param use_max: 是否按照每个box(w,h)最大值进行转换
    :return:
    """
    if not isinstance(boxes, np.ndarray):
        boxes = np.asarray(boxes)
    center = xyxy2cxcywh(boxes)
    if use_max:
        b = np.max(center[:, 2:4], axis=1)
    else:
        b = np.min(center[:, 2:4], axis=1)
    b = b.reshape(len(boxes), 1)
    center[:, 2:4] = b
    _boxes = cxcywh2xyxy(center)
    return _boxes


def get_square_rects(rects, use_max=True):
    """
    将rects转换为正方形的bboxes
    :param rects: xywh
    :param use_max: 是否按照每个box(w,h)最大值进行转换
    :return:
    """
    boxes = xywh2xyxy(rects)
    boxes = get_square_bboxes(boxes, use_max=use_max)
    rects = xyxy2xywh(boxes)
    return rects


class YOLOCoords(object):
    def __init__(self, max_boxes=120, norm=False):
        self.max_boxes = max_boxes
        self.norm = norm

    def __call__(self, image, boxes, labels):
        dboxes = np.zeros((self.max_boxes, 4))
        dlabels = np.zeros((self.max_boxes))
        if len(boxes) > 0:
            width, height, _ = image.shape
            cboxes = xyxy2cxcywh(boxes, width, height, normalized=self.norm)
            dboxes[0:len(cboxes)] = cboxes
            dlabels[0:len(cboxes)] = labels
        return image, dboxes, dlabels


def show_image(name, image, boxes, labels, center2bboxes=False, untranspose=False, waitKey=0):
    from utils import image_utils
    if center2bboxes:
        boxes = cxcywh2xyxy(boxes)
    if untranspose:
        image = image_utils.untranspose(image)
    image = image_utils.show_image_bboxes_text(name, image, boxes, labels, delay=waitKey)
    return image


def demo_for_augment():
    from utils import image_utils
    input_size = [320, 320]
    image_path = "test.jpg"
    boxes = [[98, 42, 160, 100], [244, 260, 297, 332], [98 + 50, 42 + 50, 160 + 50, 100 + 50]]
    labels = [1, 2, 3]
    image = image_utils.read_image(image_path)
    boxes = np.asarray(boxes, np.float32)
    labels = np.asarray(labels)
    augment = YOLOCoords(max_boxes=120, norm=False)
    for i in range(1000):
        boxes = extend_xyxy(boxes, scale=[1.2, 1.2])
        dst_image, dst_label, dst_boxes = augment(image, boxes.copy(), labels.copy())
        image = show_image("detd", image, dst_label, dst_boxes, center2bboxes=True, untranspose=False, waitKey=0)


if __name__ == "__main__":
    demo_for_augment()
