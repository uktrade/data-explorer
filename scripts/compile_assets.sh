#!/bin/bash

source ./scripts/functions.sh

run "npm run-script build"
run "node -v"
