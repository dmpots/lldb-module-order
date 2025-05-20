#!/bin/bash
set -x
CXX=c++

$CXX -g2 -shared -fPIC -o libfoo.so foo.cc
$CXX -g2 -shared -fPIC -o libbar.so bar.cc
$CXX -g2 main.cc $(pwd)/libfoo.so $(pwd)/libbar.so
