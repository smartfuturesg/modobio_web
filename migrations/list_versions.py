#!/usr/bin/env python
import math
import pathlib

from dataclasses import dataclass

@dataclass
class Node():
    """ Linked list node. """
    next: object = None
    hash: str = ''
    file: str = ''

    def __repr__(self):
        return f'Node {self.hash}'

    def __len__(self):
        """ Length of linked list, starting from current node. """
        n = 0
        node = self
        while node is not None:
            n += 1
            node = node.next
        return n

    def __str__(self):
        """ Returns linked list as string, starting from current node. """
        if len(self) == 0:
            pad = 2
        else:
            pad = math.ceil(math.log10(len(self))) + 2
        n = 1
        node = self
        out = []
        while node:
            out.append(f'{n:<{pad}}{node.file}')
            n += 1
            node = node.next
        return '\n'.join(out)

versions_dir = pathlib.Path(__file__).parent / 'versions'
paths = versions_dir.glob('*.py')

nodes = {}
nodelist = Node()

for path in paths:
    current_hash = path.name.split('_')[0]

    previous_hash = None
    with open(path, mode='rt') as fh:
        for line in fh:
            if line.startswith('down_revision'):
                previous_hash = line.split('=')[1].strip().strip("'")
                break

    if not previous_hash:
        print(f'Warning: script {path.name} does not have "down_revision" defined.')
        continue
    elif previous_hash == 'None':
        if nodelist.hash:
            print('Warning: found more than one starting point.')
            print(f'Both {nodelist.file} and {path.name} have "down_revision = None"')
            continue

        nodelist.hash = current_hash
        nodelist.file = path.name
    elif previous_hash in nodes:
        prev = nodes[previous_hash]
        print(f'Warning: scripts {path.name} and {prev.file} both '
              f'claim to upgrade {previous_hash}. Branch point?')
        continue
    else:
        nodes[previous_hash] = Node(
            next=None,
            hash=current_hash,
            file=path.name
        )

node = nodelist
while node.hash in nodes:
    node.next = nodes.pop(node.hash)
    node = node.next

print(nodelist)

if nodes:
    print()
    print('The following files are not part of the upgrade chain:')
    for node in nodes.values():
        print(f'   {node.file}')
