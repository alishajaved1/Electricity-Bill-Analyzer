"""Prepare uploaded bills for the model and for on-screen preview."""
import io

from PIL import Image, ImageOps

MAX_SIDE = 2200


def prepare_upload(filename: str, data: bytes):
    """Return (mime_type, bytes_for_model, preview_png_bytes)."""
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        import fitz  # pymupdf
        doc = fitz.open(stream=data, filetype="pdf")
        if doc.page_count == 0:
            raise ValueError("The PDF has no pages.")
        pix = doc[0].get_pixmap(dpi=110)
        return "application/pdf", data, pix.tobytes("png")
    img = Image.open(io.BytesIO(data))
    img = ImageOps.exif_transpose(img)  # fixes photos taken rotated
    img = img.convert("RGB")
    if max(img.size) > MAX_SIDE:
        img.thumbnail((MAX_SIDE, MAX_SIDE))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    prev = io.BytesIO()
    small = img.copy()
    small.thumbnail((900, 1200))
    small.save(prev, format="PNG")
    return "image/jpeg", buf.getvalue(), prev.getvalue()
