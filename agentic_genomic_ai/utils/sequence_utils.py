from __future__ import annotations

from collections import Counter
from itertools import product


def gc_content(sequence: str) -> float:
    seq = sequence.upper()
    if not seq:
        return 0.0
    gc = seq.count("G") + seq.count("C")
    return (gc / len(seq)) * 100


def nucleotide_distribution(sequence: str) -> dict[str, float]:
    seq = sequence.upper()
    if not seq:
        return {n: 0.0 for n in "ACGT"}
    c = Counter(ch for ch in seq if ch in "ACGT")
    total = sum(c.values()) or 1
    return {n: c.get(n, 0) / total for n in "ACGT"}


def kmer_frequency(sequence: str, k: int = 3) -> dict[str, float]:
    seq = sequence.upper()
    kmers = [''.join(p) for p in product('ACGT', repeat=k)]
    counts = {kmer: 0 for kmer in kmers}
    if len(seq) < k:
        return counts

    total = 0
    for i in range(len(seq) - k + 1):
        kmer = seq[i:i+k]
        if all(ch in 'ACGT' for ch in kmer):
            counts[kmer] += 1
            total += 1

    if total == 0:
        return counts
    return {k: v / total for k, v in counts.items()}
