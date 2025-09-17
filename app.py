from __future__ import annotations

import textwrap
from io import BytesIO

from flask import Flask, render_template, request, send_file
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

app = Flask(__name__)


def extract_text_from_pdf(uploaded_file) -> str:
    """Extracts text from an uploaded PDF file-like object."""
    uploaded_file.seek(0)
    reader = PdfReader(uploaded_file)
    text_parts: list[str] = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        text_parts.append(page_text)

    return "\n".join(text_parts).strip()


def build_pdf_from_text(text: str) -> BytesIO:
    """Generate a PDF document from plain text and return it as a BytesIO object."""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    left_margin = inch
    right_margin = inch
    top_margin = inch
    bottom_margin = inch

    max_line_width = width - left_margin - right_margin
    y_position = height - top_margin
    line_height = 14  # points

    def draw_text_line(line_text: str, current_y: float) -> float:
        pdf.drawString(left_margin, current_y, line_text)
        return current_y - line_height

    for paragraph in text.splitlines():
        if y_position <= bottom_margin:
            pdf.showPage()
            y_position = height - top_margin

        if not paragraph.strip():
            y_position = draw_text_line("", y_position)
            continue

        wrapped_lines = textwrap.wrap(
            paragraph,
            width=max(int(max_line_width / 7), 1),
            drop_whitespace=False,
        ) or [""]

        for line in wrapped_lines:
            if y_position <= bottom_margin:
                pdf.showPage()
                y_position = height - top_margin
            y_position = draw_text_line(line, y_position)

    pdf.save()
    buffer.seek(0)
    return buffer


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", pdf_text=None, error=None)


@app.route("/upload", methods=["POST"])
def upload_pdf():
    uploaded_file = request.files.get("pdf_file")

    if not uploaded_file or uploaded_file.filename == "":
        return render_template("index.html", pdf_text=None, error="请上传一个 PDF 文件。")

    if not uploaded_file.filename.lower().endswith(".pdf"):
        return render_template(
            "index.html", pdf_text=None, error="上传的文件必须是 PDF 格式。"
        )

    try:
        extracted_text = extract_text_from_pdf(uploaded_file.stream)
    except Exception as exc:  # pragma: no cover - defensive, route is not unit-tested
        return render_template(
            "index.html", pdf_text=None, error=f"读取 PDF 时出错: {exc}"
        )

    if not extracted_text:
        extracted_text = ""

    return render_template("index.html", pdf_text=extracted_text, error=None)


@app.route("/save", methods=["POST"])
def save_pdf():
    edited_text = request.form.get("pdf_text", "")

    if not edited_text.strip():
        return render_template(
            "index.html", pdf_text=edited_text, error="内容为空，无法生成 PDF。"
        )

    pdf_buffer = build_pdf_from_text(edited_text)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name="edited.pdf",
        mimetype="application/pdf",
    )


if __name__ == "__main__":
    app.run(debug=True)
