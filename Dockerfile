ARG BUILD_IMAGE="registry.gitlab.com/ska-telescope/ska-tango-images/ska-tango-images-pytango-builder:9.5.0"
ARG BASE_IMAGE="registry.gitlab.com/ska-telescope/ska-tango-images/ska-tango-images-pytango-runtime:9.5.0"
FROM $BUILD_IMAGE AS buildenv

FROM $BASE_IMAGE


# Install Poetry
USER root
ENV SETUPTOOLS_USE_DISTUTILS=stdlib

RUN poetry config virtualenvs.create false
WORKDIR /app

COPY --chown=tango:tango . /app
# Install runtime dependencies and the app
RUN poetry install --only main
RUN rm /usr/bin/python && ln -s /usr/bin/python3 /usr/bin/python
USER tango