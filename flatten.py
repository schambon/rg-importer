import os
import sys
from os.path import join, isfile
import shutil
import re

if len(sys.argv) < 3:
    raise ValueError("Usage: python flatten.py <source> <output>")

source = sys.argv[1]
dest = sys.argv[2]

for directory in [join(source, d) for d in os.listdir(source) if not isfile(join(source, d))]:
    for file in [join(directory, f) for f in os.listdir(directory) if
                    isfile(join(directory, f)) and
                    re.search(r'^[0-9]{8}_RG_[0-9a-f\-]+.html?$', f) is not None]:
        shutil.copy(file, dest)
