#!/bin/bash
tmpfile=$(mktemp /tmp/XXXXXXXX.png)
sacad -v quiet -d  "$(mpc status -f '%artist%' |head -n 1 )" "$(mpc status  -f %album% |head -n1)" 600 $tmpfile
if [ -e "$tmpfile" ] ; then
cp $tmpfile "/data/Musik/$(dirname "$(mpc status -f '%file%'|head -n1  )")/cover.png"
fi
rm -f $tmpfile
