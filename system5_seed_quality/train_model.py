import argparse
import json
import sys
from pathlib import Path

import tensorflow as tf


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "seed_quality"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
MODEL_PATH = ARTIFACTS_DIR / "seed_quality_model.keras"
CLASS_NAMES_PATH = ARTIFACTS_DIR / "seed_quality_class_names.json"
IMAGE_SIZE = (128, 128)
SEED = 42
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


def image_count(folder: Path) -> int:
    return len(image_paths(folder))


def image_paths(folder: Path) -> list[Path]:
    return sorted(path for path in folder.iterdir() if path.suffix.lower() in IMAGE_EXTENSIONS)


def find_image_root(data_dir: Path) -> Path:
    if not data_dir.exists():
        raise FileNotFoundError(
            f"Dataset folder not found: {data_dir}. Run system5_seed_quality/download_dataset.py first."
        )

    candidates = []
    for folder in [data_dir, *data_dir.rglob("*")]:
        if not folder.is_dir():
            continue

        class_dirs = [
            child
            for child in folder.iterdir()
            if child.is_dir() and image_count(child) > 0
        ]
        if len(class_dirs) >= 2:
            candidates.append((folder, len(class_dirs), sum(image_count(child) for child in class_dirs)))

    if not candidates:
        raise ValueError(
            f"No class folders with images found under {data_dir}. "
            "Expected folders such as intact, spotted, immature, broken, or skin-damaged."
        )

    candidates.sort(key=lambda item: (item[1], item[2]), reverse=True)
    return candidates[0][0]


def build_model(class_count: int, image_size: tuple[int, int]) -> tf.keras.Model:
    try:
        base_model = tf.keras.applications.MobileNetV2(
            input_shape=(*image_size, 3),
            include_top=False,
            weights="imagenet",
        )
    except Exception as exc:
        print(f"Could not load ImageNet weights, using MobileNetV2 without pretrained weights: {exc}")
        base_model = tf.keras.applications.MobileNetV2(
            input_shape=(*image_size, 3),
            include_top=False,
            weights=None,
        )

    base_model.trainable = False

    inputs = tf.keras.Input(shape=(*image_size, 3))
    x = tf.keras.applications.mobilenet_v2.preprocess_input(inputs)
    x = base_model(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    outputs = tf.keras.layers.Dense(class_count, activation="softmax")(x)

    model = tf.keras.Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def load_image(path: tf.Tensor, label: tf.Tensor) -> tuple[tf.Tensor, tf.Tensor]:
    image = tf.io.read_file(path)
    image = tf.io.decode_image(image, channels=3, expand_animations=False)
    image = tf.image.resize(image, IMAGE_SIZE)
    image.set_shape((*IMAGE_SIZE, 3))
    return image, label


def make_datasets(
    data_root: Path,
    class_names: list[str],
    batch_size: int,
) -> tuple[tf.data.Dataset, tf.data.Dataset]:
    paths = []
    labels = []
    for label, class_name in enumerate(class_names):
        class_dir = data_root / class_name
        class_paths = image_paths(class_dir)
        paths.extend(str(path) for path in class_paths)
        labels.extend([label] * len(class_paths))

    if len(paths) < len(class_names) * 2:
        raise ValueError("Not enough seed images found to create train and validation datasets.")

    dataset = tf.data.Dataset.from_tensor_slices((paths, labels))
    dataset = dataset.shuffle(buffer_size=len(paths), seed=SEED, reshuffle_each_iteration=False)

    validation_size = max(len(class_names), int(len(paths) * 0.2))
    validation_size = min(validation_size, len(paths) - len(class_names))

    val_ds = dataset.take(validation_size)
    train_ds = dataset.skip(validation_size)

    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.map(load_image, num_parallel_calls=AUTOTUNE)
    train_ds = train_ds.batch(batch_size).prefetch(AUTOTUNE)
    val_ds = val_ds.map(load_image, num_parallel_calls=AUTOTUNE)
    val_ds = val_ds.batch(batch_size).prefetch(AUTOTUNE)

    return train_ds, val_ds


def train_model(quick_test: bool = False) -> None:
    data_root = find_image_root(DATA_DIR)
    all_class_names = sorted(
        child.name for child in data_root.iterdir() if child.is_dir() and image_count(child) > 0
    )

    class_names = all_class_names[:3] if quick_test else all_class_names
    if len(class_names) < 2:
        raise ValueError("Need at least 2 seed quality classes to train the model.")

    epochs = 1 if quick_test else 10
    batch_size = 8 if quick_test else 32

    train_ds, val_ds = make_datasets(data_root, class_names, batch_size)

    model = build_model(class_count=len(class_names), image_size=IMAGE_SIZE)
    model.fit(train_ds, validation_data=val_ds, epochs=epochs)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    model.save(MODEL_PATH)
    CLASS_NAMES_PATH.write_text(json.dumps(class_names, indent=2), encoding="utf-8")

    print(f"Saved model to: {MODEL_PATH}")
    print(f"Saved class names to: {CLASS_NAMES_PATH}")
    print(f"Classes: {', '.join(class_names)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the System 5 seed quality model.")
    parser.add_argument(
        "--quick_test",
        action="store_true",
        help="Train only 3 classes for 1 epoch.",
    )
    args = parser.parse_args()

    try:
        train_model(quick_test=args.quick_test)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
