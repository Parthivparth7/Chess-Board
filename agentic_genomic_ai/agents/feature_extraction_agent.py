from __future__ import annotations

import logging
from statistics import mean

from agentic_genomic_ai.utils.sequence_utils import kmer_frequency, nucleotide_distribution

logger = logging.getLogger(__name__)


class FeatureExtractionAgent:
    def run(self, ingested: dict) -> dict:
        records = ingested["records"]
        if not records:
            return {"kmer_features": {}, "nucleotide_distribution": {}, "feature_vector": []}

        kmer_accum: dict[str, list[float]] = {}
        nt_accum = {"A": [], "C": [], "G": [], "T": []}

        for rec in records:
            kf = kmer_frequency(rec["sequence"], k=3)
            for k, v in kf.items():
                kmer_accum.setdefault(k, []).append(v)
            nd = nucleotide_distribution(rec["sequence"])
            for n, v in nd.items():
                nt_accum[n].append(v)

        mean_kmers = {k: mean(vs) for k, vs in kmer_accum.items()}
        mean_nt = {k: mean(vs) if vs else 0.0 for k, vs in nt_accum.items()}

        feature_vector = [mean_kmers[k] for k in sorted(mean_kmers.keys())]
        feature_vector.extend([mean_nt[n] for n in "ACGT"])

        logger.info("FeatureExtractionAgent built vector length=%d", len(feature_vector))
        return {
            "kmer_features": mean_kmers,
            "nucleotide_distribution": mean_nt,
            "feature_vector": feature_vector,
        }
