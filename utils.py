def check_whitespace_or_invalid_type(raw_pages) -> None:

        for i, doc in enumerate(raw_pages):
            if not isinstance(doc.page_content, str):
                print(f"[Warning] Document {i} has invalid type: {type(doc.page_content)}")
            elif not doc.page_content.strip():
                print(f"[Warning] Document {i} is empty or whitespace only")

# TODO: Move this to another method or even class
# TODO: Make a test where it checks if the inputted pages is empty or whitespace only
def clean_pages(raw_pages):
     
     return [
            doc for doc in raw_pages
            if isinstance(doc.page_content, str) and doc.page_content.strip()
        ]
