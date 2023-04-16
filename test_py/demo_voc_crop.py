# -*-coding: utf-8 -*-
"""
    @Author : PKing
    @E-mail : 390737991@qq.com
    @Date   : 2022-11-29 18:11:47
    @Brief  :
"""
import os
import cv2
from tqdm import tqdm
from pybaseutils.dataloader import parser_voc
from pybaseutils import image_utils, file_utils


def save_object_crops(image, out_dir, bboxes, labels, image_id, class_name=None,
                      scale=[], square=False, padding=False, vis=False):
    image_id = image_id.split(".")[0]
    if square:
        bboxes = image_utils.get_square_bboxes(bboxes, use_max=True, baseline=-1)
    if scale:
        bboxes = image_utils.extend_xyxy(bboxes, scale=scale)
    if padding:
        crops = image_utils.get_bboxes_crop_padding(image, bboxes)
    else:
        crops = image_utils.get_bboxes_crop(image, bboxes)
    if vis:
        m = image_utils.draw_image_bboxes_labels(image.copy(), bboxes, labels, class_name=class_name,
                                                 thickness=2, fontScale=0.8, drawType="custom")
        image_utils.cv_show_image("image", m, use_rgb=False, delay=0)
    for i, img in enumerate(crops):
        name = class_name[int(labels[i])] if class_name else labels[i]
        if out_dir:
            img_file = file_utils.create_dir(out_dir, name, "{}_{:0=3d}.jpg".format(image_id, i))
            cv2.imwrite(img_file, img)
        if vis: image_utils.cv_show_image("crop", img, use_rgb=False, delay=0)


if __name__ == "__main__":
    """
    """
    # data_root = "/home/dm/nasdata/dataset-dmai/handwriting/word-det/word-v3"
    filename = "/home/dm/nasdata/dataset/tmp/fall/mixed_fall/file_list.txt"
    # filename = "/home/dm/nasdata/dataset-dmai/handwriting/word-det/word-old/train.txt"
    # class_name = ["face", "face-eyeglasses"]
    # class_name = "/home/dm/nasdata/dataset/tmp/traffic-sign/TT100K/VOC/train/class_name.txt"
    # class_name = ["unique"]
    class_name =None
    # class_name = ['down', 'person']
    out_dir = os.path.join(os.path.dirname(filename), "crops")
    dataset = parser_voc.VOCDataset(filename=filename,
                                    data_root=None,
                                    anno_dir=None,
                                    image_dir=None,
                                    class_name=class_name,
                                    transform=None,
                                    check=False,
                                    use_rgb=False,
                                    shuffle=False)
    print("have num:{}".format(len(dataset)))
    class_name = dataset.class_name
    extend = [1.1, 1.1]
    for i in tqdm(range(len(dataset))):
        try:
            data = dataset.__getitem__(i)
            image, targets, image_id = data["image"], data["target"], data["image_id"]
            bboxes, labels = targets[:, 0:4], targets[:, 4:5]
            save_object_crops(image, out_dir, bboxes, labels, image_id, class_name=class_name, vis=False)
        except Exception as e:
            print("error:{}".format(dataset.index2id(i)))
            print(e)
