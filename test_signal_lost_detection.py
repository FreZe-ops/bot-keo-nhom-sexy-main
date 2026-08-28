from PIL import Image
import os

def check_video_area(img_path):
    if not os.path.exists(img_path):
        print(f"Not found: {img_path}")
        return
    im = Image.open(img_path).convert('RGB')
    w, h = im.size
    
    # Vùng video ở giữa: x từ 20% đến 80%, y từ 15% đến 65%
    box = (int(w * 0.20), int(h * 0.15), int(w * 0.80), int(h * 0.65))
    crop = im.crop(box)
    pixels = crop.getdata()
    
    total = len(pixels)
    dark_count = sum(1 for r, g, b in pixels if r < 35 and g < 35 and b < 35)
    dark_ratio = dark_count / total
    print(f"Image: {os.path.basename(img_path)} ({w}x{h}) -> Video dark ratio = {dark_ratio*100:.1f}% ({dark_count}/{total})")

check_video_area(r'C:\Users\daodu\.gemini\antigravity-ide\brain\5cf83c02-a2f8-4b5c-ae84-38aa33ee83ab\.user_uploaded\media_1787648619623.png')
check_video_area(r'd:\BOT KEO NHOM BCR\bot-keo-nhom-bcr-main\sexy_C01_R20_2026-08-25T06-56-57-276Z.png')
