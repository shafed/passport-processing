from io import BytesIO
from os import makedirs

from barcode import Code128
from barcode.writer import ImageWriter, SVGWriter

# TODO заглушка
count_of_passports = 1
count_of_cabs = 1
table = {"one": 1}


def generate_barcodes(count: int, prefix: str, out_dir):
    makedirs(out_dir, exist_ok=True)
    for i in range(count):
        value = f"{prefix}-{i + 1:06}"
        with open(f"{out_dir}/{value}.svg", "wb") as f:
            Code128(value, writer=SVGWriter()).write(f)

        rv = BytesIO()
        Code128(value, writer=SVGWriter()).write(rv)


def return_barcode(value: str):
    buffer = BytesIO()
    Code128(value, writer=ImageWriter()).write(buffer)
    buffer.seek(0)
    return buffer


generate_barcodes(count_of_passports, "PAS", "barcodes/passports")
generate_barcodes(count_of_cabs, "CAB", "barcodes/cabs")


def decode_barcode(value: str):
    return table[value]
