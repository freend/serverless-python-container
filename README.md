# Python Image AWS Lambda

<b>여기서는 python 3.9.7 버전을 기준으로 작업을 진행했습니다.</b>

lambda에서 docker image를 사용하기 위해서는 aws에서 제공하는 python 이미지를 사용해야 합니다. 현재 제공하는 이미지는 다음과 같습니다.
| 태그 | 런타임 | 운영 체제 | Dockerfile | 사용 중단 날짜 |
|-------|--------------|----------------|----------------------------|---------------------------|
| 3.12 | Python 3.12 | Amazon Linux 2023 | [파이썬 3.12 버전용 도커파일](https://github.com) | - |
| 3.11 | Python 3.11 | Amazon Linux 2 | [Python 3.11용 도커파일 버전](https://github.com) | - |
| 3.10 | Python 3.10 | Amazon Linux 2 | [파이썬 3.10용 도커파일](https://github.com) | - |
| 3.9 | Python 3.9 | Amazon Linux 2 | [Python 3.9 버전용 도커파일](https://github.com) | - |
| 3.8 | Python 3.8 | Amazon Linux 2 | [파이썬 3.8용 도커파일](https://github.com) | 2024년 10월 14일 |

위 이미지는 Dockerfile에서 받게되는데 해당이미지를 받기 위해서는 우선 아래의 명령을 이용해서 us-east-1의 ecr에 접속해야 합니다. 해당 명령은 아래와 같습니다.

```shell
aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws
```

# spec

해당 프로젝트에 사용된 라이브러리 및 파이선의 버전은 아래와 같습니다.

```text
python 3.9.7
fastapi 0.109.2
uvicorn 0.27.1
mangum 0.17.0
sqlalchemy 2.0.22
pymysql 1.1.0
pandas 1.5.3
```

# Folder 구조

실행에 관련된 파일을 app이라는 폴더 안에서 만드는 방식으로 제작하였습니다. 제일 기본적으로 설정된 파일의 구조는 다음과 같습니다.  
불필요한 파일등은 생략하였습니다.

```shell
.
├── Dockerfile
├── app
│   ├── api
│   │   └── order.py
│   ├── company.py
│   ├── database.py
│   └── main.py
└── requirements.txt
```

## main.py

```python
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from mangum import Mangum

from api.order import router as order_router

app = FastAPI()
api_router = APIRouter()

api_router.include_router(order_router)
app.include_router(api_router)

# Sample CORS Setting
origins = [
    "https://example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return { "Hello" : "World v1" }

handler = Mangum(app)
```

전과 다른 점은 handler를 함수로 만들어서 그 안의 함수를 호출했다면 이번에는 mangum을 hanlder로 만들어서 그것을 호출하는 것이 차이점 입니다.  
mangum 에 대한 내용은 다음과 같습니다.

> Mangum은 AWS Lambda와 같은 서버리스 환경에서 FastAPI와 같은 ASGI 애플리케이션을 실행할 수 있게 해주는 어댑터입니다. 이는 FastAPI와 같은 비동기 애플리케이션이 AWS Lambda의 서버리스 환경에서 실행될 수 있도록 중간에서 연결하는 역할을 합니다. 이를 통해 개발자는 FastAPI 애플리케이션을 AWS Lambda와 API Gateway를 통해 손쉽게 배포하고 운영할 수 있습니다.

# Dockerfile

lambda docker python의 Dockerfile의 기본내용은 다음과 같습니다.

```Docker
# Use an official Python runtime as a parent image
FROM public.ecr.aws/lambda/python:3.9

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r ./requirements.txt

# Copy function code
COPY app ${LAMBDA_TASK_ROOT}
https://docs.docker.com/build/building/multi-platform/
# Command to run the application
CMD [ "main.handler" ]
```

docker build 명령어는 다음과 같습니다. lambda 함수의 아키텍처가 x86_64 혹은 arm64 인지에 따라 2가지 빌드 방법이 존재합니다.

```shell
# platform x86_64
docker build --platform linux/amd64 -t docker-image:test .
# platform arm
docker build --platform linux/arm64 -t docker-image:test .
```

잘 보면 거의 동일한 명령이라 햇갈릴 수 있으며 lambda function 의 아키텍처와 Dockerfile 의 platform 이 다르면 오류가 발생하니 주의하시기 바랍니다.

# Run

이렇게 docker image 로 만들면 local 에서 docker 를 실행해서 작동 유무를 확인 할 수 있습니다.
실행 명령을 확인해 보도록 하겠습니다.
여기서도 빌드할 때의 platform 과 run 할 때의 platform 을 맞춰 주시기 바랍니다.

```shell
# arm으로 빌드한 이미지를 실행합니다.
docker run --platform linux/amd64 -p 9000:8080 --rm ocker-image:test
```

여기서 포트번호는 고정값 입니다. 그대로 사용하시면 됩니다.  
이제 포스트 맨을 실행한 후 아래 내용을 맞춰서 입력해 주시기 바랍니다.

```shell
# method
POST
# url
localhost:9000/2015-03-31/functions/function/invocations
```

그리고 Body 의 raw 에 JSON 으로 아래의 내용을 복사해 줍니다.

```json
{
  "body": "eyJ0ZXN0IjoiYm9keSJ9",
  "resource": "/{proxy+}",
  "path": "/",
  "httpMethod": "GET",
  "isBase64Encoded": true,
  "queryStringParameters": {
    "foo": "bar"
  },
  "multiValueQueryStringParameters": {
    "foo": ["bar"]
  },
  "pathParameters": {
    "proxy": "/path/to/resource"
  },
  "stageVariables": {
    "baz": "qux"
  },
  "headers": {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Accept-Language": "en-US,en;q=0.8",
    "Cache-Control": "max-age=0",
    "CloudFront-Forwarded-Proto": "https",
    "CloudFront-Is-Desktop-Viewer": "true",
    "CloudFront-Is-Mobile-Viewer": "false",
    "CloudFront-Is-SmartTV-Viewer": "false",
    "CloudFront-Is-Tablet-Viewer": "false",
    "CloudFront-Viewer-Country": "US",
    "Host": "1234567890.execute-api.us-east-1.amazonaws.com",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Custom User Agent String",
    "Via": "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
    "X-Amz-Cf-Id": "cDehVQoZnx43VYQb9j2-nvCh-9z396Uhbp027Y2JvkCPNLmGJHqlaA==",
    "X-Forwarded-For": "127.0.0.1, 127.0.0.2",
    "X-Forwarded-Port": "443",
    "X-Forwarded-Proto": "https"
  },
  "multiValueHeaders": {
    "Accept": [
      "appliation/json,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    ],
    "Accept-Encoding": ["gzip, deflate, sdch"],
    "Accept-Language": ["en-US,en;q=0.8"],
    "Cache-Control": ["max-age=0"],
    "CloudFront-Forwarded-Proto": ["https"],
    "CloudFront-Is-Desktop-Viewer": ["true"],
    "CloudFront-Is-Mobile-Viewer": ["false"],
    "CloudFront-Is-SmartTV-Viewer": ["false"],
    "CloudFront-Is-Tablet-Viewer": ["false"],
    "CloudFront-Viewer-Country": ["US"],
    "Host": ["0123456789.execute-api.us-east-1.amazonaws.com"],
    "Upgrade-Insecure-Requests": ["1"],
    "User-Agent": ["Custom User Agent String"],
    "Via": ["1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)"],
    "X-Amz-Cf-Id": ["cDehVQoZnx43VYQb9j2-nvCh-9z396Uhbp027Y2JvkCPNLmGJHqlaA=="],
    "X-Forwarded-For": ["127.0.0.1, 127.0.0.2"],
    "X-Forwarded-Port": ["443"],
    "X-Forwarded-Proto": ["https"]
  },
  "requestContext": {
    "accountId": "123456789012",
    "resourceId": "123456",
    "stage": "prod",
    "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
    "requestTime": "09/Apr/2015:12:34:56 +0000",
    "requestTimeEpoch": 1428582896000,
    "identity": {
      "cognitoIdentityPoolId": null,
      "accountId": null,
      "cognitoIdentityId": null,
      "caller": null,
      "accessKey": null,
      "sourceIp": "127.0.0.1",
      "cognitoAuthenticationType": null,
      "cognitoAuthenticationProvider": null,
      "userArn": null,
      "userAgent": "Custom User Agent String",
      "user": null
    },
    "path": "/prod/path/to/resource",
    "resourcePath": "/{proxy+}",
    "httpMethod": "POST",
    "apiId": "1234567890",
    "protocol": "HTTP/1.1"
  }
}
```

아래 내용중에서 우리가 변경할 부분은 맨 위의 `httpMethod`와 `path`입니다. 이 두개를 fast api 의
rest api 에 맞춰 주시면 됩니다. 그리고 실행하면 그 밑에 화면과 같은 결과가 나옵니다.

```text
{"statusCode": 200, "headers": {"content-length": "20", "content-type": "application/json"}, "multiValueHeaders": {}, "body": "{\"Hello\":\"World v1\"}", "isBase64Encoded": false}
```

# AWS gateway에서 함수 호출하기

문서 준비중 입니다.

# URL 연결하기

문서 준비중 입니다.

# 참고자료

[Docker Build Multi Platform](https://docs.docker.com/build/building/multi-platform/)
