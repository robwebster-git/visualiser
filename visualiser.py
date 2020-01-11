#!/usr/bin/env python3

from jinja2 import Environment, FileSystemLoader
import cx_Oracle
import cgi
import cgitb

cgitb.enable(format='text')

class GraphicsArea:

    # Defines an area for SVG graphics to be rendered on the website

    def __init__(self, width, height, viewBox_x, viewBox_y, viewBox_width, viewBox_height):

        # Parameters passed in during creation
        self.width = f"{width}px"                #  width of SVG element on page
        self.height = f"{height}px"              #  height of SVG element on page
        self.viewBox_x = viewBox_x               #  viewBox min x
        self.viewBox_y = viewBox_y               #  viewBox min y
        self.viewBox_width = viewBox_width       #  viewBox width
        self.viewBox_height = viewBox_height     #  viewBox height

        #  string representation of the whole viewBox:
        self.viewBox_custom = f"{viewBox_x} {viewBox_y} {viewBox_width} {viewBox_height}"


class Field:

    #  Field Object Creator

    def __init__(self, field_id, lowx, lowy, hix, hiy, area, owner, crop_id):

        # Parameters passed in during creation (ie fetched from database)
        self.field_id = field_id        #  a number uniquely identifying the field
        self.lowx = lowx                #  x-coordinate of lower left corner
        self.lowy = lowy                #  y-coordinate of lower left corner
        self.hix = hix                  #  x-coordinate of upper right corner
        self.hiy = hiy                  #  y-coordinate of upper right corner
        self.area = f"{area:.2f}"       #  area, formatted to 2 decimal places
        self.owner = owner              #  name of the farmer who owns the field
        self.crop_id = crop_id          # a number identifying the crop in the field

        #  Derived Attributes (populated at runtime)
        self.finds_in_this_field = []   # a list containing the finds found in this field

        #  Attributes calculated from object properties
        self.width = hix - lowx                     #  field width (in map units)
        self.height = hiy - lowy                    #  field height
        self.centroidx = (hix - lowx)/2 + lowx      #  field centroid x coordinate
        self.centroidy = (hiy - lowy)/2 + lowy      #  field centroid y coordinate

        # Default value for fill is 'none'.  This property is dynamically added at runtime
        self.fill = 'none'

    #  User & coder friendly representations of Field objects
    def __repr__(self):
        return f"Field({self.field_id}, {self.lowx}, {self.lowy}, {self.hix}, {self.hiy})"

    def __str__(self):
        return f"Field {self.field_id} - Bottom Left({self.lowx},{self.lowy}) Top Right({self.hix},{self.hiy})"


class Find:

    #  Find Object Creator

    def __init__(self, find_id, xcoord, ycoord, find_type, depth, field_notes):
        self.find_id = find_id          #  a number uniquely identifying the find
        self.xcoord = xcoord            #  x coordinate of find location
        self.ycoord = ycoord            #  y coordinate of find location
        self.find_type = find_type      #  a number identifying the find type (class)
        self.depth = f"{depth:.2f}"     #  the depth of the find, formatted to 2 decimal places
        self.field_notes = field_notes  #  a string field with field notes
        self.class_name = 'none'        #  holds the text name of the crop populated at runtime

        # Derived Attributes

        #  a list of which field(s) the find is found in
        #  (it can be more than 1 field if on the border between fields!)
        self.in_which_fields = []       #  populated at runtime

        self.fill = get_find_colour(self.find_type)  #  applies a colour based on the find type

    #  User & coder friendly representations of Find objects
    def __repr__(self):
        return f"Find({self.find_id}, {self.xcoord}, {self.ycoord})"

    def __str__(self):
        return f"Find {self.find_id} - Coordinates : ({self.xcoord}, {self.ycoord})"


class MyClass:

    #  MyClass Object Creator

    def __init__(self, class_type, name, period, use):
        self.class_type = class_type        #  a number identifying the class type
        self.name = name                    #  a string with the class name
        self.period = period                #  a string with the period of the class
        self.use = use                      #  a string with the use of the class

        self.fill = 'none'                  #  the colour of a particular class, populated at runtime

    #  User & coder friendly representations of MyClass objects
    def __repr__(self):
        return f"Class({self.class_type}, {self.name}, {self.period}, {self.use})"

    def __str__(self):
        return f"Class # {self.class_type} - {self.name}, Period : {self.period}, Use: {self.use})"


class Crop:

    #  Crop Object Creator

    def __init__(self, crop, name, startseason, endseason):
        self.crop = crop                    #  a number identifying the crop type
        self.name = name                    #  a string identifying the crop name
        self.startseason = startseason      #  the start of the growing season
        self.endseason = endseason          #  the end of the growing season

        self.fill = 'none'                  #  the colour assigned to each crop type, populated at runtime

    #  User & coder friendly representations of Crop objects
    def __repr__(self):
        return f"Crop({self.crop}, {self.name}, {self.startseason}, {self.endseason})"

    def __str__(self):
        return f"Crop # {self.crop} - {self.name}, Start of Season: {self.startseason}, End of Season: {self.endseason})"


def getDBdata(table_name, order_column):
    #  Accesses the Oracle database and creates Find, Field, Crop & MyClass
    #  objects with which to create the website visualiser tools
    results = []
    with open('../../../details.txt', 'r') as f:
        pwd = f.readline().strip()
    try:
        conn = cx_Oracle.connect(f"s0092179/{pwd}@geoslearn")
        c = conn.cursor()
        c.execute(f"SELECT * FROM {table_name} ORDER BY {order_column}")
    except:
        print("Failed to connect to Database Server...")

    if table_name == "MY_FIELDS":
        fields_list = []                                #  initialise an empty list
        for row in c:
            (a, b, c, d, e, f, g, h) = row              # pack the results of the query into a tuple
            field_name = table_name[:-1] + str(a)
            field_name = Field(a, b, c, d, e, f, g, h)  # create a new Field object for each row in the table
            fields_list.append(field_name)              # add the newly created field to the "fields_list" list
            results = fields_list                       # return the list of Field objects

    #  The following elif statements handle creation of other objects from the
    #  different tables.  I will not comment these further as the process is the same as for Field ojects
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
    else:                                             #  if no table name matches are made, go to the else...
        print("Table Name not supported...")
    conn.close()                                      #  close the connection to the Oracle server
    return results


def get_which_finds(fields, finds):
    #  loops through fields and finds, and identifies which finds fall within which field,
    #  and also which fields a particular find falls in (could be more than one if on border...)
    #  The program appends any items fulfilling the basic spatial criteria to the relevant field and find objects attribute lists
    for field in fields:
        for find in finds:
            if find.xcoord >= field.lowx and find.xcoord <= field.hix and find.ycoord >= field.lowy and find.ycoord <= field.hiy:
                field.finds_in_this_field.append(find.find_id)
                find.in_which_fields.append(field.field_id)


def get_field_colour(field_crop):
    #  takes a crop name and returns the correct colour for rendering to the web
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
    #  takes a class name and returns the correct colour for rendering to the web
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
    #  takes a crop id number, and returns a string of the actual crop name
    for crop in crops:
        if crop.crop == crop_id:
            return crop.name
        else:
            continue


def get_class_name(my_class, find_type):
    #  takes a find type, and returns a string of its class name
    for cls in my_class:
        if cls.class_type == find_type:
            return cls.name
        else:
            continue

def get_unique_owners(fields):
    #  simply takes the list of all owners and returns a list of just the unique values
    #  which is used for displaying dropdown menus in the website with no duplicate values
    unique = []
    for field in fields:
        if field.owner not in unique:
            unique.append(field.owner)
    return unique

def get_max_find_coordinates(finds):
    #  returns a list of the maximum x and y co-ordinates for any find
    #  this is used for rendering the co-ordinate options in the dropdown menus
    #  to make sure that the values are sensible and go high enough but not any further than needed
    max = [0,0]
    for find in finds:
        if find.xcoord > max[0]:
            max[0] = find.xcoord
        if find.ycoord > max[1]:
            max[1] = find.ycoord

    return max


def print_svg(width, height, viewbox):
    #  if required, can return a string of the basic SVG tag
    return f'<svg width="{width}" height="{height}" viewBox="{viewbox}">'


def assign_field_colours(fields, crops):
    #  takes a lists of fields and crops, and populates the fill colour attributes
    #  by matching crop id from field objects with crop from crop objects
    #  This results in all fields with a particular crop having the same colour,
    #  and all crop name cells in the tables having the same colour.
    for field in fields:
        for crop in crops:
            if field.crop_id == crop.crop:
                field.fill = get_field_colour(crop.name)
                crop.fill = field.fill
            else:
                continue


def assign_find_colours(finds, classes):
    #  takes a lists of finds and classes, and populates the fill colour attributes
    #  by matching find type from find objects with class_type from class objects
    #  This results in all finds with a particular class having the same colour,
    #  and all class name cells in the tables having a matching colour.
    for find in finds:
        for cls in classes:
            if find.find_type == cls.class_type:
                find.fill = get_find_colour(cls.class_type)
                cls.fill = find.fill
            else:
                continue


def assign_crop_names(fields, crops):
    #  populates the crop_name attribute for each field by linking the crop id to the list of crop objects
    for field in fields:
        field.crop_name = get_crop_name(crops, field.crop_id)


def assign_class_names(finds, classes):
    #  populates the class_name attribute of each find by linking the find_type to the list of MyClass objects
    for find in finds:
        find.class_name = get_class_name(classes, find.find_type)


def render_html():
    #  Uses Jinja2 to render an html template and passing in a long list of objects and variables from python to the html page
    env = Environment(loader=FileSystemLoader('.'))
    temp = env.get_template('index.html')
    print(temp.render(fields=field_objects, finds=find_objects, classes=my_classes, crops=my_crops, g=graphics_area_for_svg, unique_owners=unique_owners, max_find_coords=max_find_coords))


if __name__ == '__main__':

    print("Content-type: text/html\n")      #  Ensures that the webpage is rendered correctly using HTML code

    #  Create new lists of objects for each of the main types of interest
    my_classes = getDBdata("MY_CLASS", "TYPE")
    my_crops = getDBdata("MY_CROPS", "CROP")
    field_objects = getDBdata("MY_FIELDS", "FIELD_ID")
    find_objects = getDBdata("MY_FINDS", "FIND_ID")

    #  run the required functions to complete the population of the important fields
    #  in each of the objects by cross referencing between object attributes
    assign_field_colours(field_objects, my_crops)
    assign_find_colours(find_objects, my_classes)
    assign_crop_names(field_objects, my_crops)
    assign_class_names(find_objects, my_classes)
    unique_owners = get_unique_owners(field_objects)
    get_which_finds(field_objects, find_objects)
    max_find_coords = get_max_find_coordinates(find_objects)

    #  Define a new GraphicsArea object which contains the necessary attributes for the SVG rendering on the website
    #  (SVG container width in pixels, SVG conatiner height in pixels, viewBox min x, ViewBox min y, viewBox width, viewBox height)
    graphics_area_for_svg = GraphicsArea(420, 530, -1, 1, 16, 18)

    #  render the html template to the browser
    render_html()
