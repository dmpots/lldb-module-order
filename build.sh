#!/bin/bash
set -x -e
CXX=c++

$CXX -g2 -shared -fPIC -o libfoo.so foo.cc
$CXX -g2 -shared -fPIC -o libbar.so bar.cc
$CXX -g2 -shared -fPIC -o libbuz.so buz.cc $(pwd)/libbar.so
#$CXX -g2 main.cc $(pwd)/libfoo.so $(pwd)/libbar.so $(pwd)/libbuz.so
$CXX -g2 main.cc $(pwd)/libfoo.so $(pwd)/libbar.so $(pwd)/libbuz.so
