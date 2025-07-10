import streamlit as st
import asyncio
import tempfile
import os
from pyppeteer import launch
from concurrent.futures import ProcessPoolExecutor

async def html_to_pdf_async(html_path, pdf_path):
    browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
    page = await browser.newPage()
    await page.goto(f"file://{html_path}")

    total_height = await page.evaluate("document.documentElement.scrollHeight")

    await page.pdf({
        'path': pdf_path,
        'printBackground': True,
        'width': '210mm',
        'height': f"{total_height}px"
    })

    await browser.close()

def html_to_pdf_worker(html_bytes):
    import asyncio
    import tempfile
    import os
    from pyppeteer import launch

    async def html_to_pdf_async(html_path, pdf_path):
        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()
        await page.goto(f"file://{html_path}")

        total_height = await page.evaluate("document.documentElement.scrollHeight")

        await page.pdf({
            'path': pdf_path,
            'printBackground': True,
            'width': '210mm',
            'height': f"{total_height}px"
        })

        await browser.close()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as html_temp:
        html_temp.write(html_bytes)
        html_temp.flush()
        html_path = html_temp.name

    pdf_fd, pdf_path = tempfile.mkstemp(suffix=".pdf")
    os.close(pdf_fd)

    asyncio.run(html_to_pdf_async(html_path, pdf_path))

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    os.remove(html_path)
    os.remove(pdf_path)
    return pdf_bytes

def html_to_pdf(html_bytes):
    with ProcessPoolExecutor() as executor:
        future = executor.submit(html_to_pdf_worker, html_bytes)
        return future.result()

st.title("HTML to PDF Converter (Pyppeteer)")

uploaded_file = st.file_uploader("Upload an HTML file", type=["html", "htm"])
default_pdf_name = ""
if uploaded_file:
    base_name = os.path.splitext(uploaded_file.name)[0]
    default_pdf_name = base_name

pdf_name = st.text_input("Enter the name for the generated PDF (without .pdf):", value=default_pdf_name)

if uploaded_file is not None:
    if st.button("Convert to PDF"):
        with st.spinner("Converting..."):
            pdf_bytes = html_to_pdf(uploaded_file.read())
        st.success("Your PDF file is ready for download!")
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name=f"{pdf_name.strip() or 'converted'}.pdf",
            mime="application/pdf"
        )
