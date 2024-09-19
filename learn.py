"""learn python"""


f = open(r'D:\24DLend\yolov5\runs\train\exp\results.csv', 'r', encoding='UTF-8')
data_loss = f.readlines()
data_loss = data_loss[1::]
for line in data_loss:
    data = line.split(",")
    print(f"{data}")