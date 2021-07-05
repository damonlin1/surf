import sys
import io
import os

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from difflib import SequenceMatcher
from tqdm import tqdm
# import codecs


def cosine_similarity(string1, string2):
    list1 = word_tokenize(string1)
    list2 = word_tokenize(string2)

    sw = stopwords.words('english')
    l1 = []
    l2 = []

    # remove stop words from the string
    set1 = {w for w in list1 if not w in sw}
    set2 = {w for w in list2 if not w in sw}

    rvector = set1.union(set2)
    for w in rvector:
        if w in set1:
            l1.append(1)
        else:
            l1.append(0)
        if w in set2:
            l2.append(1)
        else:
            l2.append(0)
    c = 0

    for i in range(len(rvector)):
        c += l1[i] * l2[i]
    cosine = c / float((sum(l1) * sum(l2)) ** 0.5)

    return cosine


def sequence_matcher(string1, string2):
    return SequenceMatcher(None, string1, string2).ratio()


def load_end_statements(filename):
    read_file = io.open(filename, 'r', encoding='iso-8859-15')
    end_lines = []

    while True:
        line = read_file.readline()
        if not line:
            read_file.close()
            return end_lines
        if line != '\n':
            end_lines.append(line[:-3])



def isolate_acts(filename, destination, end_lines):
    read_file = io.open(filename, 'r', encoding='iso-8859-15')
    write_file = open(f'{destination}/{filename[24:]}', 'w')

    pgraph_start = 0
    last_period = 0
    curr = 0
    read_text = read_file.read()

    for char in read_text:
        if char == '.':
            sentence = read_text[last_period + 1: curr + 1]
            # print(sequence_matcher(sentence, endline))
            if sentence[-5:].lower() == 'civil':
                last_period = curr
            else:
                for line in end_lines:
                    extra = len(sentence) - len(line)
                    if extra > 5:
                        extra -= 5
                    if sequence_matcher(sentence[extra:], line) > 0.60 \
                            or sequence_matcher(sentence[:30], '(Suivent les signatures)') > .75:
                        record = read_text[pgraph_start: curr]
                        record += "\n"
                        record += filename
                        record += "\n\n"
                        print(record, file=write_file)
                        pgraph_start = curr
                        break
                last_period = curr
        curr += 1
    read_file.close()
    write_file.close()


if __name__ == '__main__':
    # for folder in tqdm(os.listdir("T1-Arr02/AD075EC_02D120")):
    #     if folder != '.DS_Store':  # Ignore .DS_Store because it is not a folder
            # os.mkdir(f'results/{folder}')
            os.mkdir(f'results/AD075EC_02D120')
            for file in tqdm(os.listdir('T1-Arr02/AD075EC_02D120')):
                # Ignore duplicated blurry images with 'vignvis' prefix
                if file.lower().endswith('txt') and not file.startswith('vignvis'):
                    isolate_acts(f'T1-Arr02/AD075EC_02D120/{file}', 'results/AD075EC_02D120', load_end_statements('02D120.txt'))
    # isolate_acts('T1-Arr02/AD075EC_02D120/AD075EC_02D120_0002_l.txt', 'results', load_end_statements('02D120.txt'))
