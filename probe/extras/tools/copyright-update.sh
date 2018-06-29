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



EXE="$0"

usage() {
    >&2 cat <<USAGE
This script updates copyright strings in the IRMA project.

usage: $EXE [DIR] [-y YEAR] [-v]
usage: $EXE [-h]

    DIR
        Directory of the project. Defaults to '.'
    -y, --year YEAR
        End year of the copyright. Defaults to currentt year.
    -h, --help
        Print this help
    -v, --verbose
        Be verbose
USAGE
    exit 1
}


parse() {
    DIR="."
    YEAR="$(date +%Y)"

    while [[ $# > 0 ]]; do
        case $1 in
            -y|--year) YEAR="$2"; shift 2;;
            -h|--help) usage;;
            -v|--verbose) VERBOSE=1; shift;;
            *) DIR="$1"; shift;;
        esac
    done
}

parse "$@"

MATCHPATTERN="\(Copyright (c) \)\?2013-[0-9]\{4\},\? Quarkslab"

find "$DIR" -type f ${VERBOSE:+-print} -exec \
    sed -i -e "/${MATCHPATTERN}/ s/2013-[0-9]\{4\}/2013-$YEAR/g" {} +


[[ "${VERBOSE}" != "" ]] && cat <<FOOTER
Copyrights updated
WARNING: documentation probably need to be regenerated.
FOOTER
