from byaldi import RAGMultiModalModel
import base64, io
from PIL import Image

def index_pdf(path: str):
    print("index_pdf", path)
    RAG = RAGMultiModalModel.from_pretrained("vidore/colqwen2-v1.0", verbose=0)
    
    RAG.index(
        input_path=path,
        index_name="session_index",
        store_collection_with_index=True,
        overwrite=True
    )
    return RAG

def search_image(RAG, question: str):
    results = RAG.search(question, k=1)
    if not results or not results[0].base64:
        raise ValueError("No image found for the question.")
    image_bytes = base64.b64decode(results[0].base64)
    return Image.open(io.BytesIO(image_bytes))
