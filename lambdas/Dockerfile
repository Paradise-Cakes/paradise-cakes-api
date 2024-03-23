FROM public.ecr.aws/lambda/python:3.8

COPY . ${LAMBDA_TASK_ROOT}/

RUN pip list

RUN cd ${LAMBDA_TASK_ROOT} && \
    python -m pip install poetry==1.4.2 && \
    poetry export -f requirements.txt --without-hashes > requirements.txt && \
    python -m pip install -r requirements.txt

CMD ["src.api.lambda_handler"]