import json

import yaml

from src.api import app


def main():
    api = app.openapi()
    with open("../swagger.yaml", "w") as f:
        yaml.dump(json.loads(json.dumps(api)), f, sort_keys=False)


if __name__ == "__main__":
    main()
