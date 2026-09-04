import os
import fitz  # PyMuPDF
import hashlib

def extract_questions_pure_python(input_folder, output_pdf_path):
    pdf_files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]
    total_files = len(pdf_files)
    
    print(f"Found {total_files} PDF files. Scanning using pure PyMuPDF pixel analysis...\n")
    
    if total_files == 0:
        print("No PDF files found in the 'my_pdfs' folder!")
        return

    unique_pages = []
    seen_image_hashes = set()
    question_count = 0

    for i, filename in enumerate(pdf_files):
        # Live Terminal Progress Bar
        progress = (i + 1) / total_files
        bar_length = 30
        filled_len = int(bar_length * progress)
        bar = '=' * filled_len + '-' * (bar_length - filled_len)
        print(f"\rProgress: [{bar}] {int(progress * 100)}% ({i+1}/{total_files}) - {filename[:15]}...", end="", flush=True)

        file_path = os.path.join(input_folder, filename)
        doc = fitz.open(file_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # 1. Render the top 20% of the page at a fixed DPI (100) 
            # so pixel measurements remain consistent across all files
            rect = fitz.Rect(0, 0, page.rect.width, page.rect.height * 0.20)
            pix = page.get_pixmap(clip=rect, dpi=100)
            
            samples = pix.samples
            width = pix.width
            height = pix.height
            n = pix.n  # 3 for RGB
            
            red_x_coords = []
            
            # 2. Scan pixels to find the red banner coordinates
            for y in range(height):
                for x in range(width):
                    idx = (y * width + x) * n
                    r = samples[idx]
                    g = samples[idx+1]
                    b = samples[idx+2]
                    
                    # Target the dark-red / red gradient of the banner
                    if r > 120 and g < 60 and b < 60:
                        red_x_coords.append(x)
            
            if red_x_coords:
                min_x = min(red_x_coords)
                max_x = max(red_x_coords)
                banner_width = max_x - min_x
                
                # 3. Validation: Must start near the left edge AND be compact (short width)
                if min_x < width * 0.15:
                    # Question banners have a compact width (roughly 80 to 320 pixels at 100 DPI)
                    # Concept banners ("Binomial Approximation") stretch much wider (> 350 pixels)
                    if 80 <= banner_width <= 320:
                        question_count += 1
                        
                        # Full page hash for clean deduplication
                        full_pix = page.get_pixmap(dpi=72)
                        page_hash = hashlib.md5(full_pix.tobytes()).hexdigest()
                        
                        if page_hash not in seen_image_hashes:
                            seen_image_hashes.add(page_hash)
                            unique_pages.append({
                                'doc': doc,
                                'page_num': page_num
                            })

    print("\n") 
    print(f"Total question slides found: {question_count}")
    print(f"Unique questions after deduplication: {len(unique_pages)}")

    if len(unique_pages) == 0:
        print("Warning: No question slides found.")
        return

    print("Building final clean question-only PDF...")
    output_doc = fitz.open()
    for item in unique_pages:
        output_doc.insert_pdf(item['doc'], from_page=item['page_num'], to_page=item['page_num'])
        
    output_doc.save(output_pdf_path)
    output_doc.close()
    print(f"\nSUCCESS! Clean question-only PDF saved to: {output_pdf_path}")

if __name__ == "__main__":
    folder_path = "./my_pdfs"
    output_file = "./clean_unique_questions.pdf"
    extract_questions_pure_python(folder_path, output_file)
