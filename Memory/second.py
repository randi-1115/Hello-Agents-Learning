def _split_paragraphs_with_headings(text:str) -> List[Dict]:
    """"根据标题层次分割段落，保持语义完整性"""
    lines = text.splitlines()
    heading_stack:List[str] = []
    paragraphs:List[Dict] = []
    buf:List[str] = []
    char_pos = 0

    def flush_buf(end_pos:int):
        if not buf:
            return
        paragraphs.append({
            "content": "\n".join(buf),
            "heading_path":" > ".join(heading_stack) if heading_stack else None,
        "start":max(0,end_pos - len(content)),
        "end":end_pos,
    })

    for ln in lines:
        raw = ln
        if raw.strip().startswith("#"):
            flush_buf(char_pos)
            level = len(raw) - len(raw.lstrip('#'))
            title = raw.lstrip('#').strip()

            if level <= 0:
                level = 1
            if level <= len(heading_stack):
                heading_stack = heading_stack[:level-1]
            heading_stack.append(title)

            char_pos += len(raw) +1
            continue
        if raw.strip() == "":
            flush_buf(char_pos)
            buf = []
        else:
            buf.append(raw)
        char_pos += len(raw)+1

    flush_buf(char_pos)

    if not paragraphs:
        paragraphs = [{"content":text,"heading_path":None,"start":0,"ens":len(text)}]

    return paragraphs

def _chunk_paragraphs(paragraphs:List[Dict],chunk_token:int,overlap_tokens:int) -> List[Dict]:

    """基于Token数量的智能分块"""
    chunks:List[Dict] = []
    cur: List[Dict] = []
    cur_tokens = 0
    i=0

    while i<len(paragraphs):
        p =paragraphs[i]
        p_tokens = _approx_token_len(p["content"]) or 1

        if cur_tokens + p_tokens <= chunk_tokens or not cur:
            cur.append(p)
            cur_tokens += p_tokens
            i+=1
        else:
            content = "\n\n".join(x["content"] for x in cur)
            start = cur[0]["start"]
            end = cur[-1]["end"]
            heading_path = next((x["heading_path"] for x in reversed(cur) if x.get("heading_path")),None)

            chunks.append({
                "content":content,
                "start":start,
                "end":end,
                "heading_path":heading_path,
            })

            if overlap_tokens>0 and cur:
                kept:List[dict] = []
                kept_tokens = 0
                for x in reversed(cur):
                    t=_approx_token_len(x["content"]) or 1
                    if kept_tokens + t > overlap_tokens:
                        break
                    kept.append(x)
                    kept_tokens += t

                cur = list(reversed(kept))
                cur_tokens = kept_tokens
            else:
                cur = []
                cur_tokens = 0

            if cur:
                content = "\n\n".join(x["content"] for x in cur)
                start = cur[0]["start"]
                end = cur[-1]["end"]
                heading_path = next((x["heading_path"] for x in reversed(cur) if x.get("heading_path")),None)
                
                chunks.append({
                    "content":content,
                    "start":start,
                    "end":end,
                    "heading_path":heading_path,
                })

            return chunks


def search_vectors_expanded(
        store =None,
        query:str="",
        top_k:int=8,
        rag_namespace : Optional[str] = None,
        only_rag_data:bool=True,
        score_threshold: Optional[float] = None,
        enable_mqe: bool = False,
        mqe_expansions:int = 2,
        enable_hyde:bool = False,
        candidate_pool_multiplier: int = 4,
) -> List[Dict]:
    if not query:
        return []

    if store is None:
        store = _create_default_vector_store()

    expansions: List[str] = [query]
    if enable_mqe and mqe_expansions > 0:
        expansions.extend(_prompt_mqe(query,mqe_expansions))

    if enable_hyde:
        hyde_text = _prompt_hyde(query)
        if hyde_text:
            expansions.append(hyde_text)

    uniq: List[str] = []
    for e in expansions:
        if e and e not in uniq:
            uniq.append(e)
    expansions = uniq[:max(1,len(uniq))]

    pool = max(top_k * candidate_pool_multiplier,20)
    per = max(1,pool // max(1,len(expansions)))

    where = {"memory_type":"rag_chunk"}
    if only_rag_data:
        where["is_rag_data"] = True
        where["data_source"] = "rag_pipeline"
    if rag_namespace:
        where["rag_namespace"] = rag_namespace

    agg:Dict[str,Dict] = {} 
    for q in expansions:
        qv = embed_query(q)
        hits = store.search_similer(
            query_vector = qv,
            limit = per,
            score_threshold = score_threshold,
            where = where
        )
        for h in hits:
            mid = h.get("metadata",{}).get("memory_id",h.get("id"))
            s=float(h.get("score",0.0))
            if mid not in agg or s>float(agg[mid].get("score",0.0)):
                agg[mid] = h

    merged = list(agg.values())
    merged.sort(key=lambda x:float(x.get("score",0.0)),reverse=True)
    return merged[:top_k]
                
            

            






    

