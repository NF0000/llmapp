import os 
import pickle
import numpy as np
import faiss
from pdfminer.high_level import extract_text
from sentence_transformers import SentenceTransformer

#モデルと保存先
model=SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
INDEX_FILE="pdf_index.pkl"
UPLOAD_DIR="uploads"

#pdf登録
def register_pdf(file_path:str):
    """
    pdfからテキストを抽出し、ベクトル化してFAISSに登録
    """
    text=extract_text(file_path)
    chunks=[text[i:i+500] for i in range(0,len(text),500)]
    embeddings=model.encode(chunks)
    
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "rb") as f:
            old_chunks,old_index = pickle.load(f)
        new_chunks=old_chunks+chunks
        old_embs=old_index.reconstruct_n(0,old_index.ntotal)
        all_embs=np.concatenate([old_embs, embeddings])
        
        index=faiss.IndexFlatL2(all_embs.shape[1])
        index.add(all_embs)
    else:
        new_chunks=chunks
        index=faiss.IndexFlatL2(embeddings.shape[1])
        index.add(np.array(embeddings))
        
    with open(INDEX_FILE,"wb") as f:
        pickle.dump((new_chunks,index),f)
        
    return len(chunks)

#疑似検索
def retrieve_context(query:str,top_k:int =3) -> str:
    """
    質問に関する文章を検索し、テキストを返す
    """
    if not os.path.exists(INDEX_FILE):
        return "まだPDFが登録されていません。"

    with open(INDEX_FILE, "rb") as f:
        chunks,index=pickle.load(f)
        
    q_emb=model.encode([query])
    D,I=index.search(np.array(q_emb),top_k)
    retrieved="\n".join([chunks[i] for i in I[0]])
    
    return retrieved