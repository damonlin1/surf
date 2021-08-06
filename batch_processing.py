from PIL import Image
from tqdm import tqdm
import boto3
import os

PAGE_SENSITIVITY = 0.02
TEXT_SENSITIVITY = 0.03


def extract_text(img_folder, txt_folder):
    """
    Extracts text from images in the image folder and writes into text files of the
    text folder using batch processing with AWS Textract.
    :param img_folder: the folder of images
    :param txt_folder: the folder of text files
    :return: none
    """
    client = boto3.client('textract')

    for img in tqdm(os.listdir(img_folder)):
        if img != '.DS_Store':  # Ignore .DS_Store because it is not an image
            with open(f'{img_folder}/{img}', 'rb') as raw_img:
                temp_img = raw_img.read()
                bytes_img = bytearray(temp_img)

            response = client.detect_document_text(Document={'Bytes': bytes_img})

            with open(f'{txt_folder}/{img[0:len(img) - 4]}.txt', 'w') as txt_file:
                for entry in response['Blocks']:
                    if entry['BlockType'] != 'PAGE':
                        txt_file.write(entry['Text'] + ' ')


def split_images(image):
    """
    Split images in the source directory into left and right halves, convert them
    into pdf files, and saves them to the destination directory with title 'imgXXX.pdf'.

    :param image: the image to be split
    :return: the split images
    """
    width, height = image.size
    image_left = image.crop((0, 0, 0.50 * width, height))
    image_right = image.crop((0.50 * width, 0, width, height))
    return image_left, image_right


def remove_borders(image):
    """
    Removes the (dark) borders of a (light) image.

    :param image: the image to be cropped
    :return: the cropped image
    """
    width, height = image.size
    x1 = 1
    y = 1
    counter = 0
    while x1 < width:
        while y < height:
            r, g, b = image.getpixel((x1, y))
            if r > 100 and g > 100 and b > 100:
                counter += 100
            y += 1000
        if counter > PAGE_SENSITIVITY * height:
            break
        x1 += 40
        y = 0
        counter = 0

    x = 1
    y1 = 1
    counter = 0
    while y1 < height:
        while x < width:
            r, g, b = image.getpixel((x, y1))
            if r > 100 and g > 100 and b > 100:
                counter += 100
            x += 1000
        if counter > PAGE_SENSITIVITY * width:
            break
        y1 += 10
        x = 0
        counter = 0

    x2 = width - 1
    y = height - 1
    counter = 0
    while x2 > 0:
        while y > 0:
            r, g, b = image.getpixel((x2, y))
            if r > 100 and g > 100 and b > 100:
                counter += 100
            y -= 1000
        if counter > PAGE_SENSITIVITY * height:
            break
        x2 -= 40
        y = height - 1
        counter = 0

    x = width - 1
    y2 = height - 1
    counter = 0
    while y2 > 0:
        while x > 0:
            r, g, b = image.getpixel((x, y2))
            if r > 100 and g > 100 and b > 100:
                counter += 100
            x -= 1000
        if counter > PAGE_SENSITIVITY* width:
            break
        y2 -= 10
        x = width - 1
        counter = 0

    cropped_img = image.crop((x1, y1, x2, y2))
    return cropped_img


def smart_crop(image):
    """
    Crops an image to just the text.

    :param image: the image to be smart cropped
    :return: the smart cropped image
    """
    width, height = image.size
    x1 = 31
    y = 1
    counter = 0
    while x1 < width / 3:
        while y < height:
            r, g, b = image.getpixel((x1, y))
            if r < 100 and g < 100 and b < 100:
                counter += 4
            y += 4
        if counter > TEXT_SENSITIVITY * height:
            break
        x1 += 5
        y = 1
        counter = 0

    width, height = image.size
    x2 = width - 31
    y = 1
    counter2 = 0
    while x2 > 2 * width / 3:
        while y < height:
            r, g, b = image.getpixel((x2, y))
            if r < 100 and g < 100 and b < 100:
                counter2 += 4
            y += 4
        if counter2 > TEXT_SENSITIVITY * height:
            break
        x2 -= 5
        y = 0
        counter2 = 0

    cropped_img = image.crop((x1 - 30, 0, x2 + 30, height))
    return cropped_img


def batch_processing(filename, destination):
    img = Image.open(filename)
    img_rgb = img.convert("RGB")
    img_no_borders = remove_borders(img_rgb)
    left_image, right_image = split_images(img_no_borders)
    left_final = smart_crop(left_image)
    right_final = smart_crop(right_image)

    left_final.save(f'{destination}/{filename[9:-4]}.png')
    right_final.save(f'{destination}/{filename[9:-4]}.png')


if __name__ == '__main__':
    for folder in tqdm(os.listdir("Test_Set")):
        if folder != '.DS_Store':  # Ignore .DS_Store because it is not a folder
            os.mkdir(f'Test_Set_edited/{folder}')
            for file in tqdm(os.listdir(f'{"Test_Set"}/{folder}')):
                # Ignore duplicated blurry images with 'vignvis' prefix
                if file.lower().endswith('jpg') and not file.startswith('vignvis'):
                    batch_processing(f'Test_Set/{folder}/{file}', 'Test_Set_edited')
                    os.mkdir()
