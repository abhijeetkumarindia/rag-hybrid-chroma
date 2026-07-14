from langchain_community.document_loaders import DirectoryLoader
import logging
from pathlib import Path



def load_doc(directory_path, extension=None):
    p = Path(directory_path)
    logging.debug("Loading documents from %s", p)
    if not p.exists():
        logging.warning("Directory %s does not exist; returning empty list", p)
        return []

    if extension is None:
        extension = ["pdf"]

    documents = []
    for exe in extension:
            if exe.lower() == "pdf":
                # prefer lightweight PDF text extraction that doesn't require Poppler
                pdf_paths = list(p.rglob("*.pdf"))
                for fp in pdf_paths:
                    text = None
                    # try pdfplumber first
                    try:
                        import pdfplumber

                        with pdfplumber.open(fp) as pdf:
                            pages = [page.extract_text() or "" for page in pdf.pages]
                            text = "\n\n".join(pages).strip()
                    except ModuleNotFoundError:
                        # pdfplumber not installed
                        text = None
                    except Exception:
                        logging.exception("pdfplumber failed for %s", fp)
                        text = None

                    # fallback to pypdf (PyPDF) if pdfplumber failed
                    if not text:
                        try:
                            from pypdf import PdfReader

                            reader = PdfReader(str(fp))
                            pages = []
                            for page in reader.pages:
                                try:
                                    pages.append(page.extract_text() or "")
                                except Exception:
                                    pages.append("")
                            text = "\n\n".join(pages).strip()
                        except ModuleNotFoundError:
                            text = None
                        except Exception:
                            logging.exception("pypdf failed for %s", fp)
                            text = None

                    if text:
                        LD = globals().get("LangchainDocument")
                        if LD is not None:
                            documents.append(LD(page_content=text, metadata={"source": str(fp)}))
                        else:
                            # simple fallback object with page_content attribute
                            class _Doc:
                                def __init__(self, content, src):
                                    self.page_content = content
                                    self.metadata = {"source": src}

                            documents.append(_Doc(text, str(fp)))
                    else:
                        logging.warning("Could not extract text from PDF %s with pdfplumber or pypdf; skipping (poppler may be required for images/ocr).", fp)
                continue

            # non-pdf handling: use DirectoryLoader as before
            try:
                loader = DirectoryLoader(
                    str(p),
                    glob=f"**/*.{exe}",
                    show_progress=True,
                    use_multithreading=True,
                )
                loaded = loader.load()
                documents.extend(loaded)
            except ModuleNotFoundError as mnf:
                logging.exception("Missing dependency while loading %s files: %s", exe, mnf)
                logging.error(
                    "If you're loading PDFs, install optional PDF parsers (e.g. unstructured-inference, pypdf, pdfplumber) and system deps like Poppler."
                )
                continue
            except Exception:
                logging.exception("Error loading documents with extension %s from %s", exe, p)
                # continue with other extensions / files
                continue
    print(documents ,'===')
    return documents
