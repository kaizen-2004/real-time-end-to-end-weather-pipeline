import pytest
import importlib.util
import sys
from pathlib import Path


def test_dag_import():
    dag_path = Path(__file__).parent.parent / "dags" / "weather_pipeline.py"
    assert dag_path.exists(), f"DAG file not found: {dag_path}"

    spec = importlib.util.spec_from_file_location("weather_pipeline", dag_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["weather_pipeline"] = module


def test_dags_folder_exists():
    dags_dir = Path(__file__).parent.parent / "dags"
    assert dags_dir.exists(), "dags/ directory does not exist"


def test_include_folder_exists():
    include_dir = Path(__file__).parent.parent / "include"
    assert include_dir.exists(), "include/ directory does not exist"
