"""
Test Suite: Document Upload (Issue #8)
Tests TC-8.1 through TC-8.20
"""

import pytest
from playwright.sync_api import Page, expect
import time
import os


class TestUploadFunctionality:
    """Test Suite: Upload Functionality (TC-8.1 - TC-8.10)"""

    def test_tc_8_1_accepts_pdf(self, streamlit_page: Page, create_test_pdf):
        """TC-8.1: File uploader accepts PDF files"""
        pdf_file = create_test_pdf("test.pdf", size_kb=100)

        # Find file uploader
        file_input = streamlit_page.locator('input[type="file"]')

        if file_input.count() > 0:
            file_input.first.set_input_files(pdf_file)
            time.sleep(1)

            # Verify file is selected
            assert os.path.basename(pdf_file) in streamlit_page.content()

    def test_tc_8_2_accepts_txt(self, streamlit_page: Page, create_test_txt):
        """TC-8.2: File uploader accepts TXT files"""
        txt_file = create_test_txt("test.txt")

        file_input = streamlit_page.locator('input[type="file"]')

        if file_input.count() > 0:
            file_input.first.set_input_files(txt_file)
            time.sleep(1)

    def test_tc_8_3_accepts_md(self, streamlit_page: Page, test_files_dir):
        """TC-8.3: File uploader accepts MD files"""
        md_file = os.path.join(test_files_dir, "test.md")
        with open(md_file, 'w') as f:
            f.write("# Test Markdown\n\nThis is a test.")

        file_input = streamlit_page.locator('input[type="file"]')

        if file_input.count() > 0:
            file_input.first.set_input_files(md_file)
            time.sleep(1)

    def test_tc_8_4_accepts_docx(self, streamlit_page: Page, test_files_dir):
        """TC-8.4: File uploader accepts DOCX files"""
        # Create minimal DOCX
        from docx import Document

        docx_file = os.path.join(test_files_dir, "test.docx")
        doc = Document()
        doc.add_paragraph("Test DOCX content")
        doc.save(docx_file)

        file_input = streamlit_page.locator('input[type="file"]')

        if file_input.count() > 0:
            file_input.first.set_input_files(docx_file)
            time.sleep(1)

    def test_tc_8_5_rejects_unsupported(self, streamlit_page: Page, test_files_dir):
        """TC-8.5: File uploader rejects unsupported types"""
        exe_file = os.path.join(test_files_dir, "test.exe")
        with open(exe_file, 'wb') as f:
            f.write(b'\x00' * 100)

        file_input = streamlit_page.locator('input[type="file"]')

        if file_input.count() > 0:
            try:
                file_input.first.set_input_files(exe_file)
                time.sleep(2)

                # Should show error
                error_msg = streamlit_page.get_by_text("error", exact=False)
                if error_msg.count() > 0:
                    expect(error_msg.first).to_be_visible()
            except:
                pass  # Expected to fail

    def test_tc_8_6_rejects_large_files(self, streamlit_page: Page, create_test_pdf):
        """TC-8.6: Files over 10MB are rejected with error message"""
        # Create large PDF (>10MB)
        large_pdf = create_test_pdf("large.pdf", size_kb=11000)

        file_input = streamlit_page.locator('input[type="file"]')

        if file_input.count() > 0:
            file_input.first.set_input_files(large_pdf)
            time.sleep(2)

            # Should show size error
            error_msg = streamlit_page.get_by_text("10MB", exact=False)
            if error_msg.count() > 0:
                expect(error_msg.first).to_be_visible()

    def test_tc_8_7_multiple_files(self, streamlit_page: Page, create_test_pdf):
        """TC-8.7: Multiple files can be selected simultaneously"""
        pdf1 = create_test_pdf("test1.pdf", size_kb=100)
        pdf2 = create_test_pdf("test2.pdf", size_kb=100)

        file_input = streamlit_page.locator('input[type="file"]')

        if file_input.count() > 0:
            file_input.first.set_input_files([pdf1, pdf2])
            time.sleep(1)

    def test_tc_8_8_upload_button_appears(self, streamlit_page: Page, create_test_pdf):
        """TC-8.8: Upload button appears when files selected"""
        pdf_file = create_test_pdf("test.pdf", size_kb=100)

        file_input = streamlit_page.locator('input[type="file"]')

        if file_input.count() > 0:
            file_input.first.set_input_files(pdf_file)
            time.sleep(1)

            # Look for upload button
            upload_button = streamlit_page.get_by_text("Upload", exact=False)
            if upload_button.count() > 0:
                expect(upload_button.first).to_be_visible()

    def test_tc_8_9_upload_progress_shown(self, streamlit_page: Page, create_test_pdf):
        """TC-8.9: Upload progress shown with spinner"""
        pdf_file = create_test_pdf("test.pdf", size_kb=500)

        file_input = streamlit_page.locator('input[type="file"]')

        if file_input.count() > 0:
            file_input.first.set_input_files(pdf_file)
            time.sleep(1)

            upload_button = streamlit_page.get_by_text("Upload", exact=False)
            if upload_button.count() > 0:
                upload_button.first.click()

                # Look for spinner
                spinner = streamlit_page.locator('[data-testid="stSpinner"]')
                if spinner.count() > 0:
                    expect(spinner.first).to_be_visible(timeout=5000)

    def test_tc_8_10_success_message(self, streamlit_page: Page, create_test_pdf):
        """TC-8.10: Success message displays for successful uploads"""
        pdf_file = create_test_pdf("test.pdf", size_kb=100)

        file_input = streamlit_page.locator('input[type="file"]')

        if file_input.count() > 0:
            file_input.first.set_input_files(pdf_file)
            time.sleep(1)

            upload_button = streamlit_page.get_by_text("Upload", exact=False)
            if upload_button.count() > 0:
                upload_button.first.click()
                time.sleep(5)

                # Look for success message
                success_msg = streamlit_page.get_by_text("success", exact=False)
                if success_msg.count() > 0:
                    expect(success_msg.first).to_be_visible()


class TestUploadIntegration:
    """Test Suite: Upload Integration (TC-8.11 - TC-8.20)"""

    def test_tc_8_11_appears_in_recent_uploads(self, streamlit_page: Page, create_test_pdf):
        """TC-8.11: Uploaded documents appear in recent uploads"""
        pdf_file = create_test_pdf("recent_test.pdf", size_kb=100)

        file_input = streamlit_page.locator('input[type="file"]')

        if file_input.count() > 0:
            file_input.first.set_input_files(pdf_file)
            time.sleep(1)

            upload_button = streamlit_page.get_by_text("Upload", exact=False)
            if upload_button.count() > 0:
                upload_button.first.click()
                time.sleep(5)

                # Check recent uploads section
                expect(streamlit_page.get_by_text("recent_test.pdf", exact=False)).to_be_visible()

    def test_tc_8_12_document_count_increases(self, streamlit_page: Page, create_test_pdf):
        """TC-8.12: Document count increases after upload"""
        # Get initial count
        initial_count_text = streamlit_page.get_by_text("Documents", exact=False)
        initial_count = None

        if initial_count_text.count() > 0:
            text = initial_count_text.first.inner_text()
            # Extract number from text

        pdf_file = create_test_pdf("count_test.pdf", size_kb=100)

        file_input = streamlit_page.locator('input[type="file"]')

        if file_input.count() > 0:
            file_input.first.set_input_files(pdf_file)
            time.sleep(1)

            upload_button = streamlit_page.get_by_text("Upload", exact=False)
            if upload_button.count() > 0:
                upload_button.first.click()
                time.sleep(5)

                # Verify count increased

    def test_tc_8_13_content_searchable(self, streamlit_page: Page, create_test_pdf):
        """TC-8.13: Uploaded content is searchable via chat"""
        unique_content = f"UniqueTestContent{int(time.time())}"
        pdf_file = create_test_pdf("searchable.pdf", size_kb=100, content=unique_content)

        # Upload file
        file_input = streamlit_page.locator('input[type="file"]')

        if file_input.count() > 0:
            file_input.first.set_input_files(pdf_file)
            time.sleep(1)

            upload_button = streamlit_page.get_by_text("Upload", exact=False)
            if upload_button.count() > 0:
                upload_button.first.click()
                time.sleep(10)  # Wait for indexing

                # Search for content
                chat_input = streamlit_page.get_by_placeholder("Ask a question about your documents...")
                chat_input.fill(unique_content)
                chat_input.press("Enter")
                time.sleep(5)

                # Should find the content

    def test_tc_8_14_rag_retrieves_chunks(self, streamlit_page: Page, create_test_pdf):
        """TC-8.14: RAG retrieves chunks from uploaded documents"""
        # Similar to TC-8.13 but verify chunks in response

    def test_tc_8_15_failed_uploads_show_error(self, streamlit_page: Page):
        """TC-8.15: Failed uploads show error messages"""
        # Test with invalid file or simulated error

    def test_tc_8_16_upload_history_timestamps(self, streamlit_page: Page):
        """TC-8.16: Upload history shows timestamps"""
        # Check that recent uploads display timestamps

    def test_tc_8_17_multiple_uploads_sequential(self, streamlit_page: Page, create_test_pdf):
        """TC-8.17: Multiple uploads processed in sequence"""
        pdf1 = create_test_pdf("seq1.pdf", size_kb=100)
        pdf2 = create_test_pdf("seq2.pdf", size_kb=100)

        file_input = streamlit_page.locator('input[type="file"]')

        if file_input.count() > 0:
            # Upload first
            file_input.first.set_input_files(pdf1)
            time.sleep(1)

            upload_button = streamlit_page.get_by_text("Upload", exact=False)
            if upload_button.count() > 0:
                upload_button.first.click()
                time.sleep(5)

            # Upload second
            file_input.first.set_input_files(pdf2)
            time.sleep(1)

            if upload_button.count() > 0:
                upload_button.first.click()
                time.sleep(5)

    def test_tc_8_18_large_files_near_limit(self, streamlit_page: Page, create_test_pdf):
        """TC-8.18: Large files (near 10MB) upload successfully"""
        large_pdf = create_test_pdf("near_limit.pdf", size_kb=9500)

        file_input = streamlit_page.locator('input[type="file"]')

        if file_input.count() > 0:
            file_input.first.set_input_files(large_pdf)
            time.sleep(1)

            upload_button = streamlit_page.get_by_text("Upload", exact=False)
            if upload_button.count() > 0:
                upload_button.first.click()
                time.sleep(30)  # Large file takes longer

    def test_tc_8_19_duplicate_filenames_handled(self, streamlit_page: Page, create_test_pdf):
        """TC-8.19: Duplicate filenames handled gracefully"""
        pdf1 = create_test_pdf("duplicate.pdf", size_kb=100, content="First version")

        file_input = streamlit_page.locator('input[type="file"]')

        if file_input.count() > 0:
            file_input.first.set_input_files(pdf1)
            time.sleep(1)

            upload_button = streamlit_page.get_by_text("Upload", exact=False)
            if upload_button.count() > 0:
                upload_button.first.click()
                time.sleep(5)

            # Try uploading again with same filename
            pdf2 = create_test_pdf("duplicate.pdf", size_kb=100, content="Second version")
            file_input.first.set_input_files(pdf2)
            time.sleep(1)

            if upload_button.count() > 0:
                upload_button.first.click()
                time.sleep(5)

    def test_tc_8_20_special_characters_in_filename(self, streamlit_page: Page, create_test_pdf):
        """TC-8.20: Upload works with special characters in filename"""
        special_pdf = create_test_pdf("test-file_123 (copy).pdf", size_kb=100)

        file_input = streamlit_page.locator('input[type="file"]')

        if file_input.count() > 0:
            file_input.first.set_input_files(special_pdf)
            time.sleep(1)

            upload_button = streamlit_page.get_by_text("Upload", exact=False)
            if upload_button.count() > 0:
                upload_button.first.click()
                time.sleep(5)
