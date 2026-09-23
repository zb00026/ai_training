"""Pure-Python readers for modern Office formats (PPTX, XLSX, XLS)."""

from pathlib import Path

from openpyxl import load_workbook
from pptx import Presentation
import xlrd


def read_pptx(path: Path) -> str:
    prs = Presentation(str(path))
    parts: list[str] = []

    for slide_num, slide in enumerate(prs.slides, 1):
        slide_parts = [f"[Slide {slide_num}]"]
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    text = para.text.strip()
                    if text:
                        slide_parts.append(text)
            if shape.has_table:
                for row in shape.table.rows:
                    cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if cells:
                        slide_parts.append("\t".join(cells))

        if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
            notes = slide.notes_slide.notes_text_frame.text.strip()
            if notes:
                slide_parts.append(f"[Notes] {notes}")

        if len(slide_parts) > 1:
            parts.append("\n".join(slide_parts))

    return "\n\n".join(parts)


def read_xlsx(path: Path) -> str:
    wb = load_workbook(str(path), read_only=True, data_only=True)
    parts: list[str] = []

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        sheet_parts = [f"[Sheet: {sheet_name}]"]
        for row in ws.iter_rows(values_only=True):
            cells = [str(cell).strip() for cell in row if cell is not None and str(cell).strip()]
            if cells:
                sheet_parts.append("\t".join(cells))
        if len(sheet_parts) > 1:
            parts.append("\n".join(sheet_parts))

    wb.close()
    return "\n\n".join(parts)


def read_xls(path: Path) -> str:
    book = xlrd.open_workbook(str(path))
    parts: list[str] = []

    for sheet in book.sheets():
        sheet_parts = [f"[Sheet: {sheet.name}]"]
        for row_idx in range(sheet.nrows):
            cells = [
                str(sheet.cell_value(row_idx, col_idx)).strip()
                for col_idx in range(sheet.ncols)
                if str(sheet.cell_value(row_idx, col_idx)).strip()
            ]
            if cells:
                sheet_parts.append("\t".join(cells))
        if len(sheet_parts) > 1:
            parts.append("\n".join(sheet_parts))

    return "\n\n".join(parts)
