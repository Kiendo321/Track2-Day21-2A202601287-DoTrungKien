# BÁO CÁO KẾT QUẢ LAB: CI/CD VÀ CONTINUOUS TRAINING CHO AI SYSTEMS

**Dự án:** Kiendo321/K3-Track2-Day21-CI-CD-for-AI-Systems  
**Ngày hoàn thành:** 21/08/2026  

---

## 1. Bộ Siêu Tham Số Đã Chọn Và Lý Do (Dựa trên kết quả MLflow UI)

Trong **Bước 1**, mô hình Random Forest đã được tiến hành huấn luyện và theo dõi **4 lần chạy thực nghiệm** trên tập dữ liệu Phase 1 (2,998 mẫu), ghi nhận trực tiếp trên giao diện MLflow UI (`http://localhost:5000`):

| Run Name MLflow | `n_estimators` | `max_depth` | `min_samples_split` | Accuracy | F1-Score | Đánh Giá Thực Nghiệm |
|---|---|---|---|---|---|---|
| **`abundant-pug-604`** | `50` | `3` | `2` | `0.558` | `0.5185` | Underfitting nghiêm trọng (Cây quá nông) |
| **`gaudy-fox-248`** | `100` | `5` | `2` | `0.564` | `0.5534` | Độ sâu 5 vẫn chưa đủ bắt các thuộc tính phi tuyến |
| **`rogue-gull-527`** | `200` | `10` | `5` | `0.644` | `0.6417` | Kết quả tăng lên |
| **`flawless-cub-156` (Chọn)** | `100` | `20` | `2` | **`0.684`** | **`0.6829`** | **Tối ưu nhất trên tập dữ liệu Phase 1** |

* **Lý do lựa chọn:** 
  * Dựa trên bảng so sánh trực quan từ MLflow UI, run **`flawless-cub-156`** (`n_estimators: 100`, `max_depth: 20`, `min_samples_split: 2`) cho kết quả vượt trội nhất với **Accuracy = 0.684** và **F1-Score = 0.6829**.
  * Việc thiết lập `max_depth: 20` giúp cây quyết định của mô hình Random Forest biểu diễn tốt các mối quan hệ phức tạp giữa các thuộc tính hóa lý của rượu mà không bị quá giới hạn như ở 3 lần chạy trước.

---

## 2. So Sánh Hiệu Suất Mô Hình Qua Các Bước (Bước 2 vs Bước 3)

Bảng tổng hợp kết quả chạy thực tế của bộ siêu tham số tối ưu qua các giai đoạn của bài Lab:

| Chỉ Số | Bước 2 (Phase 1: 2,998 mẫu) | Bước 3 (Phase 1+2: 5,996 mẫu) | Mức Độ Cải Thiện |
|---|---|---|---|
| **Accuracy** | `0.6840` | **`0.7580`** | **+ 7.40%** 🚀 |
| **F1-Score (Weighted)** | `0.6829` | **`0.7571`** | **+ 7.42%** 🚀 |
| **Kết quả CI/CD Pipeline** | Bị dừng ở `Eval` (`0.6840 < 0.70`) | **XANH cả 4 Jobs (`0.7580 >= 0.70`)** | **Tự động Deploy** |

* **Nhận xét luồng hoạt động:**
  * **Tại Bước 2:** Mô hình đạt Accuracy `0.6840`. Do cổng kiểm định chất lượng (Eval) đặt ngưỡng yêu cầu `Accuracy >= 0.70`, pipeline đã dừng lại chính xác tại bước `Eval` để ngăn không cho triển khai mô hình chưa đạt chuẩn lên máy chủ sản phẩm.
  * **Tại Bước 3:** Khi thêm 2,998 mẫu Phase 2 (tổng 5,996 mẫu) và push file `.dvc` lên Git, pipeline tự động kích hoạt lại. Nhờ có nhiều dữ liệu hơn, Accuracy tăng vọt lên **`0.7580`**, vượt qua ngưỡng `0.70`. Cả 4 jobs (`Test`, `Train`, `Eval`, `Deploy`) đều báo **XANH** và mô hình mới tự động được deploy thành công lên Compute Engine VM.

---

## 3. Khó Khăn Gặp Phải Và Cách Giải Quyết

1. **Lỗi MLflow Tracking URI Protocol (SSL Handshake Timeout):**
   * *Khó khăn:* Cấu hình nhầm URI tracking `https://127.0.0.1:5000` (HTTPS thay vì HTTP/SQLite) khiến script `train.py` bị treo do chờ bắt tay SSL.
   * *Giải pháp:* Khôi phục URI về `sqlite:///mlflow.db` (hoặc `http://127.0.0.1:5000`), giúp tiến trình ghi dữ liệu thực nghiệm vào SQLite thành công.

2. **Lỗi Phân Quyền IAM / GCS Bucket trên GCP:**
   * *Khó khăn:* Service Account ban đầu bị thiếu quyền `storage.objects.list` và `storage.objects.get` trên Google Cloud Storage (`403 Forbidden`) khi DVC pull và khi server VM tải model.
   * *Giải pháp:* Cấp bổ sung quyền `roles/storage.admin` cho Service Account `mlops-lab-sa` trên cả Bucket và GCP Project `ai-lab-16-gcp-gragas`.

3. **Lỗi Kết Nối SSH / Timeout ở bước Deploy trên VM:**
   * *Khó khăn:* Job `Deploy` chạy lệnh `curl /health` sau 5 giây (`sleep 5`), trong khi máy chủ VM cần ~6 giây để tải mô hình từ GCS và khởi động Uvicorn, gây ra lỗi `Connection refused`.
   * *Giải pháp:* Cập nhật script deploy trong `.github/workflows/mlops.yml` tăng thời gian chờ lên `sleep 10` kết hợp cờ tự động thử lại `--retry 5 --retry-delay 3`.
