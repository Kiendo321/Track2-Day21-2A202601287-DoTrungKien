import os
import json
import numpy as np
import pandas as pd
from src.train import train


FEATURE_NAMES = [
    "fixed_acidity", "volatile_acidity", "citric_acid", "residual_sugar",
    "chlorides", "free_sulfur_dioxide", "total_sulfur_dioxide", "density",
    "pH", "sulphates", "alcohol", "wine_type",
]


def _make_temp_data(tmp_path):
    """
    Tạo dataset nhỏ với cùng schema Wine Quality để sử dụng trong test.

    pytest cung cấp `tmp_path` là một thư mục tạm thời, tự động được xóa sau khi test kết thúc.
    """
    rng = np.random.default_rng(0)
    n = 200
    X = rng.random((n, len(FEATURE_NAMES)))
    y = rng.integers(0, 3, size=n)

    df = pd.DataFrame(X, columns=FEATURE_NAMES)
    df["target"] = y

    train_df = df.iloc[:160]
    eval_df = df.iloc[160:]

    train_path = str(tmp_path / "train.csv")
    eval_path = str(tmp_path / "eval.csv")

    train_df.to_csv(train_path, index=False)
    eval_df.to_csv(eval_path, index=False)

    return train_path, eval_path


def test_train_returns_float(tmp_path):
    """Kiểm tra hàm train() trả về một số thực trong khoảng [0, 1]."""
    train_path, eval_path = _make_temp_data(tmp_path)
    acc = train(
        {"n_estimators": 10, "max_depth": 3},
        data_path=train_path,
        eval_path=eval_path,
    )
    assert isinstance(acc, float)
    assert 0.0 <= acc <= 1.0


def test_metrics_file_created(tmp_path):
    """Kiểm tra file outputs/metrics.json được tạo sau khi huấn luyện."""
    train_path, eval_path = _make_temp_data(tmp_path)
    train(
        {"n_estimators": 10, "max_depth": 3},
        data_path=train_path,
        eval_path=eval_path,
    )
    metrics_file = "outputs/metrics.json"
    assert os.path.exists(metrics_file)
    with open(metrics_file) as f:
        data = json.load(f)
    assert "accuracy" in data
    assert "f1_score" in data


def test_model_file_created(tmp_path):
    """Kiểm tra file models/model.pkl được tạo sau khi huấn luyện."""
    train_path, eval_path = _make_temp_data(tmp_path)
    train(
        {"n_estimators": 10, "max_depth": 3},
        data_path=train_path,
        eval_path=eval_path,
    )
    assert os.path.exists("models/model.pkl")
