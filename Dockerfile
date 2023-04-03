FROM python

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip

RUN pip install git+https://github.com/AaronWatters/H5Gizmos && \
  pip install git+https://github.com/AaronWatters/jp_doodle && \
  pip install git+https://github.com/AaronWatters/array_gizmos && \
  pip install git+https://github.com/flatironinstitute/mouse_embryo_labeller

RUN pip install -e .

CMD cd examples/lineage_sample && python load_sample_lineage.py
