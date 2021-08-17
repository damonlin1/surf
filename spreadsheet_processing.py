import pandas as pd

sheet = pd.read_excel(r'A-actsV01.xlsx')

columns = pd.DataFrame(sheet, columns=['data', 'source'])

file_fourteen = write_file = open('first_14_words', 'w')
file_other = open('act_minus_first_14_words', 'w')
file_dictionary = open('dictionary', 'w')

dictionary = []

for data, source in columns:
    space = 0
    index = 0
    for char in data:
        if char == ' ':
            space += 1
            if space == 14:
                fourteen = data[:index] + '\n' + source
                print(fourteen, file=file_fourteen)
                print(data[index + 1:] + '\n' + source, file=file_other)

                for word in fourteen.split():
                    if word not in dictionary:
                        dictionary.append(word)
            break
        index += 1

for word in dictionary:
    print(word, file=file_dictionary)

file_dictionary.close()
file_other.close()
file_fourteen.close()