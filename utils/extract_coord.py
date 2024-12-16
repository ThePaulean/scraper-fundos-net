import os

import pandas as pd
from pdfminer.pdfparser import PDFSyntaxError
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage


def extract_text_in_page(page: PDFPage, laparams=None):
    # Create a PDF resource manager object
    resource_manager = PDFResourceManager()

    # Create a PDF device object
    if not laparams:
        laparams = LAParams(char_margin=1.0)
    device = PDFPageAggregator(resource_manager, laparams=laparams)

    # Create a PDF interpreter object
    interpreter = PDFPageInterpreter(resource_manager, device)

    # Process each page contained in the document
    interpreter.process_page(page)
    layout = device.get_result()
    text_coordinates = []
    y_offset = 0
    for element in layout:
        if isinstance(element, LTTextBox) or isinstance(element, LTTextLine):
            bbox = element.bbox
            text_coordinates.append(
                [
                    element.get_text(),
                    bbox[0],
                    bbox[2],
                    bbox[1] + y_offset,
                    bbox[3] + y_offset,
                ]
            )
    df_coord = pd.DataFrame(text_coordinates, columns=["text", "xi", "xf", "yi", "yf"])
    return df_coord


def extract_text_with_coordinates(pdf_path, pages: list[int] = [], laparams=None):
    # Open the PDF file
    with open(pdf_path, "rb") as file:
        try:
            # Create a PDF file parser object associated with the file object
            parser = PDFPage.get_pages(file)

            # Create a list of dataframes containing the text and coordinates of each page
            df_list = []
            for page_num, page in enumerate(parser, start=1):
                if (pages) and (page_num not in pages):
                    continue
                df_coord = extract_text_in_page(page, laparams=laparams)
                df_coord["page"] = page_num
                df_list.append(df_coord)
            return df_list
        except PDFSyntaxError:
            print(f"Error: {pdf_path} is not a valid PDF file")
