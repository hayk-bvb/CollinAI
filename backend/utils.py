import logging

class Utils:
    """A class to hold few utility methods"""
    
    def __init__(self):
        pass

    def check_whitespace_or_invalid_type(self, raw_pages) -> None:

            for i, doc in enumerate(raw_pages):
                if not isinstance(doc.page_content, str):
                    print(f"[Warning] Document {i} has invalid type: {type(doc.page_content)}")
                elif not doc.page_content.strip():
                    print(f"[Warning] Document {i} is empty or whitespace only")

    def clean_pages(self, raw_pages):
        res = []
        for page in raw_pages:
            if isinstance(page.page_content, str) and page.page_content:
                page.page_content = page.page_content.strip()
                res.append(page)
            else:
                print(f"Skipping invalid page: {page.metadata.get('page')} (bad content)")
        
        return res
    


class MaxLengthFormatter(logging.Formatter):
    def __init__(self, max_length=120):
        super().__init__()
        self.max_length = max_length

    def format(self, record):
        msg = super().format(record)
        if len(msg) > self.max_length:
            lines = []
            while len(msg) > self.max_length:
                lines.append(msg[:self.max_length])
                msg = msg[self.max_length:]
            lines.append(msg)
            return '\n'.join(lines)
        else:
            return msg

