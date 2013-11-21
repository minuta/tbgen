
from xml.etree.ElementTree import ElementTree, Element, SubElement, Comment, tostring
from xml.dom import minidom

def pretty_format(e):
    """Return a pretty-formated XML for the Element e.
    """
    rough_string = tostring(e, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ")



def create_rule(rid):
    rule = SubElement(root, 'rule')
    rule.set('id', rid)
    return rule

def create_packet(parent, pid, sa, da, sp, dp, pr, ac, ma):
    packet = SubElement(parent, 'packet')
    packet.set('id', pid)
    src_addr = SubElement(packet, 'src_addr')
    dst_addr = SubElement(packet, 'dst_addr')
    src_port = SubElement(packet, 'src_port')
    dst_port = SubElement(packet, 'dst_port')
    protocol = SubElement(packet, 'protocol')
    action = SubElement(packet, 'action')
    match = SubElement(packet, 'match')

    src_addr.text = sa
    dst_addr.text = da
    src_port.text = sp
    dst_port.text = dp
    protocol.text = pr
    action.text = ac
    match.text = ma


# ------------------------ MAIN ---------------------------------
root = Element('tests')
r1 = create_rule('r1')
r2 = create_rule('r2')

create_packet(r1, '0', '100000', '200000', '1', '2', '15', 'PASS', 'TRUE')


# print tostring(root)

print pretty_format(root)

# wrap it in an ElementTree instance, and save as XML
tree = ElementTree(root)
tree.write("test.xml")
print "XML file is written...\n"
