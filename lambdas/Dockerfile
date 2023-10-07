FROM public.ecr.aws/lambda/python:3.8

COPY . ${LAMBDA_TASK_ROOT}/

RUN pip install poetry==1.4.2

RUN poetry export --format requirements.txt --output requirements.txt --without-hashes

CMD ["api.app"]
