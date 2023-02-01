#!/usr/bin/env python3
import os
import argparse

def raw_to_bmp(rawfile, bmpfile):
    # 读16bitraw文件
    with open(rawfile, 'rb') as rf:
        # 'RAWT'
        type = rf.read(4)
        header_size = int.from_bytes(rf.read(4), byteorder = 'little')
        info_size = header_size - 16
        col = int.from_bytes(rf.read(4), byteorder = 'little')
        row = int.from_bytes(rf.read(4), byteorder = 'little')
        info = rf.read(info_size)
        raw_data = rf.read()

    # bmp行尾padding字节数
    row_padding = (4 - col % 4) % 4
    # 处理像素，16bit压缩为8bit
    bmp_data = []
    rowdata = bytearray()
    for i in range(0, len(raw_data), 2):
        rowdata.append(int.from_bytes(raw_data[i:i+2], 'little') >> 8)
        # 行尾添加padding
        if (i % (col * 2) == (col-1) * 2):
            for j in range(0, row_padding):
                rowdata.append(0)
            bmp_data.append(rowdata)
            rowdata = bytearray()
    # bmp是行像素从下到上存储的，需要翻转
    bmp_data = reversed(bmp_data)
    bmp_data = b''.join(bmp_data)

    # struct BITMAPINFOHEADER {
    #     DWORD biSize; // 本结构所占用字节数
    #     LONG biWidth; // 位图的宽度，以像素为单位
    #     LONG biHeight; // 位图的高度，以像素为单位
    #     WORD biPlanes; // 目标设备的平面数不清，必须为 1
    #     WORD biBitCount; // 每个像素所需的位数，必须是 1(双色), 4(16 色)，8(256 色)或 24(真彩色)之一
    #     DWORD biCompression; // 位图压缩类型，必须是 0(不压缩),1(BI_RLE8 压缩类型)或 2(BI_RLE4 压缩类型)之一
    #     DWORD biSizeImage; // 位图的大小，以字节为单位
    #     LONG biXPelsPerMeter; // 位图水平分辨率，每米像素数
    #     LONG biYPelsPerMeter; // 位图垂直分辨率，每米像素数
    #     DWORD biClrUsed; // 位图实际使用的颜色表中的颜色数
    #     DWORD biClrImportant; // 位图显示过程中重要的颜色数
    # }; //该结构占据 40 个字节。
    bmih = (40).to_bytes(4, 'little')
    bmih += (col).to_bytes(4, 'little')
    bmih += (row).to_bytes(4, 'little')
    bmih += (1).to_bytes(2, 'little')
    bmih += (8).to_bytes(2, 'little')
    bmih += (0).to_bytes(4, 'little')
    bmih += (len(bmp_data)).to_bytes(4, 'little')
    bmih += (11811).to_bytes(4, 'little')
    bmih += (11811).to_bytes(4, 'little')
    bmih += (256).to_bytes(4, 'little')
    bmih += (256).to_bytes(4, 'little')

    # 8bit bmp文件必须有color table
    color_table = bytes()
    for i in range(0,256):
        color_table += (i).to_bytes(1, 'little')
        color_table += (i).to_bytes(1, 'little')
        color_table += (i).to_bytes(1, 'little')
        color_table += (0).to_bytes(1, 'little')
    # 为了让像素起始位置对齐到四字节
    gap1 = (0).to_bytes(2, 'little')
    offset = 14 + 40 + len(color_table) + len(gap1)
    bmp_size = offset + len(bmp_data)
    bmp_header = b'BM' + (bmp_size).to_bytes(4, 'little') + (0).to_bytes(4, 'little') + (offset).to_bytes(4, 'little')


    with open(bmpfile, 'wb') as bf:
        bf.write(bmp_header)
        bf.write(bmih)
        bf.write(color_table)
        bf.write(gap1)
        bf.write(bmp_data)

def bmp_to_raw(bmpfile, rawfile):
    with open(bmpfile, 'rb') as bf:
        bf.seek(10)
        # 像素起始位置
        offset = int.from_bytes(bf.read(4), byteorder = 'little')
        bf.seek(18)
        col = int.from_bytes(bf.read(4), byteorder = 'little')
        row = int.from_bytes(bf.read(4), byteorder = 'little')
        bf.seek(34)
        imgsize = int.from_bytes(bf.read(4), byteorder = 'little')
        bf.seek(offset)

        raw_data = []
        row_data = bytes()
        row_padding = (4 - col % 4) % 4
        for i in range(0,row):
            for j in range(0,col):
                # 8位扩展为16位
                row_data += (int.from_bytes(bf.read(1), byteorder = 'little') << 8).to_bytes(2, 'little')
            # 去掉行尾padding
            bf.read(row_padding)
            raw_data.append(row_data)
            row_data = bytes()
        # bmp是行像素从下到上存储的，需要翻转
        raw_data = reversed(raw_data)
        raw_data = b''.join(raw_data)

    raw_header = b'RAWT'
    raw_header += (16).to_bytes(4, 'little')
    raw_header += (col).to_bytes(4, 'little')
    raw_header += (row).to_bytes(4, 'little')

    with open(rawfile,'wb') as rf:
        rf.write(raw_header)
        rf.write(raw_data)


if '__main__' == __name__:
    # 解析命令
    parser = argparse.ArgumentParser(description='Convert each file from srcdir to dstdir, rather from bmp into 16bitraw or 16bitraw into bmp')
    parser.add_argument("srcdir", help="source path")
    parser.add_argument("dstdir", help="destination path")
    args = parser.parse_args()
    srcdir = args.srcdir
    dstdir = args.dstdir
    # 如果dest目录不存在就创建目录
    if not os.path.exists(dstdir):
        os.makedirs(dstdir)
    # 遍历srcdir
    for root, dirs, files in os.walk(srcdir):
        for file in files:
            filename = file.split('.')
            filename = '.'.join(filename[:-1])
            srcfile = os.path.join(srcdir,file)
            # 判断文件头是BM还是RAWT
            with open(srcfile,'rb') as f:
                headname = f.read(2)
            if headname == b"BM":
                dstfile = os.path.join(dstdir,filename+'.16bitraw')
                bmp_to_raw(srcfile, dstfile)
            elif headname == b"RA":
                dstfile = os.path.join(dstdir,filename+'.bmp')
                raw_to_bmp(srcfile, dstfile)