set -e
cd ./lambdas
poetry run generate_swagger src/api.py ../swagger.yaml