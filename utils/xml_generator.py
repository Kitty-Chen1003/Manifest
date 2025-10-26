import xml.etree.ElementTree as ET


# xml生成器
class XMLGenerator:
    def __init__(self, root_tag, attrib=None):
        self.root = ET.Element(root_tag, attrib=attrib)

    def add_element(self, tag, text=None, attrib=None):
        if attrib == None:
            attrib= {}
        element = ET.SubElement(self.root, tag, attrib)
        if text:
            element.text = text
        return element

    def add_sub_element(self, parent, tag, text=None, attrib={}):
        element = ET.SubElement(parent, tag, attrib)
        if text:
            element.text = text
        return element

    def write_to_file(self, filename, encoding='utf-8'):
        tree = ET.ElementTree(self.root)
        tree.write(filename, encoding=encoding, xml_declaration=True)

    def get_xml(self):
        return ET.tostring(self.root, encoding='utf-8').decode()

    def add_half_tag_element(self, parent, tag, attrib=None):
        element = ET.Element(tag, attrib)
        parent.append(element)
        return element
