# Bai 2: Chon file video -> phat len man hinh
#   Phim A: xoay nguoc chieu kim dong ho 90 do
#   Phim D: xoay theo chieu kim dong ho 90 do
#   Phim O: mo video khac (khong can dong chuong trinh)
#   Phim Space: tam dung / tiep tuc
#   Phim Q hoac ESC: thoat
import os
import shutil
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2

LOAI_VIDEO = [("Video", "*.mp4 *.avi *.mkv *.mov *.wmv"), ("Tat ca", "*.*")]


def mo_video(path):
    """Mo video. Tra ve (cap, file_tam). Du phong cho duong dan co ky tu dac biet."""
    cap = cv2.VideoCapture(path)
    if cap.isOpened():
        return cap, None
    tmp = os.path.join(tempfile.gettempdir(), "tmp_video" + os.path.splitext(path)[1])
    shutil.copy(path, tmp)
    return cv2.VideoCapture(tmp), tmp


def thu_nho(img, max_w=1000, max_h=700):
    h, w = img.shape[:2]
    s = min(max_w / w, max_h / h, 1)
    return cv2.resize(img, (int(w * s), int(h * s))) if s < 1 else img


def dong_video(cap, tmp):
    if cap is not None:
        cap.release()
    if tmp and os.path.exists(tmp):
        os.remove(tmp)


def chon_va_mo():
    """Hien hop thoai chon video. Tra ve (cap, tmp, delay, ten_file) hoac None."""
    path = filedialog.askopenfilename(title="Chon video", filetypes=LOAI_VIDEO)
    if not path:
        return None
    cap, tmp = mo_video(path)
    if not cap.isOpened():
        dong_video(cap, tmp)
        messagebox.showerror("Loi", "Khong mo duoc video:\n" + path)
        return None
    fps = cap.get(cv2.CAP_PROP_FPS)
    delay = max(1, int(1000 / fps)) if fps and fps > 0 else 30
    return cap, tmp, delay, os.path.basename(path)


def chay():
    ket_qua = chon_va_mo()
    if ket_qua is None:
        return
    cap, tmp, delay, ten_file = ket_qua
    lbl_ten.config(text="Dang phat: " + ten_file)

    goc = 0            # goc xoay NGUOC chieu kim dong ho: 0, 90, 180, 270
    tam_dung = False
    frame = None
    TIEU_DE = "Video (A: nguoc KDH | D: thuan KDH | O: mo video khac | Space: dung | Q: thoat)"

    while True:
        if not tam_dung:
            ret, frame = cap.read()
            if not ret:                       # het video -> phat lai tu dau
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

        hien_thi = frame
        if goc == 90:
            hien_thi = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif goc == 180:
            hien_thi = cv2.rotate(frame, cv2.ROTATE_180)
        elif goc == 270:
            hien_thi = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        hien_thi = thu_nho(hien_thi).copy()
        cv2.putText(hien_thi, "Goc: %d do (nguoc KDH)" % goc, (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow(TIEU_DE, hien_thi)

        key = cv2.waitKey(delay) & 0xFF
        if key in (ord('q'), ord('Q'), 27):
            break
        elif key in (ord('a'), ord('A')):
            goc = (goc + 90) % 360            # nguoc chieu kim dong ho
        elif key in (ord('d'), ord('D')):
            goc = (goc - 90) % 360            # theo chieu kim dong ho
        elif key == ord(' '):
            tam_dung = not tam_dung
        elif key in (ord('o'), ord('O')):     # chon video khac
            moi = chon_va_mo()
            if moi is not None:
                dong_video(cap, tmp)
                cap, tmp, delay, ten_file = moi
                lbl_ten.config(text="Dang phat: " + ten_file)
                tam_dung = False

    dong_video(cap, tmp)
    cv2.destroyAllWindows()
    lbl_ten.config(text="Chua chon video")


root = tk.Tk()
root.title("Bai 2")
root.geometry("420x190")
tk.Label(root, text="Bai 2: Phat video, A / D de xoay 90 do",
         font=("Arial", 11)).pack(pady=10)
tk.Button(root, text="Chon video", width=16, height=2, command=chay).pack()
lbl_ten = tk.Label(root, text="Chua chon video", fg="gray")
lbl_ten.pack(pady=8)
root.mainloop()