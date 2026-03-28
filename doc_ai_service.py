import os
import tempfile

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from sap_business_document_processing import DoxApiClient
from sap_business_document_processing.document_information_extraction_client.constants import (
    CONTENT_TYPE_PDF, CONTENT_TYPE_PNG, CONTENT_TYPE_JPEG,
    CONTENT_TYPE_TIFF, CONTENT_TYPE_UNKNOWN,
)

HEADER_FIELDS = [
    "documentNumber", "taxId", "purchaseOrderNumber", "shippingAmount",
    "netAmount", "senderAddress", "senderName", "grossAmount", "currencyCode",
    "receiverContact", "documentDate", "taxAmount", "taxRate",
    "receiverName", "receiverAddress",
]
LINE_ITEM_FIELDS = ["description", "netAmount", "quantity", "unitPrice"]
MIME_MAP = {
    "application/pdf": CONTENT_TYPE_PDF,
    "image/png": CONTENT_TYPE_PNG,
    "image/jpeg": CONTENT_TYPE_JPEG,
    "image/jpg": CONTENT_TYPE_JPEG,
    "image/tiff": CONTENT_TYPE_TIFF,
}

def _get_client():
    url = os.getenv("DOX_URL") or os.getenv("URL")
    client_id = os.getenv("DOX_CLIENT_ID") or os.getenv("CLIENT_ID")
    client_secret = os.getenv("DOX_CLIENT_SECRET") or os.getenv("CLIENT_SECRET")
    uaa_url = os.getenv("DOX_UAADOMAIN") or os.getenv("UAADOMAIN")
    missing = [k for k, v in {"DOX_URL": url, "DOX_CLIENT_ID": client_id,
               "DOX_CLIENT_SECRET": client_secret, "DOX_UAADOMAIN": uaa_url}.items() if not v]
    if missing:
        raise ValueError(f"Missing credentials: {', '.join(missing)}")
    return DoxApiClient(url, client_id, client_secret, uaa_url)

def get_capabilities():
    return _get_client().get_capabilities()

def extract_from_file(file_stream, filename, document_type="invoice", client_id="default", rotation=0):
    client = _get_client()
    content_type = MIME_MAP.get(_guess_mime(filename), CONTENT_TYPE_UNKNOWN)
    with tempfile.NamedTemporaryFile(delete=False, suffix=_suffix(filename)) as tmp:
        tmp.write(file_stream.read())
        tmp_path = tmp.name
    try:
        return client.extract_information_from_document(
            document_path=tmp_path, client_id=client_id,
            document_type=document_type, mime_type=content_type,
            header_fields=HEADER_FIELDS, line_item_fields=LINE_ITEM_FIELDS,
        )
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

def _guess_mime(filename):
    ext = (filename or "").lower().split(".")[-1]
    return {"pdf": "application/pdf", "png": "image/png", "jpg": "image/jpeg",
            "jpeg": "image/jpeg", "tiff": "image/tiff", "tif": "image/tiff"}.get(ext, "application/octet-stream")

def _suffix(filename):
    ext = (filename or "").lower().split(".")[-1]
    return ("." + ext) if ext in ("pdf", "png", "jpg", "jpeg", "tiff", "tif") else ".pdf"
