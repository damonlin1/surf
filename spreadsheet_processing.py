import pandas as pd
import openpyxl

sheet = pd.read_excel(r'A-actsV01.xlsx')
table = pd.DataFrame(sheet, columns=['data', 'source'])

file_fourteen = write_file = open('first_14_words', 'w')
file_other = open('act_minus_first_14_words', 'w')
file_dictionary = open('dictionary', 'w')

dictionary = []

# print(columns.iloc[0, 1])
# 27083, 2
rows, _ = table.shape
acts = 0
sources = 1
for row_index in range(rows):
    act = table.iloc[row_index, acts]

    space = 0
    curr = 0
    for char in act:
        if char == ' ':
            space += 1
            if space == 14:
                source = table.iloc[row_index, sources]
                fourteen = act[:curr]
                print(fourteen + '\n' + source + '\n', file=file_fourteen)
                print(act[curr + 1:] + '\n' + source + '\n', file=file_other)

                for word in fourteen.split():
                    if word not in dictionary:
                        dictionary.append(word)
                break
        curr += 1

for word in dictionary:
    print(word, file=file_dictionary)

file_dictionary.close()
file_other.close()
file_fourteen.close()