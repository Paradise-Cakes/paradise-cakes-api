set -e
cd ./lambdas
poetry install

# Run all tests or a subset
if [ -z "$1" ]; then
    poetry run pytest ../integration_tests -vvv
else
    poetry run pytest ../integration_tests/routes/"$1" -vvv
fi
