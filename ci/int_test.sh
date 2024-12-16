set -e
cd ./lambdas
poetry install

# Run all tests, a subset of tests, or a single test
if [ -z "$1" ]; then
    poetry run pytest ../integration_tests -vvv
elif [ -z "$2" ]; then
    poetry run pytest ../integration_tests/routes/"$1" -vvv
else
    poetry run pytest ../integration_tests/routes/"$1" -k "$2" -vvv
fi
