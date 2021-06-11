from PIL import Image
from PyPDF2 import PdfFileMerger
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
                    image_left = image.crop((0, 0, 0.5 * width, height))
                    image_right = image.crop((0.5 * width, 0, width, height))
                    image_left.save(f'{dest_dir}/image{image_num}.pdf')
                    image_right.save(f'{dest_dir}/image{image_num + 1}.pdf')
                    image_num += 2


def merge_pdfs(src_dir, dest_dir):
    """
    Merge a list of pdfs in a directory into a single pdf.

    :param src_dir: the source directory path
    :param dest_dir: the destination directory path
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
        if num_pdfs % 10 == 0:
            merger.write(f"{dest_dir}/merged{num_pdfs // 10}.pdf")
            merger.close()
            merger = PdfFileMerger()
    if num_pdfs % 10 != 0:  # Add the remaining pdfs that are left off
        merger.write(f"{dest_dir}/merged{num_pdfs // 10 + 1}.pdf")
        merger.close()


if __name__ == '__main__':
    split_images('1957/raw', '1957/split')
    merge_pdfs('1957/split', '1957/merged')
