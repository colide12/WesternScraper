import csv
import re
from bs4 import BeautifulSoup
from urllib.request import urlopen
from dateutil.parser import parse
import pickle

def intList2strList(inputList):
    outputList = []
    for p in inputList:
        outputList.append(str(p))
    return outputList

Class1 = [
    8, 19, 71, 127, 442, 504,
    106,118, 401, 427,
    48, 55, 95, 96,
    534, 536, 540, 544, 546, 548, 549, 552, 554, 556, 558, 560, 562, 564, 568, 570,
    520, 521, 522, 523, 524, 525, 526, 527, 528, 530,
    23, 34, 44, 102, 117, 149, 156, 159, 162, 196, 201, 202, 203, 204, 205, 208, 210, 216, 222, 252, 260, 261, 349, 366, 416, 422, 423, 430, 436, 494, 501, 502, 510, 512, 516, 518, 585, 588]

Class2 = [
    178, 333, 340, 342, 343, 358, 367, 370, 375, 379, 385, 455,
    341, 380, 382, 395, 700, 701, 702, 704, 705, 706, 707, 708, 709, 710, 712, 713, 714,
    345, 347,
    360, 365, 369, 711]

Class3 = [
    424, 514,
    128, 600, 601, 602, 604, 606, 607,
    435, 800,
    351, 433, 623]

Class4 = [
    174, 200, 327, 329, 330, 331, 332, 334, 335, 336, 337, 338, 392, 439,
    313, 314, 315, 362, 372, 445,
    73, 324, 356, 374,
    250, 376, 378,
    60, 136, 290, 310, 318, 320, 322, 323, 361, 363, 388, 429,
    257, 326, 438, 505,
    191, 218, 219, 307, 346, 348, 377, 381, 386]

Class5 = [
    65, 82, 83, 125, 141, 142, 144, 173, 209, 221, 225, 226, 234, 241, 242, 264, 271, 407, 408, 409, 414, 425, 451, 493,
    29, 72, 75, 76, 140, 147, 148, 163, 164, 228, 266, 270, 413, 419, 420,
    91, 92, 123, 185, 188, 192, 251, 303, 415, 417, 418, 464, 474, 475, 476, 477,
    352, 353, 355, 359, 396, 399,
    104, 105, 114, 152, 180, 187, 213, 238, 244, 246, 258, 280, 293, 295, 296, 298, 301, 305, 410, 440,
    7, 16, 42, 49, 51, 74, 81, 86, 89, 100, 124, 157, 184, 193, 194, 198, 212, 227, 235, 239, 254, 267, 291, 294, 384, 400, 402, 406, 411, 453, 454, 470, 482, 483, 492, 508]

Class6 = [
    43, 47, 56, 99, 111, 119, 131, 426, 449, 452, 460,
    273, 446, 463, 472, 473,
    2, 12, 24, 26, 28, 36, 38, 57, 66, 68, 69, 79, 87, 112, 139, 223, 450,
    37, 166, 171, 172, 175, 299, 405, 507,
    4, 5, 30, 70, 132, 182, 211, 256, 297, 312,
    110, 122, 126, 165, 237, 373, 431, 432,
    138, 277, 285, 403,
    53, 206, 215, 217, 220, 224, 229, 232, 383,
    1, 14, 15, 27, 33, 40, 52, 54, 59, 62, 63, 84, 101, 108, 109, 116, 134, 135, 137, 150, 160, 168, 169, 177, 181, 186, 190, 199, 231, 236, 245, 248, 249, 269, 276, 278, 279, 281, 283, 289, 292, 300, 368, 404, 412, 428, 434, 441, 462, 503]
ClassSet = [Class1, Class2, Class3, Class4, Class5, Class6]

html = urlopen('http://www.ibiblio.org/patents/classes.html')
source = html.read()
html.close()
soup = BeautifulSoup(source, "lxml")
tables = soup.find_all('li')
USPCNumber = []
for li in tables:
    USPCNumber.append(li.find('a').text.replace('Class: ','').strip())

HJTPatentClassInt = Class1+Class2+Class3+Class4+Class5+Class6
HJTPatentClassStr = intList2strList(HJTPatentClassInt)

chaJipHap = set(USPCNumber) - set(HJTPatentClassStr)
print(len(HJTPatentClassStr))
print(len(USPCNumber))
print(len(chaJipHap))
print(list(chaJipHap))

ClassSetStr = []
for i in ClassSet:
    ClassSetStr.append(intList2strList(i))

augmentedClass = []
augmentedClass.append(ClassSetStr[0] + ['987','532'])
augmentedClass.append(ClassSetStr[1] + ['902','364','371'])
augmentedClass.append(ClassSetStr[2] + ['930','935'])
augmentedClass.append(ClassSetStr[3] + ['354','976','328','437'])
augmentedClass.append(ClassSetStr[4] + ['901','968'])
augmentedClass.append(ClassSetStr[5] + ['D02','D19','D09','D15','D20','D32','D01','D21','D11','D28','D03','D25','D17','D08','D18','D24','D23','D99','D34','D13','D22','D04','D27','D06','D26','D07','D30','D16','D10','D12','D14','D05','D29','984'])

f = open("classificationChart.txt", 'wb')
pickle.dump(augmentedClass, f)
f.close()