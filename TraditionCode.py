#coding:utf-8
from PIL import  Image
import tesserocr
#解析传统验证码
img = Image.open('code2.jpg')
img = img.convert('L')
threshold = 130
table = []
for i in range(256):
    if i < threshold:
        table.append(0)
    else:
        table.append(1)
img =img.point(table,'1')
print(tesserocr.image_to_text(img))

img.save('c.jpg')
