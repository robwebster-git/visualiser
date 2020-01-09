#!/usr/bin/env python3

from jinja2 import Environment, FileSystemLoader
import cx_Oracle
import cgi
import cgitb

cgitb.enable(format='text')

class GraphicsArea:

    def __init__(self, width, height, viewBox_x, viewBox_y, viewBox_width, viewBox_height):
        #self.width = f"{width}cm"
        #self.height = f"{height}cm"
        self.width = "480px"
        self.height = "640px"
        self.viewBox_x = viewBox_x
        self.viewBox_y = viewBox_y
        self.viewBox_width = viewBox_width
        self.viewBox_height = viewBox_height
        self.viewBox_custom = f"{viewBox_x} {viewBox_y} {viewBox_width} {viewBox_height}"


class Field:

    def __init__(self, field_id, lowx, lowy, hix, hiy, area, owner, crop_id):

        # Parameters passed in during creation (ie fetched from database)
        self.field_id = field_id
        self.lowx = lowx
        self.lowy = lowy
        self.hix = hix
        self.hiy = hiy
        self.area = f"{area:.2f}"
        self.owner = owner
        self.crop_id = crop_id

        #  Derived Attributes
        self.finds_in_this_field = []

        #  Attributes calculated from object properties
        self.width = hix - lowx
        self.height = hiy - lowy
        self.centroidx = (hix - lowx)/2 + lowx
        self.centroidy = (hiy - lowy)/2 + lowy

        # Default value for fill is 'none'.  This property is dynamically added at runtime
        self.fill = 'none'

    def __repr__(self):
        return f"Field({self.field_id}, {self.lowx}, {self.lowy}, {self.hix}, {self.hiy})"

    def __str__(self):
        return f"Field {self.field_id} - Bottom Left ({self.lowx}, {self.lowy}) Top Right ({self.hix}, {self.hiy})"


class Find:

    def __init__(self, find_id, xcoord, ycoord, find_type, depth, field_notes):
        self.find_id = find_id
        self.xcoord = xcoord
        self.ycoord = ycoord
        self.find_type = find_type
        self.depth = f"{depth:.2f}"
        self.field_notes = field_notes
        self.class_name = 'none'

        # Derived Attributes
        self.in_which_fields = []

        self.fill = get_find_colour(self.find_type)

    def __repr__(self):
        return f"Find({self.find_id}, {self.xcoord}, {self.ycoord})"

    def __str__(self):
        return f"Find {self.find_id} - Coordinates : ({self.xcoord}, {self.ycoord})"


class MyClass:

    def __init__(self, class_type, name, period, use):
        self.class_type = class_type
        self.name = name
        self.period = period
        self.use = use

        self.fill = 'none'

    def __repr__(self):
        return f"Class({self.class_type}, {self.name}, {self.period}, {self.use})"

    def __str__(self):
        return f"Class # {self.class_type} - {self.name}, Period : {self.period}, Use: {self.use})"


class Crop:

    def __init__(self, crop, name, startseason, endseason):
        self.crop = crop
        self.name = name
        self.startseason = startseason
        self.endseason = endseason

        self.fill = 'none'

    def __repr__(self):
        return f"Crop({self.crop}, {self.name}, {self.startseason}, {self.endseason})"

    def __str__(self):
        return f"Crop # {self.crop} - {self.name}, Start of Season: {self.startseason}, End of Season: {self.endseason})"


def get_which_finds(fields, finds):
    for field in fields:
        for find in finds:
            if find.xcoord >= field.lowx and find.xcoord <= field.hix and find.ycoord >= field.lowy and find.ycoord <= field.hiy:
                field.finds_in_this_field.append(find.find_id)


def get_field_colour(field_crop):
    if field_crop == 'TURNIPS':
        return '#A647FF'  # purple
    elif field_crop == 'OIL SEED RAPE':
        return '#F3FC30'  # pale yellow
    elif field_crop == 'STRAWBERRIES':
        return '#FD5959'  # orangey red
    elif field_crop == 'PEAS':
        return '#91F708'  # light green
    elif field_crop == 'POTATOES':
        return '#F9C89A'  # lightish orange
    else:
        return 'none'


def get_find_colour(find_class):
    if find_class == 1:
        return '#9AA8F9'  # light blue
    elif find_class == 2:
        return '#C8C8C8'  # light grey
    elif find_class == 3:
        return '#ABC349'  # flinty green
    elif find_class == 4:
        return '#D1BB00'  # mustard colour
    else:
        return 'none'


def get_crop_name(crops, crop_id):
    for crop in crops:
        if crop.crop == crop_id:
            return crop.name
        else:
            continue


def get_class_name(my_class, find_type):
    for cls in my_class:
        if cls.class_type == find_type:
            return cls.name
        else:
            continue

def get_unique_owners(fields):
    unique = []
    for field in fields:
        if field.owner not in unique:
            unique.append(field.owner)
    return unique

def print_svg(width, height, viewbox):
    return f'<svg width="{width}" height="{height}" viewBox="{viewbox}">'


def getDBdata(table_name, order_column):
    results = []
    conn = cx_Oracle.connect("s0092179/1Annenkov650@geoslearn")
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table_name} ORDER BY {order_column}")

    if table_name == "MY_FIELDS":
        fields_list = []
        for row in c:
            (a, b, c, d, e, f, g, h) = row
            field_name = table_name[:-1] + str(a)
            field_name = Field(a, b, c, d, e, f, g, h)
            fields_list.append(field_name)
            results = fields_list

    elif table_name == "MY_FINDS":
        finds_list = []
        for row in c:
            (a, b, c, d, e, f) = row
            find_name = table_name[:-1] + str(a)
            find_name = Find(a, b, c, d, e, f)
            finds_list.append(find_name)
            results = finds_list

    elif table_name == "MY_CLASS":
        classes_list = []
        for row in c:
            (a, b, c, d) = row
            my_class = MyClass(a, b, c, d)
            classes_list.append(my_class)
            results = classes_list

    elif table_name == "MY_CROPS":
        crops_list = []
        for row in c:
            (a, b, c, d) = row
            my_crop = Crop(a, b, c, d)
            crops_list.append(my_crop)
            results = crops_list
    else:
        print("Table Name not supported...")
    conn.close()
    return results


def assign_field_colours(fields, crops):
    for field in fields:
        for crop in crops:
            if field.crop_id == crop.crop:
                field.fill = get_field_colour(crop.name)
                crop.fill = field.fill
            else:
                continue


def assign_find_colours(finds, classes):
    for find in finds:
        for cls in classes:
            if find.find_type == cls.class_type:
                find.fill = get_find_colour(cls.class_type)
                cls.fill = find.fill
            else:
                continue


def assign_crop_names(fields, crops):
    for field in fields:
        field.crop_name = get_crop_name(crops, field.crop_id)


def assign_class_names(finds, classes):
    for find in finds:
        find.class_name = get_class_name(classes, find.find_type)


def render_html():
    env = Environment(loader=FileSystemLoader('.'))
    temp = env.get_template('index.html')
    print(temp.render(fields=field_objects, finds=find_objects, classes=my_classes, crops=my_crops, g=graphics_area_for_svg, unique_owners=unique_owners))


if __name__ == '__main__':

    print("Content-type: text/html\n")

    my_classes = getDBdata("MY_CLASS", "TYPE")
    my_crops = getDBdata("MY_CROPS", "CROP")
    field_objects = getDBdata("MY_FIELDS", "FIELD_ID")
    find_objects = getDBdata("MY_FINDS", "FIND_ID")

    assign_field_colours(field_objects, my_crops)
    assign_find_colours(find_objects, my_classes)
    assign_crop_names(field_objects, my_crops)
    assign_class_names(find_objects, my_classes)
    unique_owners = get_unique_owners(field_objects)
    get_which_finds(field_objects, find_objects)

    graphics_area_for_svg = GraphicsArea(15, 15, -1, 1, 16, 18)

    render_html()
