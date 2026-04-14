import io

import fitz
import pandas as pd
import streamlit as st
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image


def pdf_to_images(uploaded_pdf):
    pdf_bytes = uploaded_pdf.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    images = []
    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_bytes = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_bytes))
        images.append(image)

    return images


def return_barcode(value: str):
    buffer = io.BytesIO()
    Code128(value, writer=ImageWriter()).write(buffer)
    buffer.seek(0)
    return buffer


def view_and_correct(result_of_ocr, key: str):
    table = pd.DataFrame(result_of_ocr)
    return st.data_editor(table, use_container_width=True, key=key)


uploaded_files = st.file_uploader(
    "Загрузите файлы",
    accept_multiple_files=True,
    type=["jpg", "jpeg", "png", "pdf"],
)

all_tables = []
passport_store = {}

if uploaded_files:
    for i, uploaded_file in enumerate(uploaded_files, start=1):
        passport_id = f"PAS-{i:06}"

        st.subheader(f"{uploaded_file.name} — {passport_id}")

        file_bytes = uploaded_file.getvalue()

        if uploaded_file.type.startswith("image/"):
            st.image(file_bytes, use_container_width=True)

        elif uploaded_file.type == "application/pdf":
            images = pdf_to_images(io.BytesIO(file_bytes))
            for page_number, image in enumerate(images, start=1):
                st.write(f"Страница {page_number}")
                st.image(image, use_container_width=True)

        edited_table = view_and_correct(
            [
                {
                    "passport_id": passport_id,
                    "file_name": uploaded_file.name,
                    "serial_number": "12345",
                    "manufacturer": "ООО Завод",
                    "date": "2024-01-01",
                    "barcode_value": passport_id,
                }
            ],
            key=f"editor_{passport_id}",
        )

        st.image(return_barcode(passport_id), width=220)

        all_tables.append(edited_table)

        passport_store[passport_id] = {
            "file_name": uploaded_file.name,
            "file_type": uploaded_file.type,
            "file_bytes": file_bytes,
        }

    st.session_state["passport_store"] = passport_store
    st.session_state["final_table"] = pd.concat(all_tables, ignore_index=True)

    st.divider()
    st.subheader("Поиск паспорта по штрихкоду")

    scanned_code = st.text_input("Введите код со штрихкода", placeholder="PAS-000001")

    if scanned_code:
        store = st.session_state.get("passport_store", {})
        final_table = st.session_state.get("final_table")

        if scanned_code in store:
            passport = store[scanned_code]
            st.success(f"Паспорт найден: {passport['file_name']}")

            if final_table is not None:
                matched = final_table[final_table["passport_id"] == scanned_code]
                st.dataframe(matched, use_container_width=True)

            if passport["file_type"].startswith("image/"):
                st.image(passport["file_bytes"], use_container_width=True)

            elif passport["file_type"] == "application/pdf":
                images = pdf_to_images(io.BytesIO(passport["file_bytes"]))
                for page_number, image in enumerate(images, start=1):
                    st.write(f"Страница {page_number}")
                    st.image(image, use_container_width=True)
        else:
            st.error("Паспорт с таким кодом не найден")
