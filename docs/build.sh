#!/usr/bin/env sh

# Run apidoc to automatically set up the API document structure.
# It does not need to be run every time, but this way new files
# in the source directory will be detected automatically.
# 
# DO NOT ADD -f, it will overwrite existing files, which may
# contain custom options.
sphinx-apidoc -Me -o odyssey ../src/odyssey/

# Run the doc builder.
rm -rf ../public/*
sphinx-build -j auto -b html . ../public
