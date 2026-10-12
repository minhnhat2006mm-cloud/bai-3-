# Bai 5: Chon anh bien so -> crop tung chu/so -> luu ra file anh (thu muc output/)
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np


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


def chay():
    path = filedialog.askopenfilename(
        title="Chon anh bien so",
        filetypes=[("Anh", "*.png *.jpg *.jpeg *.bmp"), ("Tat ca", "*.*")])
    if not path:
        return
    img = doc_anh(path)
    if img is None:
        messagebox.showerror("Loi", "Khong doc duoc anh!")
        return

    H, W = img.shape[:2]

    # Xam + lam mo nhe + threshold Otsu (tu chon nguong), dao: chu -> trang
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(blur, 0, 255,
                              cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # RETR_LIST: bien so co vien den bao quanh nen chu nam "ben trong" vien,
    # neu dung RETR_EXTERNAL se bo sot chu.
    contours = cv2.findContours(thresh, cv2.RETR_LIST,
                                cv2.CHAIN_APPROX_SIMPLE)[-2]

    # Giu contour du cao (chu/so), bo dau '-' '.', vien bien so, lo ben trong chu
    boxes = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if 0.4 * H < h < 0.95 * H and w < 0.3 * W:
            boxes.append((x, y, w, h))

    boxes.sort(key=lambda b: b[0])        # sap xep trai -> phai

    os.makedirs("output", exist_ok=True)
    ket_qua = img.copy()
    for i, (x, y, w, h) in enumerate(boxes):
        luu_anh(os.path.join("output", "kytu_%d.png" % (i + 1)), img[y:y + h, x:x + w])
        cv2.rectangle(ket_qua, (x, y), (x + w, y + h), (0, 255, 0), 2)

    print("Da luu %d ky tu vao thu muc output/" % len(boxes))
    cv2.imshow("Thresh", thu_nho(thresh))
    cv2.imshow("Ket qua", thu_nho(ket_qua))
    messagebox.showinfo("Ket qua", "Da luu %d ky tu vao thu muc output/" % len(boxes))
    cv2.waitKey(0)
    cv2.destroyAllWindows()


root = tk.Tk()
root.title("Bai 5")
root.geometry("320x130")
tk.Label(root, text="Bai 5: Crop chu so tren bien so", font=("Arial", 11)).pack(pady=12)
tk.Button(root, text="Start", width=15, height=2, command=chay).pack()
root.mainloop()