#!/bin/bash
#find $(pwd)/package | wixl-heat -p $(pwd) --component-group CG.Lethal-Manager --var var.DESTDIR > test.wxs
wixl -D SourceDir=$(pwd)/package -D DESTDIR=$(pwd) -v test.wxs

