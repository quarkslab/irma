#!/bin/sh -e 
#
# Copyright (c) 2013-2018 Quarkslab.
# This file is part of IRMA project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the top-level directory
# of this distribution and at:
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# No part of the project, including this file, may be copied,
# modified, propagated, or distributed except according to the
# terms contained in the LICENSE file.


## Setting defaults
DROOTDIR="$PWD"
DPATTERN="# Copyright (c) 2013-[0-9]\{4\} Quarkslab."
DRSTRING="# Copyright (c) 2013-$(date +%Y) Quarkslab."

usage() {
    printf "\n"
    printf "This scripts updates automatically copyright string on files that match a pattern\n"
    printf "\n"
    printf "usage: $0 [basedir] [pattern] [new string]\n"
    printf "\n"
    printf "       <basedir>    defaults to '.'\n"
    printf "       [pattern]    defaults to 'Copyright (c) 2013-[] Quarkslab.'\n"
    printf "       [new string] defaults to 'Copyright (c) 2013-[] Quarkslab.'\n"
    printf "\n"
    exit 1
}

INFO() {
    printf "[*] $@\n"
}

if [ "$#" -eq 1 ] || [ "$#" -ge 5 ];
then
    usage
fi

ROOTDIR="${1:-$DROOTDIR}"
PATTERN="${2:-$DPATTERN}"
RSTRING="${3:-$DRSTRING}"

INFO "Looking for files matching '$PATTERN' from '$ROOTDIR'.\n    Replacing with '$RSTRING'"

for FILE in $(grep -Rle "$PATTERN" "$ROOTDIR");
do
    INFO "Pattern found in $FILE"
    eval "sed -i 's,$PATTERN,$RSTRING,g' $FILE"
done;
