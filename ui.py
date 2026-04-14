import io

import fitz
import pandas as pd
import streamlit as st
from PIL import Image

from make_barcode import generate_barcodes, return_barcode


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


def view_and_correct(result_of_OCR, index):
    table = pd.DataFrame(result_of_OCR)
    edited_table = st.data_editor(table, use_container_width=True, key=index)
    return edited_table


def convert_for_download(df):
    return df.to_csv().encode("utf-8")


uploaded_files = st.file_uploader(
    "Загрузите файлы", accept_multiple_files=True, type=["jpg", "jpeg", "png", "pdf"]
)
all_tables = []
if uploaded_files:
    for i, uploaded_file in enumerate(uploaded_files):
        with st.expander("Развернуть изображение"):
            if uploaded_file.type.startswith("image/"):
                st.image(uploaded_file, use_container_width=True)
            elif uploaded_file.type == "application/pdf":
                images = pdf_to_images(uploaded_file)
                for page_number, image in enumerate(images, start=1):
                    st.write(f"Страница {page_number}")
                    st.image(image, use_container_width=True)
        edited_table = view_and_correct(  # TODO использую заглушку
            [
                {
                    "serial_number": "12345",
                    "manufacturer": "ООО Завод",
                    "date": "2024-01-01",
                }
            ],
            i,
        )
        st.image(return_barcode(f"PAS-{i + 1:06}"), width=100)
        all_tables.append(edited_table)
    final_table = pd.concat(all_tables, ignore_index=True)
    csv = convert_for_download(final_table)
    st.download_button(
        label="Экспортировать таблицу как CSV",
        data=csv,
        file_name="passport.csv",
        mime="text/csv",
        icon=":material/download:",
    )
    if st.button("Сгенерировать штрихкод", type="primary"):
        generate_barcodes(len(uploaded_files), "PAS", "barcodes/passports")
        st.success("Штрихкоды сгенерированы")
