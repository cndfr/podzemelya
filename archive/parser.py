import re
import csv
import json


class bcolors:
    KEYC = '\033[100m'
    ENDC = '\033[0m'


lastLine = 0
parsed = []

with open('archive/pcz.txt', newline='') as source:
    lines = source.readlines()

for id in range(1, 618):
    pattern = ' ' + str(id) + ' '
    nextpattern = ' ' + str(id+1) + ' '
    print(bcolors.KEYC + '#' + str(id) + bcolors.ENDC)
    for line in lines[lastLine:]:
        if pattern in line:
            forward = 0
            if nextpattern in line:
                content = (line[line.index(pattern):line.index(nextpattern)])
            else:
                content = line[line.index(pattern):]
                # print('lastLine: ' + str(lastLine))
                content += '--------------⚔️--------------<br>'
                rest = lines[lastLine + 1:]
                for nextline in rest:
                    forward += 1
                    if nextpattern in nextline:
                        content += nextline[:nextline.index(nextpattern)]
                        break
                    else:
                        content += nextline
            # content.replace('\r\n', '')
            print(content)
            parsed.append(content)
            lastLine = lines.index(line) + forward
            break

# print(parsed)
data = []
with open('archive/base.txt', 'w') as base:
    base.write(f"\n")
    n = 1
    for page in parsed:
        item = str(page).replace('\r\n', '<br>')
        quotes = item.replace('\"', '<q>')
        # text = item
        # item.find(' ')
        # text = item.split(' ')
        text = re.sub(r'^\ \d+\ ', '', quotes)
        # text = text[text.find(' '):]
        paragraph = {
            'id': n,
            'event': 'default',
            'moves': [int(move)
                      for move in re.findall(r'\b\d+\b', text)],

            'pass': [],
            'drops': [],
            'takes': [],
            'text': text,
        }
        n += 1
        line = str(paragraph).replace('\'', '\"')
        base.write(f"{line}\n")

    # data.append(paragraph)

# with open('archive/base.json', 'w', encoding='utf8') as base:
#     json.dump(data, base, ensure_ascii=False)


# with open('archive/base.json', 'w', encoding='utf8') as base:
#     json.dump(parsed, base, ensure_ascii=False)

# with open('archive/base.txt', 'w') as base:
#     base.write(f"{data}")


# for page in parsed:
#     item = str(page).replace('\r\n', '<br>')
#     parsed[page] = item

# with open('base', 'w') as base:
#     json.dump(item, base)

# output_file = open('base', 'w', encoding='utf-8')
# for page in parsed:
#     json.dump(page, output_file)
#     output_file.write("\n")


# with open('/Users/cndfr/Library/Mobile Documents/com~apple~CloudDocs/DEV/Podzemelya/base.csv', 'wb') as base:
#     writer = csv.writer(base)
#     for page in parsed:
#         writer.writerows(page)

while (1 > 0):
    id = input('ID:')

    with open('archive/base.txt', 'r') as book:
        lines = book.readlines()
        paragraph = json.loads(lines[int(id)])
        # obj = json.loads(paragraph)
        # print(lines[int(id)]['id'])
        # print(lines[int(id)]['text'])
        # print(paragraph)
        # print(paragraph[4])
        # json_acceptable_string = paragraph.replace("'", "\"")
        # y = json.loads(paragraph)
        # object = json.loads(paragraph)
        print(f"Page ID: {paragraph['id']}")
        print(f"Event: {paragraph['event']}")
        print(f"Moves: {paragraph['moves']}")
        print(f"Pass: {paragraph['pass']}")
        print(f"Drops: {paragraph['drops']}")
        print(f"Takes: {paragraph['takes']}")
        print(f"Text: {paragraph['text']}")
        # print(obj)

        # js = json.loads(lines)

    # print(bcolors.KEYC + '#' + str(id) + bcolors.ENDC)
    # print(parsed[int(id)])
    # print(' ')
