import cv2
import os
import time
import sys
import numpy as np

# ==========================================
# 核心参数配置
# ==========================================
# 字符集：从暗到亮排列
ASCII_CHARS = np.array(list("@%#*+=-:. "))

# 宽度：决定了画面在终端里的横向长度
# 如果你的终端比较窄，建议调到 80-100；如果全屏运行，可以调到 150
TARGET_WIDTH = 100 

def video_to_ascii(video_path, new_width=TARGET_WIDTH):
    # 1. 打开视频文件
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ 无法打开视频文件: {video_path}")
        return

    # 获取视频原始帧率和总帧数
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or fps > 60:
        fps = 30 # 兜底帧率
    frame_time = 1.0 / fps

    # 2. 准备清屏指令和隐藏光标
    # \033[H 将光标移到左上角，\033[2J 清屏，\033[?25l 隐藏光标
    clear_cmd = "\033[H\033[2J"
    hide_cursor = "\033[?25l"
    show_cursor = "\033[?25h"

    print(hide_cursor, end="")

    try:
        while True:
            start_time = time.time()
            ret, frame = cap.read()
            if not ret:
                break # 视频播放结束

            # 3. 转换为灰度图
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 4. 计算缩放比例 (终端字符高宽比约 2:1，高度乘 0.55 补偿)
            h, w = gray.shape
            new_height = int(h * (new_width / w) * 0.55)
            resized = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # 5. 映射为 ASCII (NumPy 向量化操作)
            indices = (resized / 255.0 * (len(ASCII_CHARS) - 1)).astype(np.uint8)
            ascii_matrix = ASCII_CHARS[indices]
            
            # 拼接字符串
            ascii_str = "\n".join("".join(row) for row in ascii_matrix)
            
            # 6. 渲染到终端 (把光标移到左上角，直接覆盖上一帧)
            sys.stdout.write("\033[H" + ascii_str)
            sys.stdout.flush()
            
            # 7. 帧率控制 (计算处理耗时，补足剩余时间)
            elapsed = time.time() - start_time
            sleep_time = frame_time - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
                
    except KeyboardInterrupt:
        # 捕获 Ctrl+C 提前退出
        pass
    finally:
        # 恢复光标，释放资源
        print(show_cursor)
        cap.release()
        print("\n播放结束。")

if __name__ == "__main__":
    print("🎬 视频转 ASCII 动画 🎬")
    print("-" * 40)
    
    # 获取当前目录下的视频文件
    valid_exts = ('.mp4', '.avi', '.mov', '.mkv')
    video_files = [f for f in os.listdir('.') if f.lower().endswith(valid_exts)]
    
    if video_files:
        print("当前文件夹下发现以下视频：")
        for i, f in enumerate(video_files):
            print(f"  {i + 1}. {f}")
        print("-" * 40)
        
    file_name = input("请输入视频文件名 (例如 test.mp4): ").strip()
    
    if os.path.exists(file_name):
        print("3秒后开始播放，请将终端窗口全屏或拉到最大...")
        time.sleep(3)
        video_to_ascii(file_name)
    else:
        print(f"❌ 找不到文件: {file_name}")