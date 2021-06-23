from PIL import Image
from tqdm import tqdm
import boto3
import os

PAGE_SENSITIVITY = 0.30
TEXT_SENSITIVITY = 0.011


def split_images(src_dir, dest_dir):
    """
    Split images in the source directory into left and right halves, convert them
    into pdf files, and saves them to the destination directory.

    :param src_dir: the source directory path
    :param dest_dir: the destination directory path
    :return: none
    """
    for folder in tqdm(os.listdir(src_dir)):
        if folder != '.DS_Store':  # Ignore .DS_Store because it is not a folder
            for file in os.listdir(f'{src_dir}/{folder}'):
                # Ignore duplicated blurry images with 'vignvis' prefix
                if file.lower().endswith('jpg') and not file.startswith('vignvis'):
                    image = Image.open(f'{src_dir}/{folder}/{file}')
                    width, height = image.size
                    image_left = image.crop((0, 0, 0.50 * width, height))
                    image_right = image.crop((0.50 * width, 0, width, height))
                    image_left.save(f'{dest_dir}/{folder}/{file[0:len(file) - 4]}_l.png')
                    image_right.save(f'{dest_dir}/{folder}/{file[0:len(file) - 4]}_r.png')


def extract_text(img_folder, txt_folder):
    """
    Extracts text from images in the image folder and writes into text files of the
    text folder using batch processing with AWS Textract.

    :param img_folder: the folder of images
    :param txt_folder: the folder of text files
    :return: none
    """
    client = boto3.client('textract')

    for folder in tqdm(os.listdir(img_folder)):
        if folder != '.DS_Store':  # Ignore .DS_Store because it is not a folder
            for img in os.listdir(f'{img_folder}/{folder}'):
                if img != '.DS_Store':  # Ignore .DS_Store because it is not an image
                    # Don't process images that have already been processed
                    if img not in os.listdir(f'{txt_folder}/{folder}'):
                        with open(f'{img_folder}/{folder}/{img}', 'rb') as raw_img:
                            temp_img = raw_img.read()
                            bytes_img = bytearray(temp_img)

                        response = client.detect_document_text(Document={'Bytes': bytes_img})

                        with open(f'{txt_folder}/{folder}/{img[:-4]}.txt', 'w') as txt_file:
                            for entry in response['Blocks']:
                                if entry['BlockType'] != 'PAGE':
                                    txt_file.write(entry['Text'] + ' ')


def make_folders(folder_lst):
    """
    Makes a list of folders.
    :param folder_lst: a list of folders to make
    :return: none
    """
    for folder in folder_lst:
        try:
            os.mkdir(folder)
        except FileExistsError:
            pass


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
    cropped_img.save(f'1972_no_border/{filename}_cropped.png')


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
            y += 1
        if counter2 > TEXT_SENSITIVITY * height:
            break
        x2 -= 1
        y = 0
        counter2 = 0

    cropped_img = img.crop((x1 - 20, 0, x2 + 25, height))
    cropped_img.save(f'1972_edited/{filename}_smart_cropped.png')


if __name__ == '__main__':
    split_images('1972', '1972_split')

    for file in os.listdir('1972_split'):
        print(file)
        remove_borders(f'1972_split/{file}')

    # for file in os.listdir('1972_no_border'):
    #     smart_crop(f'1972_no_border/{file}')
