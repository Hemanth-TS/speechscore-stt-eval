"""Score synthetic or user-supplied transcript pairs; no STT provider is invoked."""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import re
import unicodedata

def normalize(text):
    text = unicodedata.normalize('NFKC', text).casefold()
    return ' '.join(''.join(c if c.isalnum() or c.isspace() else ' ' for c in text).split())

def align(reference, hypothesis):
    """Levenshtein alignment, preferring substitution then deletion on ties."""
    n, m = len(reference), len(hypothesis)
    if (n+1)*(m+1) > 2_000_000:
        raise ValueError('alignment too large; split long recordings into segments')
    dp = [[0]*(m+1) for _ in range(n+1)]
    for i in range(n+1): dp[i][0] = i
    for j in range(m+1): dp[0][j] = j
    for i in range(1,n+1):
        for j in range(1,m+1):
            dp[i][j] = min(dp[i-1][j]+1, dp[i][j-1]+1,
                           dp[i-1][j-1]+(reference[i-1]!=hypothesis[j-1]))
    out = []
    i, j = n, m
    while i or j:
        if i and j and dp[i][j] == dp[i-1][j-1]+(reference[i-1]!=hypothesis[j-1]):
            out.append({'op':'equal' if reference[i-1]==hypothesis[j-1] else 'substitute',
                        'reference':reference[i-1], 'hypothesis':hypothesis[j-1]})
            i, j = i-1,j-1
        elif i and dp[i][j] == dp[i-1][j]+1:
            out.append({'op':'delete','reference':reference[i-1],'hypothesis':None})
            i -= 1
        else:
            out.append({'op':'insert','reference':None,'hypothesis':hypothesis[j-1]})
            j -= 1
    return list(reversed(out))

def percentile(values, q):
    if not values: return None
    values = sorted(values)
    return values[max(0, math.ceil(len(values)*q)-1)]

def summarize(rows):
    words = sum(x['reference_words'] for x in rows)
    chars = sum(x['reference_chars'] for x in rows)
    errors = sum(x['word_errors'] for x in rows)
    char_errors = sum(x['char_errors'] for x in rows)
    latencies = [x['latency_ms'] for x in rows if x['latency_ms'] is not None]
    return dict(segments=len(rows), reference_words=words, word_errors=errors,
                wer=errors/words if words else None,
                cer=char_errors/chars if chars else None,
                latency_p50_ms=percentile(latencies,.5), latency_p95_ms=percentile(latencies,.95))

def evaluate(records):
    rows, seen = [], set()
    for record in records:
        ident = record['id']
        if not isinstance(ident,str) or not ident or ident in seen:
            raise ValueError('IDs must be nonempty unique strings')
        seen.add(ident)
        ref, hyp = normalize(record['reference']), normalize(record['hypothesis'])
        alignment = align(ref.split(), hyp.split())
        char_alignment = align(list(ref.replace(' ','')), list(hyp.replace(' ','')))
        latency = record.get('latency_ms')
        if latency is not None and (not isinstance(latency,(int,float)) or isinstance(latency,bool) or not math.isfinite(latency) or latency<0):
            raise ValueError('latency_ms must be a finite nonnegative number')
        rows.append(dict(id=ident,language=record.get('language','unknown'),
            reference_words=len(ref.split()),reference_chars=len(ref.replace(' ','')),
            word_errors=sum(x['op']!='equal' for x in alignment),
            char_errors=sum(x['op']!='equal' for x in char_alignment),
            latency_ms=latency,alignment=alignment))
    groups = defaultdict(list)
    for row in rows: groups[row['language']].append(row)
    return dict(overall=summarize(rows),by_language={k:summarize(v) for k,v in sorted(groups.items())},segments=rows)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, nargs='?', default=Path(__file__).parent/'samples/transcripts.json')
    args = parser.parse_args()
    print(json.dumps(evaluate(json.loads(args.input.read_text(encoding='utf-8'))),indent=2,ensure_ascii=False,allow_nan=False))

if __name__ == '__main__': main()
