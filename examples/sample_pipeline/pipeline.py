# This file contains a sample pipeline. Loading data from a parquet file,
# using the load_from_parquet component, chain a custom dummy component, and use
# the reusable chunking component
import os
from pathlib import Path

import pandas as pd
import pyarrow as pa

from fondant.component import PandasTransformComponent
from fondant.pipeline import Pipeline, lightweight_component

BASE_PATH = Path("./.artifacts").resolve()
BASE_PATH.mkdir(parents=True, exist_ok=True)

# Define pipeline
pipeline = Pipeline(name="dummy-pipeline", base_path=str(BASE_PATH))

# Load from hub component
load_component_column_mapping = {
    "text": "text_data",
}

dataset = pipeline.read(
    "load_from_parquet",
    arguments={
        "dataset_uri": "/data/sample.parquet",
        "column_name_mapping": load_component_column_mapping,
        "n_rows_to_load": 5,
    },
    produces={"text_data": pa.string()},
)

dataset = dataset.apply(
    "./components/dummy_component",
)

dataset = dataset.apply(
    "chunk_text",
    arguments={"chunk_size": 10, "chunk_overlap": 2},
    consumes={"text": "text_data"},
)


@lightweight_component(
    base_image="python:3.8",
    extra_requires=[
        f"fondant[component]@git+https://github.com/ml6team/fondant@"
        f"{os.environ.get('FONDANT_VERSION', 'main')}",
    ],
)
class CalculateChunkLength(PandasTransformComponent):
    def __init__(self, feature_name: str, **kwargs):
        self.feature_name = feature_name

    def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        dataframe[self.feature_name] = dataframe["chunk"].apply(len)
        return dataframe


_ = dataset.apply(
    ref=CalculateChunkLength,
    consumes={"chunk": "text"},
    produces={"chunk_length": pa.int32()},
    arguments={"feature_name": "chunk_length"},
)
