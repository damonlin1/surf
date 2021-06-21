from PIL import Image
from tqdm import tqdm
import boto3
import os


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
                    image_left = image.crop((0, 0, 0.38 * width, height))
                    image_right = image.crop((0.62 * width, 0, width, height))
                    image_left.save(f'{dest_dir}/image{image_num}.png')
                    image_right.save(f'{dest_dir}/image{image_num + 1}.png')
                    image_num += 2


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


if __name__ == '__main__':
    split_images('1957/raw', '1957/split')
    extract_text('1957/split', '1957/text')
