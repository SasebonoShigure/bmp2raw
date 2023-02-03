#!/usr/bin/env python3
from PIL import Image
import os
import argparse

def merge_images(pathname, merged_file, vertical):
    # 依次读取路径中的bmp文件
    images = []
    for file in os.listdir(pathname):
        if file.endswith(".bmp"):
            image = Image.open(os.path.join(pathname, file))
            images.append(image)
    if vertical:
        # 如果vertical == True，竖直合并
        max_width = max(image.size[0] for image in images)
        total_height = sum(image.size[1] for image in images)
        # "L"：保存为8位bmp
        result = Image.new("L", (max_width, total_height))
        offset = 0
        for image in images:
            result.paste(image, (0, offset))
            offset += image.size[1]
    else:
        # 如果vertical == False，水平合并
        total_width = sum(image.size[0] for image in images)
        max_height = max(image.size[1] for image in images)
        # "L"：保存为8位bmp
        result = Image.new("L", (total_width, max_height))
        offset = 0
        for image in images:
            result.paste(image, (offset,0))
            offset += image.size[0]
    result.save(merged_file)


if '__main__' == __name__:
    # 解析命令
    parser = argparse.ArgumentParser(description='Merge bmp files into one 8-bit bmp')
    parser.add_argument("srcdir", help = "Source path")
    parser.add_argument("merged_file_name", help = "File name of merged image")
    parser.add_argument("mode",help = "v for vertical, h for horizontal")
    args = parser.parse_args()
    if args.mode == 'v':
        merge_images(args.srcdir, args.merged_file_name, True)
    elif args.mode == 'h':
        merge_images(args.srcdir, args.merged_file_name, False)
    else :
        print('invalid parameter')
        quit()