# PDF Question Extractor & Deduplicator

Automatically scans image-based lecture PDFs, filters out concept slides and solved duplicate pages using color and layout analysis, and merges unique questions into a single clean PDF.

## 🚀 How to Use This Tool

# 1. Download the Project
Click the green **Code** button at the top of the repository and select **Download ZIP** (then extract it), or clone it via your terminal:
```bash
git clone [https://github.com/Rishabh1653/PDF-Question-Extractor-Deduplicator.git](https://github.com/Rishabh1653/PDF-Question-Extractor-Deduplicator.git)
cd PDF-Question-Extractor-Deduplicator

2. Install Dependencies
This tool relies on PyMuPDF, OpenCV, and NumPy for layout and pixel analysis. Install them via your terminal:

Bash
pip install PyMuPDF opencv-python numpy

3. Set Up Your Folders
Create a folder named my_pdfs in the same directory as clean.py.

Drop your image-based lecture PDFs inside the my_pdfs folder.

4. Run the Script
Execute the script in your terminal:

Bash
python clean.py
5. Get Your Clean PDF
Once finished, a brand-new file named clean_unique_questions.pdf will be generated automatically, containing only the unique, unsolved question slides with zero concept filler or handwritten duplicates!
