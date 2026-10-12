# Bai 3: Nhan dien khuon mat tren ANH hoac VIDEO
#   - Ve hinh chu nhat xanh la (Green) quanh moi khuon mat va dem so khuon mat
#   - Phim S    : luu cac khuon mat dang hien thi ra 0.png, 1.png, 2.png ... (thu muc faces/)
#   - Phim Space: tam dung / tiep tuc (chi o che do video)
#   - Phim Q/ESC: thoat
import os
import shutil
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np

TEN_FILE_XML = "haarcascade_frontalface_default.xml"
THU_MUC_LUU = "faces"


# ---------------------------------------------------------------- tien ich
def doc_anh(path):
    data = np.fromfile(path, dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def luu_anh(path, img):
    ok, buf = cv2.imencode(".png", img)
    if ok:
        buf.tofile(path)


def thu_nho(img, max_w=1000, max_h=700):
    h, w = img.shape[:2]
    s = min(max_w / w, max_h / h, 1)
    return cv2.resize(img, (int(w * s), int(h * s))) if s < 1 else img


def mo_video(path):
    cap = cv2.VideoCapture(path)
    if cap.isOpened():
        return cap, None
    # Du phong: duong dan co ky tu dac biet -> copy sang file tam
    tmp = os.path.join(tempfile.gettempdir(), "tmp_video" + os.path.splitext(path)[1])
    shutil.copy(path, tmp)
    return cv2.VideoCapture(tmp), tmp


def tai_bo_nhan_dien():
    """Tra ve CascadeClassifier, hoac None neu thu vien cv2 bi loi."""
    if not hasattr(cv2, "CascadeClassifier"):
        messagebox.showerror(
            "Loi thu vien OpenCV",
            "OpenCV cua ban thieu CascadeClassifier (phien ban %s).\n\n"
            "Chay: python -m pip uninstall -y opencv-python\n"
            "roi: python -m pip install \"opencv-python<5\"" % getattr(cv2, "__version__", "?"))
        return None
    ung_vien = []
    data_mod = getattr(cv2, "data", None)
    if data_mod is not None:
        ung_vien.append(os.path.join(data_mod.haarcascades, TEN_FILE_XML))
    if getattr(cv2, "__file__", None):
        ung_vien.append(os.path.join(os.path.dirname(cv2.__file__), "data", TEN_FILE_XML))
    ung_vien.append(TEN_FILE_XML)
    for p in ung_vien:
        if os.path.exists(p):
            cascade = cv2.CascadeClassifier(p)
            if not cascade.empty():
                return cascade
    messagebox.showerror("Khong tim thay file xml",
                         "Khong tim thay %s.\nCai lai opencv-python hoac de file xml canh bai3.py." % TEN_FILE_XML)
    return None


def tim_khuon_mat(cascade, frame, do_rong_xu_ly=640):
    """Tim khuon mat. Thu nho khung hinh de chay nhanh, tra toa do ve kich thuoc goc."""
    h, w = frame.shape[:2]
    s = min(1.0, do_rong_xu_ly / w)
    nho = cv2.resize(frame, (int(w * s), int(h * s))) if s < 1 else frame
    gray = cv2.cvtColor(nho, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)     # can bang sang, nhan dien on dinh hon
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1,
                                     minNeighbors=5, minSize=(30, 30))
    return [(int(x / s), int(y / s), int(fw / s), int(fh / s)) for (x, y, fw, fh) in faces]


def ve_khuon_mat(frame, faces):
    """Ve khung xanh Green quanh moi mat + dong chu dem. Tra ve ban sao da ve."""
    out = frame.copy()
    for (x, y, w, h) in faces:
        cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.putText(out, "So khuon mat: %d" % len(faces), (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    return out


def luu_khuon_mat(frame, faces, bat_dau=0):
    """Luu cac khuon mat thanh bat_dau.png, bat_dau+1.png ... Tra ve chi so tiep theo."""
    os.makedirs(THU_MUC_LUU, exist_ok=True)
    i = bat_dau
    for (x, y, w, h) in faces:
        luu_anh(os.path.join(THU_MUC_LUU, "%d.png" % i), frame[y:y + h, x:x + w])
        i += 1
    return i


# ---------------------------------------------------------------- che do ANH
def chay_anh():
    cascade = tai_bo_nhan_dien()
    if cascade is None:
        return
    path = filedialog.askopenfilename(
        title="Chon anh co khuon mat",
        filetypes=[("Anh", "*.png *.jpg *.jpeg *.bmp"), ("Tat ca", "*.*")])
    if not path:
        return
    img = doc_anh(path)
    if img is None:
        messagebox.showerror("Loi", "Khong doc duoc anh!")
        return

    faces = tim_khuon_mat(cascade, img)
    hien_thi = ve_khuon_mat(img, faces)
    print("So khuon mat:", len(faces))

    while True:
        cv2.imshow("Nhan dien khuon mat - ANH (S: luu, Q: thoat)", thu_nho(hien_thi))
        key = cv2.waitKey(0) & 0xFF
        if key in (ord('q'), ord('Q'), 27):
            break
        elif key in (ord('s'), ord('S')):
            luu_khuon_mat(img, faces, 0)       # anh: luu lai tu 0.png
            messagebox.showinfo("Da luu", "Da luu %d khuon mat vao thu muc %s/" % (len(faces), THU_MUC_LUU))
    cv2.destroyAllWindows()


# ---------------------------------------------------------------- che do VIDEO
def chay_video():
    cascade = tai_bo_nhan_dien()
    if cascade is None:
        return
    path = filedialog.askopenfilename(
        title="Chon video",
        filetypes=[("Video", "*.mp4 *.avi *.mkv *.mov *.wmv"), ("Tat ca", "*.*")])
    if not path:
        return
    cap, tmp = mo_video(path)
    if not cap.isOpened():
        messagebox.showerror("Loi", "Khong mo duoc video!")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    delay = max(1, int(1000 / fps)) if fps and fps > 0 else 30

    tam_dung = False
    frame = hien_thi = None
    faces = []
    so_mat_max = 0          # so mat nhieu nhat xuat hien trong 1 khung hinh
    chi_so_luu = 0          # dem tiep 0.png, 1.png... qua nhieu lan bam S
    tong_da_luu = 0

    while True:
        if not tam_dung:
            ret, frame = cap.read()
            if not ret:
                print("Het video.")
                break
            faces = tim_khuon_mat(cascade, frame)
            so_mat_max = max(so_mat_max, len(faces))
            hien_thi = ve_khuon_mat(frame, faces)
            cv2.putText(hien_thi, "Max: %d | Da luu: %d" % (so_mat_max, tong_da_luu),
                        (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        cv2.imshow("Nhan dien khuon mat - VIDEO (S: luu, Space: dung, Q: thoat)",
                   thu_nho(hien_thi))
        key = cv2.waitKey(delay) & 0xFF
        if key in (ord('q'), ord('Q'), 27):
            break
        elif key == ord(' '):
            tam_dung = not tam_dung
        elif key in (ord('s'), ord('S')) and frame is not None:
            chi_so_luu = luu_khuon_mat(frame, faces, chi_so_luu)
            tong_da_luu += len(faces)
            print("Da luu %d khuon mat (tong %d) vao thu muc %s/" % (len(faces), tong_da_luu, THU_MUC_LUU))

    cap.release()
    cv2.destroyAllWindows()
    if tmp and os.path.exists(tmp):
        os.remove(tmp)
    messagebox.showinfo("Ket thuc",
                        "So khuon mat nhieu nhat trong 1 khung hinh: %d\nDa luu: %d anh" % (so_mat_max, tong_da_luu))


# ---------------------------------------------------------------- giao dien
root = tk.Tk()
root.title("Bai 3")
root.geometry("380x170")
tk.Label(root, text="Bai 3: Nhan dien khuon mat (S: luu)",
         font=("Arial", 11)).pack(pady=12)
khung = tk.Frame(root)
khung.pack()
tk.Button(khung, text="Chon anh", width=14, height=2, command=chay_anh).grid(row=0, column=0, padx=8)
tk.Button(khung, text="Chon video", width=14, height=2, command=chay_video).grid(row=0, column=1, padx=8)
root.mainloop()