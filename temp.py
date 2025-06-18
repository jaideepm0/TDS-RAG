# import numpy as np
#
# data = np.load('./embeddings.npz', allow_pickle=True)
#
# print(data.keys())
#
# print(data['embeddings'].shape)
# print(data['chunks'].shape)
#
# print(data['chunks'][0])

import os
from rich import print

count = 0

for dir, subdirs, files in os.walk('./markdowns'):
    for file in files:
        if file.endswith('.md'):
            count += 1

print(f'Total markdown files: {count}')
