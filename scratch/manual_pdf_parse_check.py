from pathlib import Path

import fitz

from app.services.document_parser import get_parser


pdf_path = Path("tests/fixtures/manual_sample_contract.pdf")
pdf_path.parent.mkdir(parents=True, exist_ok=True)

# Build a small legal-style sample PDF.
doc = fitz.open()
page = doc.new_page()
page.insert_text((72, 72), "MASTER SERVICES AGREEMENT", fontsize=18, fontname="helv")
page.insert_text((72, 105), "1. TERM", fontsize=13, fontname="helv")
page.insert_text((72, 125), "This Agreement starts on May 1, 2026 and continues for 12 months.", fontsize=11, fontname="helv")
page.insert_text((72, 150), "2. PAYMENT TERMS", fontsize=13, fontname="helv")
page.insert_text((72, 170), "Client will pay all undisputed invoices within 30 days.", fontsize=11, fontname="helv")
page.insert_text((72, 195), "Fee Schedule", fontsize=12, fontname="helv")
page.insert_text((72, 215), "Service | Amount", fontsize=11, fontname="cour")
page.insert_text((72, 232), "Setup   | $1,000", fontsize=11, fontname="cour")
page.insert_text((72, 249), "Support | $300/month", fontsize=11, fontname="cour")

doc.save(pdf_path)
doc.close()

parser = get_parser()
parsed = parser.parse_pdf(pdf_path.read_bytes())

print(f"PDF: {pdf_path}")
print(f"Pages: {parsed.page_count}")
print(f"Blocks: {len(parsed.blocks)}")
print(f"Tables detected: {len(parsed.tables)}")
print("\n--- Extracted text preview ---")
print(parsed.text[:1200])
