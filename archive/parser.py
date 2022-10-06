
import csv


class bcolors:
    KEYC = '\033[100m'
    ENDC = '\033[0m'


lastLine = 0
parsed = [0]

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

with open('archive/base.txt', 'w') as base:
    for page in parsed:
        item = str(page).replace('\r\n', 'newline')
        base.write(f"{item}\n")


# with open('/Users/cndfr/Library/Mobile Documents/com~apple~CloudDocs/DEV/Podzemelya/base.csv', 'wb') as base:
#     writer = csv.writer(base)
#     for page in parsed:
#         writer.writerows(page)

while (1 > 0):
    id = input("ID:")
    print(bcolors.KEYC + '#' + str(id) + bcolors.ENDC)
    print(parsed[int(id)])
    print(' ')
