from PIL import Image
from PyPDF2 import PdfFileMerger
import os

PAGE_SENSITIVITY = 0.70
TEXT_SENSITIVITY = 0.011

def split_images(src_dir, dest_dir):
    """
    Split images in the source directory into left and right halves, convert them
    into pdf files, and saves them to the destination directory with title 'imgXXX.pdf'.

    :param src_dir: the source directory path
    :param dest_dir: the destination directory path
    :return: none
    """
    image_num = 1
    for folder in os.listdir(src_dir):
        if folder != '.DS_Store':  # Ignore .DS_Store because it is not a folder
            for file in os.listdir(f'{src_dir}/{folder}'):
                # Ignore duplicated blurry images with 'vignvis' prefix
                if file.endswith('jpg') and not file.startswith('vignvis'):
                    image = Image.open(f'{src_dir}/{folder}/{file}')
                    width, height = image.size
                    image_left = image.crop((0, 0, 0.50 * width, height))
                    image_right = image.crop((0.50 * width, 0, width, height))
                    image_left.save(f'{dest_dir}/image{image_num}.pdf')
                    image_right.save(f'{dest_dir}/image{image_num + 1}.pdf')
                    image_num += 2


def merge_pdfs(src_dir, dest_dir, pdf_cnt):
    """
    Merge a list of pdfs in a directory into a single pdf.

    :param src_dir: the source directory path
    :param dest_dir: the destination directory path
    :param pdf_cnt: the number of pdfs to merge into a single pdf
    :return: none
    """
    pdfs = []
    for pdf in os.listdir(src_dir):
        pdfs.append(f'{src_dir}/{pdf}')
    merger = PdfFileMerger()
    num_pdfs = 0
    for pdf in pdfs:
        if pdf.endswith('pdf'):
            merger.append(pdf)
            num_pdfs += 1
        if num_pdfs % pdf_cnt == 0:
            merger.write(f"{dest_dir}/merged{num_pdfs // pdf_cnt}.pdf")
            merger.close()
            merger = PdfFileMerger()
    if num_pdfs % pdf_cnt != 0:  # Add the remaining pdfs that are left off
        merger.write(f"{dest_dir}/merged{num_pdfs // pdf_cnt + 1}.pdf")
        merger.close()


def remove_borders(filename):
    """
    Removes the (dark) borders of a (light) image.

    :param filename: the image to be cropped
    :return: the cropped image
    """
    img = Image.open(filename)
    img_rgb = img.convert("RGB")
    width, height = img.size
    x1 = 0
    y = 0
    counter = 0
    while x1 < width:
        while y < height:
            r, g, b = img_rgb.getpixel((x1, y))
            if r > 200 and g > 200 and b > 200:
                counter += 1
            y += 1
        if counter > PAGE_SENSITIVITY * height:
            break
        x1 += 1
        y = 0
        counter = 0

    x = 0
    y1 = 0
    counter = 0
    while y1 < height:
        while x < width:
            r, g, b = img_rgb.getpixel((x, y1))
            if r > 200 and g > 200 and b > 200:
                counter += 1
            x += 1
        if counter > PAGE_SENSITIVITY * width:
            break
        y1 += 1
        x = 0
        counter = 0

    x2 = width - 1
    y = height - 1
    counter = 0
    while x2 > 0:
        while y > 0:
            r, g, b = img_rgb.getpixel((x2, y))
            if r > 200 and g > 200 and b > 200:
                counter += 1
            y -= 1
        if counter > PAGE_SENSITIVITY * height:
            break
        x2 -= 1
        y = height - 1
        counter = 0

    x = width - 1
    y2 = height - 1
    counter = 0
    while y2 > 0:
        while x > 0:
            r, g, b = img_rgb.getpixel((x, y2))
            if r > 200 and g > 200 and b > 200:
                counter += 1
            x -= 1
        if counter > PAGE_SENSITIVITY* width:
            break
        y2 -= 1
        x = width - 1
        counter = 0

    cropped_img = img.crop((x1, y1, x2, y2))
    cropped_img.save(f'{filename}_cropped.jpg')


def smart_crop(filename):
    """
    Crops an image to just the text.
    :param filename: the image to be smart cropped
    :return: the smart cropped image
    """
    img = Image.open(filename)
    img_rgb = img.convert("RGB")
    width, height = img.size
    x1 = 20
    y = 0
    counter = 0
    while x1 < width:
        while y < height:
            r, g, b = img_rgb.getpixel((x1, y))
            if r < 100 and g < 100 and b < 100:
                counter += 1
                print(f'{(x1, y)}, {counter}')
            y += 1
        if counter > TEXT_SENSITIVITY * height:
            break
        x1 += 1
        y = 0
        counter = 0

    img = Image.open(filename)
    img_rgb = img.convert("RGB")
    width, height = img.size
    x2 = width - 1
    y = 0
    counter2 = 0
    while x2 > 0:
        while y < height:
            r, g, b = img_rgb.getpixel((x2, y))
            if r < 100 and g < 100 and b < 100:
                counter2 += 1
                print(f'{(x2, y)}, {counter2}')
            y += 1
        if counter2 > TEXT_SENSITIVITY * height:
            break
        x2 -= 1
        y = 0
        counter2 = 0

    cropped_img = img.crop((x1 - 20, 0, x2 + 25, height))
    cropped_img.save(f'{filename}_smart_cropped.jpg')


if __name__ == '__main__':
    # split_images('1972/raw', '1972/split')
    remove_borders("image1.jpg")
    smart_crop('image1.jpg_cropped.jpg')