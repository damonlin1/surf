import sys
import io
import os

# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
from difflib import SequenceMatcher
from tqdm import tqdm
from unidecode import unidecode

arr02 = "L'ADJOINT AU MAIRE OFFICIER DE L'ETAT-CIVIL"
arr03 = "MAIRE DU XII° ARRONDISSEMENT DE PARIS"


def run_test(filename, destination, end_lines):
    read_file = io.open(filename, 'r', encoding='iso-8859-15')

    for line in read_file:
        if len(line) > 1000:
            list = split_long_acts(line, end_lines, True, destination)
    read_file.close()
    return list


def sequence_matcher(string1, string2):
    """
    This function returns the SequenceMatcher.ratio() of two strings.

    :param string1: first string
    :param string2: second string
    :return: double between 0.0 and 1.0
    """
    return SequenceMatcher(None, string1, string2).ratio()


def act_lengths(filename, destination):
    """
    This function reads the given file and then prints the length of each line
    to a separate write file.

    :param filename: file to read
    :param destination: directory of write file
    :return: no return value
    """
    read_file = io.open(filename, 'r', encoding='iso-8859-15')
    write_file = open(destination, 'w')

    for line in read_file:
        print(len(line), file=write_file)
    read_file.close()
    write_file.close()


def average_end_line_length(end_lines):
    """
    Finds the average length of the provided end lines.
    (This allows the algorithm to limit the length of chars
    it needs to look at)

    :param end_lines: list of strings
    :return: integer average
    """
    sum = 0
    num = 0
    for line in end_lines:
        sum += len(line)
        num += 1
    return sum // num


def split_long_acts(record, end_lines, double_check, destination):
    """
    Splits the long acts that the main splitting function finds suspicious.

    :param record: the suspiciously long record
    :param end_lines: the list of end line samples
    :param double_check: boolean if this is a double check
    :return: a list of split acts
    """
    write_file = open(destination, 'a')

    if double_check:
        sensitivity = 0.55
    else:
        sensitivity = 0.75

    split_acts = []
    last_act_end = 0
    length = average_end_line_length(end_lines)
    num_acts = 0

    for i in range((len(record) - length // 5)):  # indexing 5 chars at a time
        for line in end_lines:
            phrase = record[5*i: 5*i + length]
            # print((5*i + len(line)) - last_act_end)
            print(sequence_matcher(unidecode(phrase).lower(), unidecode(line).lower()), file=write_file)
            if sequence_matcher(unidecode(phrase).lower(), unidecode(line).lower()) > sensitivity:
                if (5 * i + length) - last_act_end <= 25:
                    if num_acts != 0:
                        split_acts[num_acts - 1] += record[last_act_end: 5*i + length]
                        last_act_end = 5*i + length
                        break
                if (5 * i + length) - last_act_end < 483:
                    break
                if check_match(unidecode(record[5*i + length: 5*i + length + 36]).lower(), "(suivent les signatures)") > 0.60 \
                        or check_match(unidecode(record[5*i + length: 5*i + length + 15]).lower(), "transcrit") > 0.60:
                    break
                stamp = 0
                if check_match(unidecode(record[5*i + length: 5*i + length + 52]),
                               unidecode("L'ADJOINT AU MAIRE OFFICIER DE L'ETAT-CIVIL")) > 0.60:
                    stamp = 45
                split_acts.append(record[last_act_end: 5*i + length + stamp])
                last_act_end = 5*i + length + stamp
                num_acts += 1
                break
    if len(record[last_act_end:]) > 0:
        if num_acts > 0:
            split_acts[num_acts - 1] += record[last_act_end:]
        else:
            split_acts.append(record[last_act_end:])
    write_file.close()
    return split_acts


def check_match(sentence, end_line):
    """
    This function uses sequence_matcher() to see if the sentence
    matches the end_line, checking the beginning, the end, and the
    entire sentence.

    :param sentence: a string to be checked
    :param end_line: an example end line string
    :return: a double between 0.0 and 1.0
    """
    score = sequence_matcher(sentence, end_line)
    length = int(1.1 * len(end_line))
    if length > len(sentence):
        length = len(sentence) - 1
    if sequence_matcher(sentence[:length], end_line) > score:
        score = sequence_matcher(sentence[:length], end_line)
    if sequence_matcher(sentence[-length:], end_line) > score:
        score = sequence_matcher(sentence[-length:], end_line)
    return score


def load_end_lines(filename):
    """
    Loads a list of example end lines for a specific
    district.

    :param filename: the file of example end lines
    :return: a list of end lines
    """
    read_file = io.open(filename, 'r', encoding='iso-8859-15')
    end_lines = []

    while True:
        line = read_file.readline()
        if not line:
            read_file.close()
            return end_lines
        if line != '\n':
            end_lines.append(line)


def isolate_acts3(filename, destination, end_lines):
    """
    This function isolates acts from a single line of
    text that is produced by AWS Textract.

    :param filename: the file of textracted data
    :param destination: the directory of the file where the results will go
    :param end_lines: the example end lines
    :return: no return value
    """
    read_file = io.open(filename, 'r', encoding='iso-8859-15')
    write_file = open(f'{destination}/T1-Arr-05', 'a')
    acts_per_page_file = open(f'{destination}/T1-Arr-05_acts_per_page', 'a')
    long_file = open(f'{destination}/T1-Arr-05_long', 'a')

    pgraph_start = 0
    last_period = 0
    curr = 0
    read_text = read_file.read()

    num_acts = 0
    acts = []

    for char in read_text:
        if char == '.':
            sentence = read_text[last_period + 1: curr + 1]
            for line in end_lines:
                if check_match(unidecode(sentence).lower(), unidecode(line).lower()) > 0.75 and len(read_text[pgraph_start: curr + 1]) > 483:
                    if check_match(unidecode(read_text[curr: curr + 30]).lower(), "(suivent les signatures)") > 0.75 \
                            or check_match(unidecode(read_text[curr: curr + 12]).lower(), "transcrit") > 0.75:
                        break
                    stamp = 0
                    if check_match(unidecode(read_text[curr: curr + 45]), unidecode("L'ADJOINT AU MAIRE OFFICIER DE L'ETAT-CIVIL")) > 0.75:
                        stamp = 45
                    record = read_text[pgraph_start: curr + 1 + stamp]
                    if len(record) < 552:
                        if num_acts > 0:
                            acts[num_acts - 1] += record
                    elif len(record) > 1100:
                        long_acts = split_long_acts(record, end_lines, False)
                        for act in long_acts:
                            if len(act) > 1100:
                                double_acts = split_long_acts(act, end_lines, True)
                                for double_act in double_acts:
                                    acts.append(double_act)
                                    num_acts += 1
                            else:
                                acts.append(act)
                                num_acts += 1
                    else:
                        acts.append(record)
                        num_acts += 1
                    pgraph_start = curr + 1
                    break
            last_period = curr
        curr += 1
    if acts == 0:
        act_list = split_long_acts(read_text, end_lines, False)
        for act in act_list:
            if len(act) > 1100:
                double_acts = split_long_acts(act, end_lines, True)
                for double_act in double_acts:
                    acts.append(double_act)
                    num_acts += 1
            else:
                acts.append(act)
                num_acts += 1
    elif len(read_text[pgraph_start:]) > 483:
        act_list = split_long_acts(read_text[pgraph_start:], end_lines, False)
        for act in act_list:
            if len(act) > 1100:
                double_acts = split_long_acts(act, end_lines, True)
                for double_act in double_acts:
                    acts.append(double_act)
                    num_acts += 1
            else:
                acts.append(act)
                num_acts += 1
    acts_per_page = filename
    acts_per_page += '\n'
    acts_per_page += f'{num_acts}\n'
    print(acts_per_page, file=acts_per_page_file)

    act_num = 1
    for act in acts:
        length = len(act)
        act += '\n'
        act += filename + f' ({act_num}) | length: {length}\n'
        print(act, file=write_file)

        if length >= 1300:
            print(act, file=long_file)
        act_num += 1

    acts_per_page_file.close()
    read_file.close()
    write_file.close()
    long_file.close()


if __name__ == '__main__':
    end_lines = load_end_lines('Ends/ends for ARR05.txt')
    # for folder in tqdm(os.listdir("Unsplit/T1-Arr05")):
    #     if folder != '.DS_Store':  # Ignore .DS_Store because it is not a folder
    #         for file in tqdm(os.listdir(f'Unsplit/T1-Arr05/{folder}')):
    #             # Ignore duplicated blurry images with 'vignvis' prefix
    #             if file.lower().endswith('txt') and not file.startswith('vignvis'):
    #                 isolate_acts3(f'Unsplit/T1-Arr05/{folder}/{file}', f'Split', end_lines)
    write_file = open("Split/T1-Arr-05/results", 'a')
    list = run_test("Split/T1-Arr-05/T1-Arr-05_long TEST", "Split/T1-Arr-05/scores", end_lines)
    for item in list:
        print(item, file=write_file)

