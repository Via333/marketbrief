# PDF 文本编辑器

这是一个使用 Flask 构建的简易网页工具，支持上传 PDF 文件、提取其中的文本内容，在浏览器中直接修改并保存为新的 PDF 文件。

## 功能特性

- 上传本地 PDF 文件并提取文字内容。
- 在网页中通过文本框编辑提取的内容。
- 将修改后的文本导出为新的 PDF 文件下载。

> ⚠️ 注意：重新生成的 PDF 仅包含纯文本内容，不保留原文件的排版、图片等信息。

## 环境准备

1. 建议使用 Python 3.11 及以上版本。
2. 创建虚拟环境（可选但推荐）：

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows 使用 .venv\Scripts\activate
   ```

3. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

## 运行项目

```bash
flask --app app run
```

默认情况下服务运行在 `http://127.0.0.1:5000/`。

## 使用方法

1. 访问网页后，在“选择要上传的 PDF 文件”处选择本地 PDF 并上传。
2. 程序会提取 PDF 中的文本并展示在编辑区域内。
3. 在文本框中进行修改后，点击“保存为新的 PDF”即可下载包含修改内容的 PDF 文件。

## 许可证

该项目以 MIT 协议发布，可自由复制、修改与分发。
