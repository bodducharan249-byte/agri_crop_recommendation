# Crop Recommendation System

A Streamlit app that recommends the top crops for soil and weather inputs using a trained Random Forest model.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Retrain Model

The repository includes the dataset at `data/Crop_recommendation.csv`. To rebuild the model artifacts:

```bash
python train_model.py
```

This creates:

- `artifacts/crop_recommendation_model.joblib`
- `artifacts/feature_columns.joblib`

## Streamlit Cloud Deployment

1. Push this project to GitHub.
2. In Streamlit Cloud, create a new app from the repository.
3. Set the main file path to `app.py`.
4. Deploy.

Make sure the `artifacts` folder and `requirements.txt` are committed with the app.
