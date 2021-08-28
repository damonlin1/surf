from difflib import SequenceMatcher
from PIL import Image, ImageDraw, ImageEnhance, ImageFont
from tqdm import tqdm
import boto3
import csv
import io
import numpy as np
import os
import unidecode


break_phrases = ['est décédé', 'est décédée', 'constate le décès', 'est accouche', 'est accouchee', 'fils de',
                 'fille de', 'Divorcée', 'Divorcé', 'Veuve de', 'Veuf de', 'Célibataire', 'transcrit', 'domiciliée a',
                 'domicilié a', ' ne a ', ' né au ', ' née a ', ' née au ', 'Epoux de ', 'Epouse de ', 'Dressé',
                 'Unsplit']
date_break_phrases = ['janvier', 'fevrier', 'mars', 'avril', 'mai', 'juin', 'juillet', 'aout', 'septembre', 'octobre',
                      'novembre', 'decembre', 'en mil huit', 'en mil neuf']

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


def is_close(num, num_lst):
    """
    Checks if a number is close (within 10) to any of the numbers in the list.

    :param num: the number to check
    :param num_lst: the list to check against
    :return: true if the number is within 10 to any number in the list, false otherwise
    """
    for number in num_lst:
        if abs(num - number) < 10:
            return True
    return False


def parse_data(src_file, dest_file):
    """
    Parses the information of the data into place of birth, date of birth, occupation,
    parent information, place of death, and date of death.

    :param src_file: the text file of the original data
    :param dest_file: the text file of comma delimited parsed data
    :return: none
    """
    # First normalize all phrases by removing accents and lowercase
    processed_break_phrases = []
    for phrase in break_phrases:
        processed_break_phrases.append(unidecode.unidecode(phrase).lower())

    # Open the source and destination files
    with io.open(src_file, 'r', encoding='utf-8') as f:
        with io.open(dest_file, 'w', encoding='utf-8') as g:
            # Clean up messy data from AWS Textract
            line = f.readline().replace('*', '').replace('-', '').replace('=', '')
            while line:
                date_of_birth_marked = False
                # If it is not an empty line, split the act
                if line != '\n':
                    # Keeps track of where to split and the splitting identifier
                    markings = {0: '<<Date of death>>: '}
                    # Keeps track of the places where spaces occur
                    space_idx = []
                    # Identify the act label
                    if line.startswith('Unsplit'):
                        markings[0] = '<<Act label>>: '

                    # Loops through the characters one by one
                    for i in range(len(line) - 13):
                        if line[i] == ' ':
                            space_idx.append(i)

                        # Checks if the words in the act matches any of the break phrases
                        for word in processed_break_phrases:
                            # Normalize the word being compared in the act
                            temp = unidecode.unidecode(line[i:i + len(word)]).lower()
                            if SequenceMatcher(None, temp, word).ratio() > 0.9:
                                # One character shifts may result in the word getting recognized multiple times.
                                # This ensures that once a break signal is added, no more is added nearby.
                                if not is_close(i, list(markings.keys())):
                                    # The following are the list of splitting identifiers
                                    if word in ['est decede', 'est decedee', 'constate le deces', 'est accouche',
                                                'est accouchee']:
                                        markings[i] = '<<Death>>: '
                                    if word in ['fils de', 'fille de']:
                                        markings[i] = '<<Parents>>: '
                                    if word in ['divorcee', 'divorce', 'veuve de', 'veuf de', 'celibataire',
                                                'epoux de ', 'epouse de ']:
                                        markings[i] = '<<Relationship>>: '
                                    if word == 'transcrit':
                                        markings[i] = '<<Transcription>>: '
                                    if word in [' ne a ', ' ne au ', ' nee a ', ' nee au ']:
                                        markings[i] = '<<Birth>>: '
                                    if word == 'dresse':
                                        markings[i] = '<<Misc>>: '

                        # Do the same thing with finding if word match a date
                        for word in date_break_phrases:
                            temp = unidecode.unidecode(line[i:i + len(word)]).lower()
                            if SequenceMatcher(None, temp, word).ratio() > 0.8:
                                if not is_close(i, list(markings.keys())):
                                    try:
                                        idx = space_idx[len(space_idx) - 3]
                                    except IndexError:
                                        pass
                                    if not is_close(idx, list(markings.keys())):
                                        # Second occurrence is date of birth
                                        if 0.1 < i / len(line) < 0.7 and not date_of_birth_marked:
                                            markings[idx] = '<<Date of birth>>: '
                                            date_of_birth_marked = True

                    # Get the index of the places to split
                    markings_list = sorted(list(markings.keys()))
                    print(markings)
                    # Write the data into the destination text file
                    for i in range(len(markings_list) - 1):
                        g.write(unidecode.unidecode(markings[markings_list[i]] +
                                line[markings_list[i]:markings_list[i + 1]] + '\n'))
                    g.write(unidecode.unidecode(markings[markings_list[len(markings_list) - 1]] +
                                                line[markings_list[len(markings_list) - 1]:] + '\n'))

                # Continue with the next act
                line = f.readline().replace('*', '').replace('-', '').replace('=', '')


def create_csv(txt_file, csv_file, keywords):
    """
    Creates a csv file from a text file.

    :param txt_file: the name of the text file to convert into a csv file
    :param csv_file: the name of the csv file
    :param keywords:
    :return: none
    """
    problem_files = []
    with open(csv_file, 'w') as dest:
        info = csv.writer(dest, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        info.writerow(['<<Act label>>'] + keywords)
        with open(txt_file, 'r') as src:
            line = src.readline()
            row = [''] * (len(keywords) + 1)
            while line:
                for j, keyword in enumerate(keywords):
                    if line.startswith(keyword):
                        idx = line.index(':')
                        row[j + 1] = line[idx + 1:]
                if line.startswith('<<Act label>>'):
                    idx = line.index(':')
                    row[0] = line[idx + 1:]
                    if '' in row:
                        problem_files.append(line)
                    info.writerow(row)
                    row = [''] * (len(keywords) + 1)
                line = src.readline()
    print(sorted(problem_files))
    print(len(problem_files))


if __name__ == '__main__':
    split_images('1972', '1972_split')

    for file in os.listdir('1972_split'):
        print(file)
        remove_borders(f'1972_split/{file}')

    # for file in os.listdir('1972_no_border'):
    #     smart_crop(f'1972_no_border/{file}')
