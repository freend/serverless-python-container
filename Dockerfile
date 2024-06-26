# Use an official Python runtime as a parent image
FROM public.ecr.aws/lambda/python:3.9

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install --no-cache-dir -r ./requirements.txt

# Copy function code
COPY app ${LAMBDA_TASK_ROOT}

CMD [ "main.handler" ]