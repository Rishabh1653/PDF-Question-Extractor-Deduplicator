import os
import fitz  # PyMuPDF
import cv2
import numpy as np
import hashlib

def extract_clean_questions_only(input_folder, output_pdf_path):
    pdf_files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]
    total_files = len(pdf_files)
    
    print(f"Found {total_files} PDF files. Filtering out solved duplicate slides...\n")
    
    if total_files == 0:
        print("No PDF files found in the 'my_pdfs' folder!")
        return

    unique_pages = []
    seen_image_hashes = set()
    question_count = 0
    solved_skipped_count = 0

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
            
            # 1. Render page as an image
            pix = page.get_pixmap(dpi=150)
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
            h, w, _ = img.shape
            
            # 2. Check Top-Left Zone for the Question Banner
            top_left_crop = img[0:int(h * 0.18), 0:int(w * 0.30)]
            hsv_banner = cv2.cvtColor(top_left_crop, cv2.COLOR_RGB2HSV)
            
            red_mask_banner = (
                cv2.inRange(hsv_banner, np.array([0, 40, 30]), np.array([12, 255, 255])) | 
                cv2.inRange(hsv_banner, np.array([168, 40, 30]), np.array([180, 255, 255]))
            )
            
            contours, _ = cv2.findContours(red_mask_banner, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            is_question_banner = False
            for cnt in contours:
                if cv2.contourArea(cnt) > 300:
                    bx, by, bw, bh = cv2.boundingRect(cnt)
                    width_pct = bw / (w * 0.30)
                    if 0.10 <= width_pct <= 0.28:
                        is_question_banner = True
                        break
            
            if not is_question_banner:
                continue # Skip if it's not a question slide at all

            # 3. SOLUTION / HANDWRITING CHECK:
            # Look at the middle/bottom body area of the slide where solutions/handwriting are written
            body_crop = img[int(h * 0.20):int(h * 0.95), int(w * 0.05):int(w * 0.95)]
            hsv_body = cv2.cvtColor(body_crop, cv2.COLOR_RGB2HSV)
            
            # Target typical instructor handwriting ink colors (Green, Pink/Magenta, Bright Cyan)
            # Green ink range
            green_mask = cv2.inRange(hsv_body, np.array([35, 50, 50]), np.array([85, 255, 255]))
            # Pink/Magenta ink range
            pink_mask = cv2.inRange(hsv_body, np.array([140, 50, 50]), np.array([175, 255, 255]))
            
            handwriting_pixels = cv2.countNonZero(green_mask | pink_mask)
            
            # If there's a significant amount of handwriting pixels in the body, it's a solved page!
            # We skip it so we only keep the clean, unsolved question page.
            if handwriting_pixels > 350:
                solved_skipped_count += 1
                continue

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
    print(f"Clean question slides found: {question_count}")
    print(f"Solved duplicate pages filtered out: {solved_skipped_count}")
    print(f"Unique final questions: {len(unique_pages)}")

    if len(unique_pages) == 0:
        print("Warning: No clean question slides found.")
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
    extract_clean_questions_only(folder_path, output_file)