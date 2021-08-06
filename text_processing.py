import sys
import io
import os

# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
from difflib import SequenceMatcher
from tqdm import tqdm
from unidecode import unidecode


def sequence_matcher(string1, string2):
    return SequenceMatcher(None, string1, string2).ratio()


def act_lengths(filename):
    read_file = io.open(filename, 'r', encoding='iso-8859-15')
    write_file = open('lengths', 'w')

    for line in read_file:
        print(len(line), file=write_file)
    read_file.close()
    write_file.close()


def average_line_length(end_lines):
    sum = 0
    num = 0
    for line in end_lines:
        sum += len(line)
        num += 1
    return sum // num


def split_long_acts(record, end_lines):
    split_acts = []
    last_act_end = 0
    length = average_line_length(end_lines)

    for i in range((len(record) - length // 5)):
        for line in end_lines:
            phrase = record[5*i: 5*i + length]
            # print((5*i + len(line)) - last_act_end)
            if sequence_matcher(unidecode(phrase).lower(), unidecode(line).lower()) > 0.75 \
                    and ((5*i + length) - last_act_end) > 500:
                split_acts.append(record[last_act_end: 5*i + length])
                last_act_end = 5*i + length
                break
    return split_acts


def check_match(sentence, end_line):
    score = sequence_matcher(sentence, end_line)
    length = int(1.1 * len(end_line))
    if length > len(sentence):
        length = len(sentence) - 1
    if sequence_matcher(sentence[:length], end_line) > score:
        score = sequence_matcher(sentence[:length], end_line)
    if sequence_matcher(sentence[-length:], end_line) > score:
        score = sequence_matcher(sentence[-length:], end_line)
    return score


def find_average(filename):
    lengths = io.open(filename, 'r', encoding='iso-8859-15')

    lines = 0
    total = 0

    for line in lengths:
        total += int(line)
        lines += 1

    return total / lines


def load_end_statements(filename):
    read_file = io.open(filename, 'r', encoding='iso-8859-15')
    end_lines = []

    while True:
        line = read_file.readline()
        if not line:
            read_file.close()
            return end_lines
        if line != '\n':
            end_lines.append(line)


def isolate_acts(filename, destination, end_lines):
    read_file = io.open(filename, 'r', encoding='iso-8859-15')
    write_file = open(f'{destination}/test-ARR-02', 'a')
    acts_per_page_file = open(f'{destination}/test-02_acts_per_page', 'a')
    long_file = open(f'{destination}/test-ARR-02-long', 'a')
    short_file = open(f'{destination}/test-ARR-02-short', 'a')
    length = open(f'{destination}/test-ARR-02-lengths', 'a')

    pgraph_start = 0
    last_period = 0
    curr = 0
    read_text = read_file.read()

    acts = 0

    for char in read_text:
        if char == '.':
            sentence = read_text[last_period + 1: curr + 1]
            # print(sequence_matcher(sentence, endline))
            for line in end_lines:
                if check_match(unidecode(sentence).lower(), unidecode(line).lower()) > 0.75 and len(read_text[pgraph_start: curr + 1]) > 400:
                    if check_match(read_text[curr: curr + 30].lower(), "(suivent les signatures)") > 0.75 \
                            or check_match(read_text[curr: curr + 12].lower(), "transcrit") > 0.75:
                        break
                    # if check_match(read_text[curr: curr + 10], "L'ADJOINT") > 0.75:
                    #     break
                    record = read_text[pgraph_start: curr + 1]
                    record += "\n"
                    print(len(record), file=length)
                    if len(record) < 500:
                        record += filename
                        record += "\n"
                        print(record, file=short_file)
                    elif len(record) > 1100:
                        act_list = split_long_acts(record, end_lines)
                        for act in act_list:
                            acts += 1
                            act += "\n"
                            act += filename
                            act += f' ({acts}) \n'
                            print(act, file=write_file)
                            print(act, file=long_file)
                    else:
                        acts += 1
                        record += filename
                        record += f' ({acts}) \n'
                        print(record, file=write_file)
                    pgraph_start = curr + 1
                    break
            last_period = curr
        curr += 1
    record2 = filename
    record2 += '\n'
    record2 += f'{acts}'
    if acts == 0:
        act_list = split_long_acts(read_text, end_lines)
        for act in act_list:
            acts += 1
            act += filename
            act += f' ({acts}) \n'
            print(act, file=write_file)
            print(act, file=long_file)
    record2 += '\n\n'
    print(record2, file=acts_per_page_file)
    acts_per_page_file.close()
    read_file.close()
    write_file.close()
    long_file.close()
    length.close()


if __name__ == '__main__':
    end_statements = load_end_statements('Ends/ends for ARR02.txt')
    for folder in tqdm(os.listdir("Unsplit/T1-Arr02")):
        if folder != '.DS_Store':  # Ignore .DS_Store because it is not a folder
            for file in tqdm(os.listdir(f'Unsplit/T1-Arr02/{folder}')):
                # Ignore duplicated blurry images with 'vignvis' prefix
                if file.lower().endswith('txt') and not file.startswith('vignvis'):
                    isolate_acts(f'Unsplit/T1-Arr02/{folder}/{file}', f'Split', end_statements)
    # record = """ A.femsry Nelue Mairie du 4° Art. Le neuf mars mil neuf cent cinquante, huit heures quarante-cing est aeceae, 1 Place du Parvis, René Emile LAMBÉRIOUX, né à Seigy ( Loir-et-Cher) le deux mai mil neuf cent, sans profession, domi- cilié rue Tiquetonne 34, fils de Emile Ferdinand LAMBÉRIOUX, et de Antoinette MARQUET, époux décédés; Epoux de Félicie BETINAS.-Dressé le neuf mars mil neuf cent cinquante, quinze heures, sur la déclaration de Luci en Guiloineau, employé, quarante-un ans, 1 Place du Parvis, qui, lecture faite a signé avec Nous, Jean MOULY, * daire du quatrieme arrondissement de Paris, Chevalier de la Légion d'Honneur, décoré de la Médaille Mili taire, de la Croix de Guerre et de la Médaille de la Résistance Frangaise.-Suivent les signatures). -Trans- crit le vingt-un mars mil neuf cent cinquante, douze heures cinq minutes, par Nous, Jean Jules DELEIEU, ** Officier de la Légion d'Honneur, Groix de Guerre , Médaille de la Résistance, Adjoint au Maire du deuxieme arrondissement de Paris, Julney dairie du 13° Art.- Le vingt-cinq février mil neuf cent cinquante, a vingt-et-une heures quarante, est décé- 16, 19 Boulevard Arago, Caroline Armantine ERNST, domiciliée à Paris, 80 rue Réaumur, née à Rozoy=en-Brie (Seine-et-Marne) le deux avril mil huit cent soixante-seize, sans profession, fille de Hubert Godefroy ERNST et de Armantine YWIS, époux décédés; veuve de Marie Georges RIOTTE. - Dressé le vingt-huit février mil neuf cent cinquante, dix heures trente, sur la déclaration de Henri Javerliat, quarante=neuf ans, employé, 66 Be Boulevard Richard Lenoir, qui, lecture faite a signé avec Nous, Louis CHAPUIS, Adjoint au Maire du treizie- ne arrondissement de Paris.-(Suivent les signatures) -Transcrit le vingt-un mars mil neuf cent cinquante, quatorze heures vingt-cinq minutes, par Nous, Jean Jules DELRIEU, Officier de la Légion d'Honneur, Croix * de Guerre, Médaille de la Résistance, Adjoint au Maire du deuxiene arrondissement de Paris."""
    # acts = split_long_acts(record, end_statements)
    # for act in acts:
    #     print(act)

