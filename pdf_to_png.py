import fitz  # PyMuPDF
from PIL import Image

def pdf_to_png(pdf_path):
    # Open the PDF
    doc = fitz.open(pdf_path)

    # Iterate through each page
    for page_num in range(len(doc)):
        # Get the page and its dimensions
        page = doc[page_num]
        pix = page.get_pixmap()

        # Scale height to 1080, maintaining aspect ratio
        scale_factor = 1080 / pix.height
        scaled_pix = page.get_pixmap(matrix=fitz.Matrix(scale_factor, scale_factor))

        # Save the image
        output_image_path = f"page_{page_num + 1}.png"
        scaled_pix.save(output_image_path)
        print(f"Saved {output_image_path}")

    # Close the PDF document
    doc.close()

# Usage example
pdf_to_png("file.pdf")
