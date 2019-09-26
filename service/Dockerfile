FROM alpine:3.8

RUN apk update && apk add --no-cache --virtual .build-deps \
	curl \
	python \
	openssh \
	bash \ 
	py-pip

COPY app /python_balena
WORKDIR /python_balena
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["service.py"]
