# -*-coding: utf-8 -*-
"""
    @Author : Pan
    @E-mail : 390737991@qq.com
    @Date   : 2022-11-17 18:43:21
    @Brief  :
"""
from pybaseutils import file_utils, image_utils
from pybaseutils.cvutils import video_utils

if __name__ == "__main__":
    image_dir = "/home/PKing/nasdata/release/tmp/Character-Recognition-Pytorch/data/test_image"
    gif_file = image_dir + ".gif"
    frames = file_utils.get_images_list(image_dir)
    # image_utils.image_file2gif(frames, size=(256, None), padding=False, interval=1, gif_file=gif_file, fps=2)
    # image_utils.image_file2gif(frames, size=(640, 640), padding=True, interval=1,
    #                            gif_file=gif_file, fps=1, use_pil=True)

    video_file = image_dir + ".mp4"
    video_utils.frames2video(image_dir, size=(416, 416), video_file=video_file,fps=1)
