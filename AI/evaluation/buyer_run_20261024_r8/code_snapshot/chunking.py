"""Structure-aware chunks with sentence boundaries, not claims of learned semantics.

Preserve heading paths and repeat table headers. Token/word budgets are separate:
the embedding adapter must still use its own tokenizer limit at indexing time.
"""
import hashlib
import re


def chunk_document(document, max_words=180):
    heading=[];buffer=[];chunks=[]
    def emit(text):
        if not text.strip(): return
        path=' > '.join(heading) or document.get('title') or document['source']
        body=path+'\n\n'+text.strip()
        retrieval_body='\n'.join(line for line in body.splitlines() if not line.startswith('DỮ LIỆU MÔ PHỎNG'))
        chunks.append(dict({k:v for k,v in document.items() if k!='text'},
            text=body,retrieval_text=retrieval_body,heading_path=path,section=len(chunks)+1,
            chunk_id=hashlib.sha256((document.get('document_id',document['source'])+':'+str(document.get('version',1))+':'+body).encode()).hexdigest()))
    def flush():
        if buffer: emit('\n\n'.join(buffer));buffer.clear()
    # Heading boundaries must work even when the author omitted blank lines.
    structured=re.sub(r'(?m)^(#{1,6}\s+[^\n]+)\n',r'\n\n\1\n\n',document['text'])
    for block in re.split(r'\n\s*\n',structured):
        block=block.strip()
        if not block: continue
        # Documents may omit blank lines after headings.
        lines=block.splitlines()
        while lines and re.match(r'^#{1,6}\s+',lines[0]):
            flush()
            match=re.match(r'^(#{1,6})\s+(.+)',lines.pop(0))
            depth=len(match[1]);heading=heading[:depth-1]+[match[2]]
        block='\n'.join(lines).strip()
        if not block: continue
        if len(lines)>=2 and '|' in lines[0] and re.match(r'^\s*\|?\s*:?-{2,}',lines[1]):
            flush();header=lines[:2];group=[]
            for line in lines[2:]:
                if group and len(('\n'.join(header+group+[line])).split())>max_words:
                    emit('\n'.join(header+group));group=[]
                group.append(line)
            emit('\n'.join(header+group));continue
        if len(block.split())>max_words:
            flush();group=[]
            for sentence in re.split(r'(?<=[.!?;])\s+',block):
                words=sentence.split()
                if len(words)>max_words:
                    if group: emit(' '.join(group));group=[]
                    # An unusually long sentence is bounded, without dropping words.
                    for offset in range(0,len(words),max_words): emit(' '.join(words[offset:offset+max_words]))
                elif len((' '.join(group+[sentence])).split())>max_words:
                    emit(' '.join(group));group=[sentence]
                else: group.append(sentence)
            if group: emit(' '.join(group))
        else:
            if len(('\n\n'.join(buffer+[block])).split())>max_words: flush()
            buffer.append(block)
    flush()
    return chunks
