#!/usr/bin/python

import sys, markdown

save = False
for arg in sys.argv:
    if arg == '--save':
        save = True

with open('Contributors', 'r') as f:
    converted = markdown.markdown(f.read())

if save:
    with open('Contributors.html', 'w') as f:
        f.write(converted)
else:
    print(converted)
