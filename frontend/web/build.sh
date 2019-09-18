#!/usr/bin/env bash

ENV="production"

while getopts e: option
do
    case "${option}" in
        e) ENV=${OPTARG};;
    esac
done

NODE_ENV=${ENV} npm install
npm run build
