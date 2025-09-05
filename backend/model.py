import numpy as np
import psycopg2

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, ollama_client, MODEL_NAME


conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
cursor = conn.cursor()

def summarize_chunks_hierarchical(chunk_texts, client, model_name, batch_size=10, summary_prompt=None):
    import time
    if summary_prompt is None:
        summary_prompt = "Be concise in conveying the main ideas, but don't leave out important details. " \
        "Keep as much content as possible."
    current_level = chunk_texts
    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level), batch_size):
            batch = current_level[i:i+batch_size]
            batch_text = "\n\n".join(batch)
            prompt = f"{summary_prompt}\n\n{batch_text}"
            response = client.generate(
                model=model_name,
                prompt=prompt
            )
            if hasattr(response, 'response'):
                summary = response.response
            elif isinstance(response, dict) and 'response' in response:
                summary = response['response']
            else:
                summary = str(response)
            next_level.append(summary.strip())
            time.sleep(0.5)  
        current_level = next_level
    return current_level[0] if current_level else ""

def summarize_all_chunks_from_db(client, model_name, batch_size=10, summary_prompt=None):
    cursor.execute(f"SELECT content FROM items ORDER BY id ASC")
    rows = cursor.fetchall()
    chunk_texts = [row[0] for row in rows]
    if not chunk_texts:
        return ""
    return summarize_chunks_hierarchical(chunk_texts, client, model_name, batch_size, summary_prompt)