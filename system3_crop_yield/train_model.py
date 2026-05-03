from __future__ import annotations

import json
from pathlib import Path
import re

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "crop_yield"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
MODEL_PATH = ARTIFACTS_DIR / "crop_yield_model.joblib"
SCHEMA_PATH = ARTIFACTS_DIR / "crop_yield_schema.json"

TARGET_KEYWORDS = ("yield", "production")
CATEGORICAL_HINTS = (
    "crop",
    "state",
    "district",
    "location",
    "region",
    "season",
    "soil_type",
    "soil",
)
FEATURE_HINTS = (
    "crop",
    "state",
    "district",
    "location",
    "region",
    "season",
    "soil",
    "fertilizer",
    "nitrogen",
    "phosphorus",
    "potassium",
    "n",
    "p",
    "k",
    "ph",
    "rain",
    "rainfall",
    "temperature",
    "temp",
    "humidity",
    "moisture",
    "area",
    "weather",
)


def clean_column_name(column: str) -> str:
    cleaned = column.strip().lower()
    cleaned = re.sub(r"[^a-z0-9]+", "_", cleaned)
    cleaned = cleaned.strip("_")
    if cleaned == "yeild":
        return "yield"
    return cleaned


def find_csv_file() -> Path:
    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"Dataset folder not found: {DATA_DIR}. Run system3_crop_yield/download_dataset.py first."
        )

    csv_files = sorted(DATA_DIR.rglob("*.csv"), key=lambda path: path.stat().st_size, reverse=True)
    if not csv_files:
        raise FileNotFoundError(
            f"No CSV file found in {DATA_DIR}. Run system3_crop_yield/download_dataset.py first."
        )
    return csv_files[0]


def load_dataset() -> tuple[pd.DataFrame, Path]:
    csv_file = find_csv_file()
    df = pd.read_csv(csv_file)
    df.columns = [clean_column_name(str(column)) for column in df.columns]
    df = df.loc[:, ~df.columns.duplicated()]
    return df, csv_file


def identify_target_column(df: pd.DataFrame) -> str:
    candidates = [
        column
        for column in df.columns
        if any(keyword in column for keyword in TARGET_KEYWORDS)
        and pd.api.types.is_numeric_dtype(df[column])
    ]
    if not candidates:
        raise ValueError(
            "Could not identify a numeric yield target column. Expected a column containing "
            "'yield' or 'production'."
        )

    yield_candidates = [column for column in candidates if "yield" in column]
    return yield_candidates[0] if yield_candidates else candidates[0]


def select_feature_columns(df: pd.DataFrame, target_column: str) -> list[str]:
    feature_columns = [
        column
        for column in df.columns
        if column != target_column and any(hint in column for hint in FEATURE_HINTS)
    ]

    if not feature_columns:
        feature_columns = [column for column in df.columns if column != target_column]

    usable_columns = []
    for column in feature_columns:
        non_null_count = df[column].notna().sum()
        unique_count = df[column].nunique(dropna=True)
        if non_null_count > 0 and unique_count > 1:
            usable_columns.append(column)

    if not usable_columns:
        raise ValueError("No usable feature columns found for crop yield prediction.")

    return usable_columns


def split_feature_types(df: pd.DataFrame, feature_columns: list[str]) -> tuple[list[str], list[str]]:
    categorical_columns = []
    numerical_columns = []

    for column in feature_columns:
        if pd.api.types.is_numeric_dtype(df[column]) and column not in CATEGORICAL_HINTS:
            numerical_columns.append(column)
        else:
            categorical_columns.append(column)

    return categorical_columns, numerical_columns


def build_preprocessor(categorical_columns: list[str], numerical_columns: list[str]) -> ColumnTransformer:
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    numerical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    transformers = []
    if categorical_columns:
        transformers.append(("categorical", categorical_pipeline, categorical_columns))
    if numerical_columns:
        transformers.append(("numerical", numerical_pipeline, numerical_columns))

    return ColumnTransformer(transformers=transformers)


def make_schema(
    df: pd.DataFrame,
    feature_columns: list[str],
    categorical_columns: list[str],
    numerical_columns: list[str],
    target_column: str,
) -> dict:
    fields = []
    for column in feature_columns:
        if column in categorical_columns:
            values = sorted(str(value) for value in df[column].dropna().unique())
            fields.append(
                {
                    "name": column,
                    "type": "categorical",
                    "options": values[:200],
                    "default": values[0] if values else "",
                }
            )
        else:
            series = pd.to_numeric(df[column], errors="coerce")
            median = float(series.median()) if series.notna().any() else 0.0
            min_value = float(series.min()) if series.notna().any() else 0.0
            max_value = float(series.max()) if series.notna().any() else 100.0
            fields.append(
                {
                    "name": column,
                    "type": "numerical",
                    "default": median,
                    "min": min_value,
                    "max": max_value,
                }
            )

    return {
        "target_column": target_column,
        "target_unit": "dataset unit, commonly tons/hectare",
        "feature_columns": feature_columns,
        "categorical_columns": categorical_columns,
        "numerical_columns": numerical_columns,
        "fields": fields,
    }


def evaluate_model(name: str, pipeline: Pipeline, x_train, x_test, y_train, y_test) -> dict:
    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test)
    return {
        "name": name,
        "pipeline": pipeline,
        "mae": mean_absolute_error(y_test, predictions),
        "rmse": np.sqrt(mean_squared_error(y_test, predictions)),
        "r2": r2_score(y_test, predictions),
    }


def main() -> None:
    df, csv_file = load_dataset()
    target_column = identify_target_column(df)
    feature_columns = select_feature_columns(df, target_column)

    model_df = df[feature_columns + [target_column]].copy()
    model_df[target_column] = pd.to_numeric(model_df[target_column], errors="coerce")
    model_df = model_df.dropna(subset=[target_column])

    if len(model_df) < 10:
        raise ValueError("Not enough rows with a valid yield target to train a model.")

    categorical_columns, numerical_columns = split_feature_types(model_df, feature_columns)

    x = model_df[feature_columns]
    y = model_df[target_column]
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
    )

    models = {
        "RandomForestRegressor": RandomForestRegressor(
            n_estimators=300,
            random_state=42,
            n_jobs=1,
        ),
        "GradientBoostingRegressor": GradientBoostingRegressor(random_state=42),
        "LinearRegression": LinearRegression(),
    }

    results = []
    for name, estimator in models.items():
        pipeline = Pipeline(
            steps=[
                ("preprocessor", build_preprocessor(categorical_columns, numerical_columns)),
                ("model", estimator),
            ]
        )
        results.append(evaluate_model(name, pipeline, x_train, x_test, y_train, y_test))

    best_result = max(results, key=lambda result: result["r2"])
    final_pipeline = Pipeline(
        steps=[
            ("preprocessor", build_preprocessor(categorical_columns, numerical_columns)),
            ("model", models[best_result["name"]]),
        ]
    )
    final_pipeline.fit(x, y)

    ARTIFACTS_DIR.mkdir(exist_ok=True)
    joblib.dump(final_pipeline, MODEL_PATH)

    schema = make_schema(
        model_df,
        feature_columns,
        categorical_columns,
        numerical_columns,
        target_column,
    )
    schema["source_csv"] = str(csv_file.relative_to(BASE_DIR))
    schema["best_model"] = best_result["name"]
    schema["metrics"] = {
        result["name"]: {
            "mae": float(result["mae"]),
            "rmse": float(result["rmse"]),
            "r2": float(result["r2"]),
        }
        for result in results
    }

    SCHEMA_PATH.write_text(json.dumps(schema, indent=2), encoding="utf-8")

    print(f"Loaded dataset: {csv_file.relative_to(BASE_DIR)}")
    print(f"Target column: {target_column}")
    print(f"Feature columns: {feature_columns}")
    print("\nModel evaluation:")
    for result in sorted(results, key=lambda item: item["r2"], reverse=True):
        print(
            f"{result['name']}: "
            f"MAE={result['mae']:.4f}, RMSE={result['rmse']:.4f}, R2={result['r2']:.4f}"
        )
    print(f"\nBest model: {best_result['name']}")
    print(f"Saved model: {MODEL_PATH.relative_to(BASE_DIR)}")
    print(f"Saved schema: {SCHEMA_PATH.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
