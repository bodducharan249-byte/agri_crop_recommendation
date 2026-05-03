import argparse
import json
import shutil
import tempfile
from pathlib import Path

import tensorflow as tf


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "plant_disease"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
MODEL_PATH = ARTIFACTS_DIR / "plant_disease_model.keras"
CLASS_NAMES_PATH = ARTIFACTS_DIR / "class_names.json"

IMAGE_SIZE = (224, 224)
SEED = 42


def find_split_dirs(root: Path) -> tuple[Path, Path | None]:
    if not root.exists():
        raise FileNotFoundError(
            f"Dataset folder not found: {root}. Run system2_plant_disease/download_dataset.py first."
        )

    train_dirs = [
        path
        for path in root.rglob("*")
        if path.is_dir() and path.name.lower() in {"train", "training"}
    ]
    valid_dirs = [
        path
        for path in root.rglob("*")
        if path.is_dir() and path.name.lower() in {"valid", "validation", "val"}
    ]

    if not train_dirs:
        raise FileNotFoundError("Could not find a train directory inside the plant disease dataset.")

    train_dir = sorted(train_dirs, key=lambda path: len(path.parts))[0]
    valid_dir = sorted(valid_dirs, key=lambda path: len(path.parts))[0] if valid_dirs else None
    return train_dir, valid_dir


def make_quick_test_subset(train_dir: Path, valid_dir: Path | None) -> tuple[tempfile.TemporaryDirectory, Path, Path | None]:
    temp_dir = tempfile.TemporaryDirectory()
    temp_root = Path(temp_dir.name)
    quick_train = temp_root / "train"
    quick_valid = temp_root / "valid"

    class_dirs = sorted([path for path in train_dir.iterdir() if path.is_dir()])[:3]
    if len(class_dirs) < 3:
        raise ValueError("Quick test mode needs at least 3 class folders in the training data.")

    for class_dir in class_dirs:
        destination = quick_train / class_dir.name
        destination.mkdir(parents=True, exist_ok=True)
        for image_path in sorted(class_dir.glob("*"))[:40]:
            if image_path.is_file():
                shutil.copy2(image_path, destination / image_path.name)

    if valid_dir and valid_dir.exists():
        for class_dir in class_dirs:
            source_valid = valid_dir / class_dir.name
            if not source_valid.exists():
                continue
            destination = quick_valid / class_dir.name
            destination.mkdir(parents=True, exist_ok=True)
            for image_path in sorted(source_valid.glob("*"))[:15]:
                if image_path.is_file():
                    shutil.copy2(image_path, destination / image_path.name)

    return temp_dir, quick_train, quick_valid if quick_valid.exists() else None


def build_model(class_count: int) -> tf.keras.Model:
    base_model = tf.keras.applications.MobileNetV2(
        include_top=False,
        weights="imagenet",
        input_shape=(*IMAGE_SIZE, 3),
    )
    base_model.trainable = False

    inputs = tf.keras.Input(shape=(*IMAGE_SIZE, 3))
    x = tf.keras.applications.mobilenet_v2.preprocess_input(inputs)
    x = base_model(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.25)(x)
    outputs = tf.keras.layers.Dense(class_count, activation="softmax")(x)

    model = tf.keras.Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def load_datasets(train_dir: Path, valid_dir: Path | None, batch_size: int):
    dataset_args = {
        "image_size": IMAGE_SIZE,
        "batch_size": batch_size,
        "label_mode": "int",
        "seed": SEED,
    }

    if valid_dir:
        train_ds = tf.keras.utils.image_dataset_from_directory(train_dir, shuffle=True, **dataset_args)
        valid_ds = tf.keras.utils.image_dataset_from_directory(valid_dir, shuffle=False, **dataset_args)
    else:
        train_ds = tf.keras.utils.image_dataset_from_directory(
            train_dir,
            validation_split=0.2,
            subset="training",
            shuffle=True,
            **dataset_args,
        )
        valid_ds = tf.keras.utils.image_dataset_from_directory(
            train_dir,
            validation_split=0.2,
            subset="validation",
            shuffle=False,
            **dataset_args,
        )

    class_names = train_ds.class_names
    train_ds = train_ds.prefetch(tf.data.AUTOTUNE)
    valid_ds = valid_ds.prefetch(tf.data.AUTOTUNE)
    return train_ds, valid_ds, class_names


def main() -> None:
    parser = argparse.ArgumentParser(description="Train System 2 plant disease detector.")
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument(
        "--quick_test",
        action="store_true",
        help="Train only 3 classes for 1 epoch to verify the pipeline.",
    )
    args = parser.parse_args()

    train_dir, valid_dir = find_split_dirs(DATA_DIR)
    temp_subset = None

    if args.quick_test:
        print("Quick test mode enabled: using 3 classes for 1 epoch.")
        temp_subset, train_dir, valid_dir = make_quick_test_subset(train_dir, valid_dir)
        args.epochs = 1

    try:
        train_ds, valid_ds, class_names = load_datasets(train_dir, valid_dir, args.batch_size)
        model = build_model(len(class_names))

        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor="val_accuracy",
                patience=2,
                restore_best_weights=True,
            )
        ]

        history = model.fit(
            train_ds,
            validation_data=valid_ds,
            epochs=args.epochs,
            callbacks=callbacks,
        )

        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        model.save(MODEL_PATH)
        CLASS_NAMES_PATH.write_text(json.dumps(class_names, indent=2), encoding="utf-8")

        best_accuracy = max(history.history.get("val_accuracy", [0.0])) * 100
        print(f"Best validation accuracy: {best_accuracy:.2f}%")
        print(f"Saved model to: {MODEL_PATH}")
        print(f"Saved class names to: {CLASS_NAMES_PATH}")
    finally:
        if temp_subset is not None:
            temp_subset.cleanup()


if __name__ == "__main__":
    main()
