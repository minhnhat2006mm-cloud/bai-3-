# Bai 4: Chon anh bong bay -> dem va in ra so bong
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np


def doc_anh(path):
    data = np.fromfile(path, dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def thu_nho(img, max_w=1000, max_h=700):
    h, w = img.shape[:2]
    s = min(max_w / w, max_h / h, 1)
    return cv2.resize(img, (int(w * s), int(h * s))) if s < 1 else img


def chay():
    path = filedialog.askopenfilename(
        title="Chon anh bong bay",
        filetypes=[("Anh", "*.png *.jpg *.jpeg *.bmp"), ("Tat ca", "*.*")])
    if not path:
        return
    img = doc_anh(path)
    if img is None:
        messagebox.showerror("Loi", "Khong doc duoc anh!")
        return

    # Nen trang: moi kenh B,G,R deu ~255. Bong bay (ke ca bong vang) co it nhat
    # 1 kenh thap -> lay kenh nho nhat roi threshold se tach bong tot hon anh xam.
    min_kenh = np.min(img, axis=2)
    min_kenh = cv2.GaussianBlur(min_kenh, (5, 5), 0)
    _, thresh = cv2.threshold(min_kenh, 235, 255, cv2.THRESH_BINARY_INV)

    # Tim contour ngoai cung (moi qua bong = 1 contour)
    contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)[-2]

    # Bo nhieu nho (chi tiet le, bui) theo dien tich
    bongs = [c for c in contours if cv2.contourArea(c) > 500]
    so_bong = len(bongs)
    print("So bong trong hinh:", so_bong)

    cv2.drawContours(img, bongs, -1, (0, 255, 0), 2)
    cv2.putText(img, "So bong: %d" % so_bong, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    cv2.imshow("Thresh", thu_nho(thresh))
    cv2.imshow("Ket qua", thu_nho(img))
    messagebox.showinfo("Ket qua", "So bong trong hinh: %d" % so_bong)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


root = tk.Tk()
root.title("Bai 4")
root.geometry("320x130")
tk.Label(root, text="Bai 4: Dem so bong bay", font=("Arial", 11)).pack(pady=12)
tk.Button(root, text="Start", width=15, height=2, command=chay).pack()
root.mainloop()