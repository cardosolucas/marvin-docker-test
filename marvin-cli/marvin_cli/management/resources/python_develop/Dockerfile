FROM python:3-alpine3.10

MAINTAINER dev@marvin.apache.org

ENV SLEEP_MILLIS 0

USER root

##############################################################
# Define all environment variables to be used 
##############################################################

ENV MARVIN_HOME=/opt/marvin
ENV MARVIN_DATA_PATH=/opt/marvin/data
ENV SPARK_HOME=/opt/spark
ENV SPARK_CONF_DIR=$SPARK_HOME/conf
ENV HADOOP_CONF_DIR=$SPARK_CONF_DIR
ENV YARN_CONF_DIR=$SPARK_CONF_DIR



##############################################################
# Create all folders needed 
##############################################################

RUN mkdir -p $MARVIN_HOME && \
    mkdir -p $MARVIN_DATA_PATH && \
    mkdir -p /var/log/marvin/engines && \
    mkdir -p /var/run/marvin/engines && \
##############################################################
# Install the system dependencies for default installation 
##############################################################
    apk add --no-cache g++ openssl-dev openjdk11-jre-headless bash && \
    apk add --no-cache --virtual .build-deps make \
    git \
    wget \
    libsass-dev \
    openblas-dev \
    libffi-dev \
    libxml2-dev \
    libxslt-dev \
    libpng-dev \
    freetype-dev \
    cyrus-sasl-dev
##############################################################
# Install Apache Spark
#
# Uncomment if you are using spark, note that is needed the 
# spark configuration files to the think works correctly.
##############################################################
#
# RUN wget -O /tmp/spark-2.1.1-bin-hadoop2.6.tgz https://d3kbcqa49mib13.cloudfront.net/spark-2.1.1-bin-hadoop2.6.tgz && \
#    tar -xf /tmp/spark-2.1.1-bin-hadoop2.6.tgz -C /opt/ && \
#    ln -s /opt/spark-2.1.1-bin-hadoop2.6 /opt/spark
##############################################################

RUN mkdir -p $SPARK_CONF_DIR

RUN /bin/bash -c "pip install --no-cache numpy && \
    pip install --no-cache scipy && \
    pip install --no-cache pandas && \
    pip install --no-cache matplotlib && \
    pip install --no-cache cython && \
    pip install --no-cache scikit-learn && \
    pip install --no-cache Fabric && \
    pip install --no-cache marvin-python-toolbox"
##############################################################
# Uninstalling unnecessary software and cleaning cache
##############################################################
RUN rm -rf /root/.cache