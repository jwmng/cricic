#!/bin/sh

# Shim for running cricic from any location
# Gets the real location of REPOSITORY before cd'ing to the cricic directory
REPOSITORY=$(realpath $1)

cd $(dirname $(realpath $0))
echo "${@:2}"
python -m cricic ${REPOSITORY} ${@:2}
