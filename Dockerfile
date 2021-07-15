# Use SKA python image as base image
FROM artefact.skao.int/ska-tango-images-pytango-builder:9.3.10 as buildenv
FROM artefact.skao.int/ska-tango-images-pytango-runtime:9.3.10 AS runtime


# create ipython profile too so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create
USER root
RUN python3 -m pip install --user pytest-forked

# Note: working dir is `/app` which will have a copy of our repo
# The pip install will be a "user installation" so update path to access console scripts
ENV PATH=/home/tango/.local/bin:$PATH
RUN python3 -m pip install -e . --user
USER tango
