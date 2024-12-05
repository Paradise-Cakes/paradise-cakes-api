#!/bin/bash

set -eu
cd ./lambdas
poetry run black "${2:---check}" .
poetry run isort --profile black "${2:---check}" .