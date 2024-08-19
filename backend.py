import os.path
from typing import List

from PyPDF2 import PdfFileReader, PdfFileWriter


def get_new_file_name(output_file_name: str, extension: str = '.pdf'):
    _path = output_file_name + extension
    if not os.path.exists(_path):
        return _path

    i = 1
    while True:
        _path = output_file_name + f' ({i})' + extension
        if not os.path.exists(_path):
            return _path
        i += 1


def split_pdf(input_file_path: str, output_dir_path: str, output_filename: str,
              reverse_on_even: bool = True, add_blank_if_needed: bool = True, progress_func=None) -> List[str]:
    def set_progress(value):
        if progress_func and callable(progress_func):
            progress_func(value)

    set_progress(0)

    pdf_reader = PdfFileReader(input_file_path)
    pdf_odd_writer = PdfFileWriter()
    pdf_even_writer = PdfFileWriter()
    file_names: List[str] = []

    _range = range(pdf_reader.getNumPages())
    odd_range = _range[::2]
    even_range = _range[1::2]
    if reverse_on_even:
        even_range = even_range[::-1]

    set_progress(20)

    for i in odd_range:
        pdf_odd_writer.addPage(pdf_reader.getPage(i))

    print(reverse_on_even)
    set_progress(30)

    for i in even_range:
        pdf_even_writer.addPage(pdf_reader.getPage(i))

    set_progress(40)
    print(reverse_on_even)

    odd_filename = get_new_file_name(output_file_name=f'{output_dir_path}{os.sep}{output_filename}_odd')
    with open(file=odd_filename, mode='wb') as file:
        pdf_odd_writer.write(file)
    file_names.append(odd_filename)

    set_progress(70)

    if len(_range) > 1:
        even_filename = get_new_file_name(output_file_name=f'{output_dir_path}{os.sep}{output_filename}_even')

        set_progress(75)

        if add_blank_if_needed and len(_range) % 2 == 1:
            pdf_even_writer.insertBlankPage(index=0)

        set_progress(80)

        with open(file=even_filename, mode='wb') as file:
            pdf_even_writer.write(file)
        file_names.append(even_filename)

    set_progress(100)

    return file_names
