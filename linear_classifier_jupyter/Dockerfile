FROM jupyter/base-notebook:python-3.10.4

WORKDIR /home/jovyan/model

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

#CMD ["python", "linear_classifier.py", "--data=banknote.csv", "--seed=1", "--verbose"]
