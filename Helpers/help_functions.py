def dedupe_ranked_chunks(results):
    """
    results: list of (Document, score)
    Keeps the best (lowest score) instance of each chunk_id.
    """
    seen = {}
    
    for doc, score in results:
        chunk_id = doc.metadata.get("chunk_id")
        if not chunk_id:
            continue

        # Keep the best (lowest) score per chunk_id
        if chunk_id not in seen or score < seen[chunk_id][1]:
            seen[chunk_id] = (doc, score)

    # Return sorted, deduped results
    return sorted(seen.values(), key=lambda x: x[1])
