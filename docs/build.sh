#!/usr/bin/env sh

# Run apidoc to automatically set up the API document structure.
# It does not need to be run every time, but this way new files
# in the source directory will be detected automatically.
# 
# DO NOT ADD -f, it will overwrite existing files, which may
# contain custom options.
sphinx-apidoc -Me -o api ../src

# Run the doc builder.
sphinx-build -b html . ../public
