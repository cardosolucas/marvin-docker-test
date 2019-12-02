FROM marvin-python:latest

ARG ENGINE_NAME
ENV ENGINE_NAME $ENGINE_NAME

ARG COMMAND
ENV COMMAND $COMMAND

EXPOSE 8888
EXPOSE 8000

CMD /bin/bash -c "cd $MARVIN_HOME && \
                  cd $ENGINE_NAME && \
                  pip install . && \
                  marvin $COMMAND"