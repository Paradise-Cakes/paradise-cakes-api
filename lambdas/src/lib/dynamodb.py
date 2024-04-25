from boto3.session import Session

_session = Session()


class DynamoConnection:
    def __init__(self, region_name, endpoint_url, table_name):
        self.table = _session.resource(
            "dynamodb", region_name=region_name, endpoint_url=endpoint_url
        ).Table(table_name)


def update_attributes_expression(attributes):
    set_expression_clauses = [
        f"#{k} = :{k}" for (k, v) in attributes.items() if v is not None
    ]
    set_expression = (
        f'SET {", ".join(set_expression_clauses)}' if set_expression_clauses else None
    )

    expression = " ".join([e for e in [set_expression] if e])

    expression_attribute_names = {f"#{k}": k for (k, v) in attributes.items()}
    expression_attribute_values = {
        f":{k}": v for (k, v) in attributes.items() if v is not None
    }

    return {
        "UpdateExpression": expression,
        "ExpressionAttributeNames": expression_attribute_names,
        "ExpressionAttributeValues": expression_attribute_values,
    }
