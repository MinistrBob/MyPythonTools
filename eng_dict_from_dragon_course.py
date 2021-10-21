import docx2txt
import re
import os
from collections import OrderedDict

dictionary = {}
directory = r"d:\YandexDisk\TEMP\АнглийскийШГ"

# for file in os.listdir(directory):
#     if file.endswith(".docx"):
#         filepath = os.path.join(directory, file)
#         print("The Path is: " + str(filepath))
#
# exit()

for file in os.listdir(directory):
    if file.endswith(".docx"):
        filepath = os.path.join(directory, file)
        # print("The Path is: " + str(filepath))

        # Passing docx file to process function
        text = docx2txt.process(filepath)

        lines = text.splitlines()

        for line in lines:
            # print(line)
            result = re.match("^.+ – .+$", line)
            if result:
                # print(result.group(0))
                try:
                    rus, eng = result.group(0).split(" – ")
                except ValueError:
                    pass
                # if eng in dictionary:
                #     pass
                # else:
                #     dictionary[eng] = rus
                if rus in dictionary:
                    pass
                else:
                    dictionary[rus] = eng

# print(dictionary)
od = OrderedDict(sorted(dictionary.items()))
# print(od)
for k, v in od.items():
    print(f"{k}\t{v}")

# Saving content inside docx file into output.txt file
# with open(r"c:\!SAVE\ENG\output.txt", "w", encoding="utf-8") as text_file:
#	print(text, file=text_file)
