#!/usr/bin/env python

import sys
import re
import xml.etree.ElementTree as ET

valid_route_pattern = re.compile('[A-Za-z0-9]{1,3}-[A-Za-z0-9]{1,3}')

def check(file_name):
    tree = ET.parse(file_name)
    root = tree.getroot()

    for relation in root.findall('relation'):
        if is_node_network_route(relation):
            ref = get_tag(relation, 'ref')
            note = get_tag(relation, 'note')
            if note == None and ref == None:
                print('')
                print('Relatie zonder ref of note gevonden:')
                print_primitive(relation)
                continue
            if note != None and not valid_route(note):
                print('')
                print('Relatie met afwijkende note gevonden:')
                print_primitive(relation)
                continue
            if ref != None and not valid_route(ref):
                print('')
                print('Relatie met afwijkende ref gevonden:')
                print_primitive(relation)
                continue
            if ref == note:
                print('')
                print('Relatie met gelijke note en ref gevonden:')
                print_primitive(relation)
                continue
            if ref != note and valid_route(note) and valid_route(ref):
                print('')
                print('Relatie met niet overeenkomende note en ref gevonden:')
                print_primitive(relation)


def convert(file_name, output_name):
    tree = ET.parse(file_name)
    root = tree.getroot()

    for relation in root.findall('relation'):
        if is_node_network_route(relation):
            ref = get_tag(relation, 'ref')
            note = get_tag(relation, 'note')
            if note == None:
                # Niks te doen.
                continue
            if ref == note:
                # Verwijder note; ref is hetzelfde.
                remove_tag(relation, 'note')
                continue
            if ref != None:
                # Ref bestaat al, en wijkt af van note. Niets doen.
                continue
            if valid_route(note):
                # Note wordt ref.
                set_tag(relation, 'ref', note)
                remove_tag(relation, 'note')
                continue

    tree.write(output_name)

def valid_route(text):
    return text != None and valid_route_pattern.match(text) != None

def is_node_network_route(relation):
    return get_tag(relation, 'type') == 'route' and get_tag(relation, 'network:type') == 'node_network'

def print_primitive(primitive):
    print('')
    members = len(primitive.findall('member'))
    print('id:%s (%r members)' % (primitive.get('id'), members))
    for tag in primitive.findall('tag'):
        print('  ' + tag.get('k') + ': ' + tag.get('v'))

def get_tag(primitive, name):
    for tag in primitive.findall('tag'):
        if tag.get('k') == name:
            return tag.get('v')
    return None

def set_tag(primitive, name, value):
    for tag in primitive.findall('tag'):
        if tag.get('k') == name:
            tag.set('v', value)
            return

    tag = ET.SubElement(primitive, 'tag')
    tag.set('k', name)
    tag.set('v', value)


def remove_tag(primitive, name):
    for tag in primitive.findall('tag'):
        if tag.get('k') == name:
            primitive.remove(tag)


def print_usage():
    print('Gebruik: note-to-ref.py check INPUT')
    print('         note-to-ref.py convert INPUT OUTPUT')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print_usage()
    elif sys.argv[1] == 'check':
        check(sys.argv[2])
    elif sys.argv[1] == 'convert':
        if len(sys.argv) < 4:
            print_usage()
        else:
            convert(sys.argv[2], sys.argv[3])
    else:
        print_usage();
