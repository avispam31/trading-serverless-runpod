FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04
RUN pip install --no-cache-dir runpod pandas pyarrow scikit-learn numpy
COPY handler.py /handler.py
CMD ["python", "-u", "/handler.py"]
