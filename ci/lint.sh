#!/bin/bash

# Change to the lambdas directory
cd ./lambdas

# Lint the code using black
poetry run black . --check

# Check the exit code of the previous command
if [ $? -eq 0 ]; then
  echo "Linting completed successfully."
else
  echo "Linting failed."
fi
