# mjc-broker

## Dependencies

* python2.7
* wxpython 2.8
* pyinstaller 3.x (build only)

## Build instructions

1. Update client-build/file_version_info.txt with correct information (lines 9, 10, 34, 39)

2. Run build.bat

## Version numbering

Version numbers are in the structure: maj.min.rev-hash

Increment version numbers:

* maj: when breaking changes to the communications protocol occur
* min: when features are added with no breaking changes
* rev: when a new release with no feature additions occur (e.g. bug fix)

hash refers to the current git commit hash

## License

Copyright (C) 2016 David Zhong

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

