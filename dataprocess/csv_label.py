import os
import csv
from xml.etree import ElementTree as ET

path = ' '  # 数据集路径
label_list = []  # 标签种类


def pretty_xml(element, indent, newline, level=0):  # elemnt为传进来的Elment类，参数indent用于缩进，newline用于换行
    '''
    用于对生成的xml文件进行遍历、换行和缩进，并不是必须的
    '''
    if element:  # 判断element是否有子元素
        if (element.text is None) or element.text.isspace():  # 如果element的text没有内容
            element.text = newline + indent * (level + 1)
        else:
            element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * (level + 1)
            # else:  # 此处两行如果把注释去掉，Element的text也会另起一行
            # element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * level
    temp = list(element)  # 将element转成list
    for subelement in temp:
        if temp.index(subelement) < (len(temp) - 1):  # 如果不是list的最后一个元素，说明下一个行是同级别元素的起始，缩进应一致
            subelement.tail = newline + indent * (level + 1)
        else:  # 如果是list的最后一个元素， 说明下一行是母元素的结束，缩进应该少一个
            subelement.tail = newline + indent * level
        pretty_xml(subelement, indent, newline, level=level + 1)  # 对子元素进行递归操作


def create_xml(objects, anno_dir, name):
    """
    xml的具体格式
    """
    save_xml_path = os.path.join(anno_dir, "%s.xml" % name.split('.')[0])
    root = ET.Element("annotation")
    # root.set("version", "1.0")
    folder = ET.SubElement(root, "folder")
    folder.text = "datasets"
    filename = ET.SubElement(root, "filename")
    filename.text = name
    source = ET.SubElement(root, "source")
    source.text = 'Unknow'
    # owner = ET.SubElement(root, "owner")
    # owner.text = "WPY"
    size = ET.SubElement(root, "size")
    width = ET.SubElement(size, "width")
    width.text = str(objects[1])
    height = ET.SubElement(size, "height")
    height.text = str(objects[2])
    depth = ET.SubElement(size, "depth")
    depth.text = "3"
    segmented = ET.SubElement(root, "segmented")
    segmented.text = "0"

    object = ET.SubElement(root, "object")
    name = ET.SubElement(object, "name")  # number
    id = objects[7]
    name.text = str(label_list[int(id)])
    # meaning = ET.SubElement(object, "meaning")  # name
    # meaning.text = inf_value[0]
    pose = ET.SubElement(object, "pose")
    pose.text = "Unspecified"
    truncated = ET.SubElement(object, "truncated")
    truncated.text = "0"
    difficult = ET.SubElement(object, "difficult")
    difficult.text = "0"
    bndbox = ET.SubElement(object, "bndbox")
    xmin = ET.SubElement(bndbox, "xmin")
    xmin.text = str(objects[3])
    ymin = ET.SubElement(bndbox, "ymin")
    ymin.text = str(objects[4])
    xmax = ET.SubElement(bndbox, "xmax")
    xmax.text = str(objects[5])
    ymax = ET.SubElement(bndbox, "ymax")
    ymax.text = str(objects[6])
    tree = ET.ElementTree(root)
    pretty_xml(root, '  ', '\n')
    tree.write(save_xml_path)


def csv_xml(csv_dir, anno_dir):
    if not os.path.exists(anno_dir):
        os.mkdir(anno_dir)
    with open(csv_dir, 'r') as f:
        reader = csv.reader(f)
        labels = list(reader)
        for label in labels[1:]:
            create_xml(label, anno_dir, name=label[0])
            print(label[0].split('.')[0] + ".xml" + 'is finish')


def convert(size, box):
    """
    对宽高、坐标进行转化
    """
    dw = 1.0 / size[0]
    dh = 1.0 / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)


def xml_txt(anno_dir, label_dir):
    if not os.path.exists(label_dir):
        os.mkdir(label_dir)
    for i in os.listdir(anno_dir):
        xml = open(os.path.join(anno_dir, i))
        txt = open(os.path.join(label_dir, i.split('.')[0] + '.txt'), 'w')
        xml_text = xml.read()
        root = ET.fromstring(xml_text)  # 将字符串转化为Element对象
        xml.close()
        size = root.find('size')
        w = int(size.find('width').text)
        h = int(size.find('height').text)
        for obj in root.iter('object'):
            cls = obj.find('name').text
            b = label_list[5]
            if cls not in label_list:
                print(cls)
                continue
            cls_id = label_list.index(cls)
            xmlbox = obj.find('bndbox')
            box = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text),
                   float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
            bbox = convert((w, h), box)
            txt.write(str(cls_id) + " " + " ".join([str(a) for a in bbox]) + '\n')


if __name__ == '__main__':
    csv_dir = os.path.join(path, "annotations.csv")
    img_dir = os.path.join(path, "JPEGImages")
    anno_dir = os.path.join(path, "Annotations")
    label_dir = os.path.join(path, "labels")
    csv_xml(csv_dir=csv_dir, anno_dir=anno_dir)
    xml_txt(anno_dir, label_dir)