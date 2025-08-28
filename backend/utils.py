import logging
from pprint import pprint
import textwrap

class Utils:
    """A class to hold few utility methods"""
    
    def __init__(self):
        pass

    @staticmethod
    def check_whitespace_or_invalid_type(raw_pages) -> None:

            for i, doc in enumerate(raw_pages):
                if not isinstance(doc.page_content, str):
                    print(f"[Warning] Document {i} has invalid type: {type(doc.page_content)}")
                elif not doc.page_content.strip():
                    print(f"[Warning] Document {i} is empty or whitespace only")

    @staticmethod
    def clean_pages(self, raw_pages):
        res = []
        for page in raw_pages:
            if isinstance(page.page_content, str) and page.page_content:
                page.page_content = page.page_content.strip()
                res.append(page)
            else:
                print(f"Skipping invalid page: {page.metadata.get('page')} (bad content)")

    @staticmethod
    def print_verbose(ai_response_dict) -> None:
        """This is a helper function that prints out the context fed into the LLM. This helps to understand the exact context given
        to the LLM, with which it generated an answer."""

        # assuming your dict is stored in a variable called response_dict

        for msg in ai_response_dict["messages"]:
                # 1) ToolMessage-like entry?
                msg_type = getattr(msg, "__class__", None).__name__ if not isinstance(msg, dict) else msg.get("type")

                # Access message content uniformly
                content = getattr(msg, "content", None) if not isinstance(msg, dict) else msg.get("content")

                # Case A: content is a tuple like (summary_string, [Document, ...])
                if isinstance(content, tuple) and len(content) == 2:
                    maybe_docs = content[1]
                    if isinstance(maybe_docs, (list, tuple)):
                        for i, doc in enumerate(maybe_docs, 1):
                            page_text = getattr(doc, "page_content", None) if not isinstance(doc, dict) else doc.get("page_content")
                            if isinstance(page_text, str):
                                # unescape literal "\n" to real newlines if needed
                                page_text = page_text.replace("\\n", "\n")
                                print(f"\n--- Context {i} ---\n{page_text}")

                # Case B: content is a big string that already includes sources + text
                elif isinstance(content, str):
                    # If it contains literal \n, unescape them to look nice
                    pretty = content.replace("\\n", "\n")
                    print(f"\n--- Context ---\n{pretty}")

                # Case C: some SDKs put docs in a side field
                elif isinstance(msg, dict) and "documents" in msg:
                    for i, doc in enumerate(msg["documents"], 1):
                        page_text = doc.get("page_content")
                        if isinstance(page_text, str):
                            print(f"\n--- Context {i} ---\n{page_text.replace('\\n', '\n')}")
        
        return
    


class MaxLengthFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style="%", max_length=120):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self.max_length = max_length

    def format(self, record):
        msg = super().format(record)
        # Wrap each line individually
        wrapped = []
        for line in msg.splitlines():
            # break_long_words=True handles long URLs/IDs; change if you prefer
            wrapped.extend(textwrap.wrap(line, width=self.max_length, break_long_words=True))
        return "\n".join(wrapped)

