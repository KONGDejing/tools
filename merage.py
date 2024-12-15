import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

def merge_pdfs():
    # 选择第一个PDF文件
    file_path1 = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if not file_path1:
        return
    file_path2 = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if not file_path2:
        return
    
    # 设置输出文件路径
    output_file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not output_file:
        return
    
    # 构建pdftk命令
    command = ["pdftk", file_path1, file_path2, "cat", "output", output_file]
    
    try:
        # 执行命令
        subprocess.run(command, check=True)
        messagebox.showinfo("Success", "PDFs have been merged successfully!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to merge PDFs: {e}")

###############################
def merge_pdfs1():
    # 选择第一个PDF文件
    file_path1 = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if not file_path1:
        return
    file_path2 = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if not file_path2:
        return
    
    # 设置输出文件路径
    output_file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not output_file:
        return
    
    # 构建pdftk命令
    command = ["pdftk", f"A={file_path1}", f"B={file_path2}", "shuffle", "A", "Bend-1", "output", output_file]
    
    try:
        # 执行命令
        subprocess.run(command, check=True)
        messagebox.showinfo("Success", "PDFs have been merged successfully!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to merge PDFs: {e}")
# 创建主窗口
root = tk.Tk()
root.title("PDF Merger")

# 创建合并按钮
merge_button = tk.Button(root, text="直接拼接 Merge PDFs", command=merge_pdfs)
merge_button.pack(pady=20)

# 创建合并按钮
merge_button = tk.Button(root, text="奇正序、偶倒序交叉合并 Merge PDFs", command=merge_pdfs1)
merge_button.pack(pady=20)

# 运行主循环
root.mainloop()