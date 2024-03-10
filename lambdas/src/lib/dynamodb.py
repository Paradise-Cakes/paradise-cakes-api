from boto3.session import Session

_session = Session()


class DynamoConnection:
    def __init__(self, region_name, endpoint_url, table_name):
        self.table = _session.resource(
            "dynamodb", region_name=region_name, endpoint_url=endpoint_url
        ).Table(table_name)
