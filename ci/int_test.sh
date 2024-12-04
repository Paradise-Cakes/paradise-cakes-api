set -e
cd ./lambdas
poetry install
poetry run pytest ../integration_tests -vvv
