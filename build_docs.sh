#!/bin/bash

rm -r ./docs/*
pdoc --force --html --output-dir ./docs pmtarray
mv ./docs/pmtarray/* ./docs/
rm -r ./docs/pmtarray

echo "Docs built with pdoc3!"