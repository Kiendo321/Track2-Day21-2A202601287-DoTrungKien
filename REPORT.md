# BÁO CÁO KẾT QUẢ LAB: XÂY DỰNG HỆ THỐNG CI/CD VÀ CONTINUOUS TRAINING CHO AI SYSTEMS

**Họ và tên / Mã học viên:** Đỗ Trung Kiên / 2A202601287
**Dự án:** Kiendo321/K3-Track2-Day21-CI-CD-for-AI-Systems  
**Ngày thực hiện:** 21/08/2026  

---

## 1. Bộ Siêu Tham Số Đã Chọn Và Lý Do (Dựa trên MLflow)

* **Bộ siêu tham số tối ưu đã chọn (`params.yaml`):**
  * `n_estimators`: `100` (Số cây quyết định trong Random Forest)
  * `max_depth`: `20` (Độ sâu tối đa của mỗi cây)
  * `min_samples_split`: `2` (Số lượng mẫu tối thiểu để tách nút)

* **Lý do lựa chọn (Dựa trên kết quả MLflow Tracking):**
  * Trong quá trình thực nghiệm tại **Bước 1**, khi sử dụng `max_depth` nông (`10`), mô hình bị underfitting trên tập dữ liệu đánh giá, chỉ đạt Accuracy **~0.6440 – 0.6620** (bị dừng ở bước Quality Gate `0.70`).
  * Khi tăng `max_depth: 20` và `n_estimators: 100`, Random Forest biểu diễn tốt hơn các mối quan hệ phi tuyến phức tạp giữa các chỉ số hóa lý của rượu (`alcohol`, `volatile acidity`, `sulphates`,...) và xếp loại chất lượng, giúp tăng hiệu suất lên vượt ngưỡng **0.70** mà không bị quá rải rác.

---

## 2. So Sánh Hiệu Suất Mô Hình (Bước 2 vs Bước 3)

| Chỉ Số Đánh Giá | Bước 2 (2,998 mẫu Phase 1) | Bước 3 (5,996 mẫu Phase 1 + 2) | Mức Độ Cải Thiện |
|---|---|---|---|
| **Accuracy** | `0.6780` | **`0.7580`** | **+ 8.00%** 🚀 |
| **F1-Score (Weighted)** | `0.6767` | **`0.7562`** | **+ 7.95%** 🚀 |

* **Đánh giá & Nhận xét:**
  * Việc bổ sung **2,998 mẫu dữ liệu mới** ở Phase 2 giúp mở rộng phân bố dữ liệu huấn luyện, tăng cường khả năng tổng quát hóa của mô hình trên tập `eval.csv`.
  * Nhờ dữ liệu mới, Accuracy tăng từ `0.6780` lên `0.7580` (vượt ngưỡng Quality Gate `0.70`), kích hoạt CI/CD Pipeline tự động triển khai mô hình mới lên server sản phẩm VM.

---

## 3. Khó Khăn Gặp Phải Và Giải Pháp

1. **Lỗi Phân Quyền IAM / GCS Bucket trên Google Cloud Platform:**
   * *Khó khăn:* Khi chạy `dvc pull` và khởi động REST API trên VM, Service Account bị từ chối quyền `storage.objects.get` và `storage.objects.list` (`403 Forbidden`).
   * *Giải pháp:* Phân bổ quyền `roles/storage.admin` và `roles/storage.objectAdmin` cho Service Account `mlops-lab-sa` trên cả cấp độ Bucket và GCP Project.

2. **Lỗi Kết Nối Timeout / Connection Refused ở bước Deploy:**
   * *Khó khăn:* Job `Deploy` chạy lệnh `curl http://localhost:8000/health` sau 5 giây (`sleep 5`), nhưng máy chủ Compute Engine `e2-small` mất ~6 giây để nạp thư viện `scikit-learn` và tải mô hình từ GCS về, dẫn tới lỗi `Connection refused`.
   * *Giải pháp:* Cập nhật script deploy trong `.github/workflows/mlops.yml` tăng thời gian chờ lên `sleep 10` kết hợp cờ tự động thử lại `--retry 5 --retry-delay 3 --retry-connrefused`.

3. **Lỗi Proxy Artifact Scheme trong MLflow:**
   * *Khó khăn:* Khi dùng URI lưu trữ SQLite `sqlite:///mlflow.db`, MLflow báo lỗi không hỗ trợ proxy artifact scheme.
   * *Giải pháp:* Chỉ định rõ tham số `artifact_location="./mlartifacts"` khi khởi tạo `mlflow.create_experiment()`.
