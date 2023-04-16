FROM public.ecr.aws/lambda/python:3.9

COPY hello_world/requirements.txt ./
RUN python3.9 -m pip install -r requirements.txt -t .

COPY hello_world/app.py ./

# Command can be overwritten by providing a different command in the template directly.
CMD ["app.lambda_handler"]
