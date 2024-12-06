from typing import List, Optional
from uuid import UUID

from aws_lambda_powertools.utilities.parser import BaseModel


def _clean(d):
    if type(d) is dict:
        for key in d.copy():
            d[key] = _clean(d[key])
            if type(d[key]) is UUID:
                d[key] = str(d[key])
            if d[key] is None:
                del d[key]
        return d
    elif type(d) is list:
        clean_list = []
        for item in d:
            clean_list.append(_clean(item))
        return clean_list
    return d


class Base(BaseModel):
    def clean(self):
        return _clean(self.model_dump())
