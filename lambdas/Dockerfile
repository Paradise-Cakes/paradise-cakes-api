FROM public.ecr.aws/lambda/python:3.8

COPY . ${LAMBDA_TASK_ROOT}/

RUN cd ${LAMBDA_TASK_ROOT} && \
    python -m pip install poetry==1.4.2 && \
    poetry export -f requirements.txt --without-hashes > requirements.txt

CMD ["api.lambda_handler"]