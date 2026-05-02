from pathlib import Path

# Import pandas for reading CSV data
import pandas as pd

# Import joblib for saving the trained model
import joblib

# Import train_test_split to split data into training and testing
from sklearn.model_selection import train_test_split

# Import Random Forest model
from sklearn.ensemble import RandomForestClassifier

# Import accuracy score to check model accuracy
from sklearn.metrics import accuracy_score

# Import classification report for detailed evaluation
from sklearn.metrics import classification_report


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "Crop_recommendation.csv"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
FEATURE_COLUMNS_PATH = ARTIFACTS_DIR / "feature_columns.joblib"
MODEL_PATH = ARTIFACTS_DIR / "crop_recommendation_model.joblib"

# Create artifacts folder to save model
ARTIFACTS_DIR.mkdir(exist_ok=True)

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found at {DATA_PATH}. Run download_dataset.py or add the CSV file."
    )

# Load the crop dataset
df = pd.read_csv(DATA_PATH)

# Show first 5 rows
print("First 5 rows:")
print(df.head())

# Show dataset size
print("\nDataset shape:")
print(df.shape)

# Show column names
print("\nColumns:")
print(df.columns)

# Check missing values
print("\nMissing values:")
print(df.isnull().sum())

# Select input features
X = df[["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]]

# Select output label
y = df["label"]

# Save feature column order for Streamlit app
joblib.dump(X.columns.tolist(), FEATURE_COLUMNS_PATH)

# Split data into training and testing data
X_train, X_test, y_train, y_test = train_test_split(
    X,                  # Input data
    y,                  # Output crop labels
    test_size=0.2,      # 20% data for testing
    random_state=42,    # Same result every time
    stratify=y          # Keep crop classes balanced
)

# Create Random Forest model
model = RandomForestClassifier(
    n_estimators=300,   # Number of trees
    random_state=42,    # Same result every time
    class_weight="balanced"  # Handles class balance safely
)

# Train the model
model.fit(X_train, y_train)

# Predict test data
y_pred = model.predict(X_test)

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)

# Print accuracy
print("\nModel Accuracy:")
print(accuracy)

# Print detailed report
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Train again using full dataset for final model
model.fit(X, y)

# Save final model
joblib.dump(model, MODEL_PATH)

# Print success message
print("\nModel saved successfully.")
print(f"Saved file: {MODEL_PATH.relative_to(BASE_DIR)}")
