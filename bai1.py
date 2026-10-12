# Bai 1: Chon anh -> chuyen sang mau xam -> hien thi
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np


def doc_anh(path):
    """Doc anh, chay duoc ca khi duong dan co dau tieng Viet."""
    data = np.fromfile(path, dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def thu_nho(img, max_w=1000, max_h=700):
    """Thu nho anh de vua man hinh (chi de hien thi)."""
    h, w = img.shape[:2]
    s = min(max_w / w, max_h / h, 1)
    return cv2.resize(img, (int(w * s), int(h * s))) if s < 1 else img


def chay():
    path = filedialog.askopenfilename(
        title="Chon anh",
        filetypes=[("Anh", "*.png *.jpg *.jpeg *.bmp"), ("Tat ca", "*.*")])
    if not path:
        return
    img = doc_anh(path)
    if img is None:
        messagebox.showerror("Loi", "Khong doc duoc anh!")
        return

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    cv2.imshow("Anh mau", thu_nho(img))
    cv2.imshow("Anh xam", thu_nho(gray))
    cv2.waitKey(0)          # bam phim bat ky de dong
    cv2.destroyAllWindows()


root = tk.Tk()
root.title("Bai 1")
root.geometry("320x130")
tk.Label(root, text="Bai 1: Anh mau -> anh xam", font=("Arial", 11)).pack(pady=12)
tk.Button(root, text="Start", width=15, height=2, command=chay).pack()
root.mainloop()