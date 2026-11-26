"""Akademisyen benzerlik hesaplaması için performans karşılaştırma modülü."""

from collections import defaultdict
from itertools import combinations
import time

from academic_algorithms import jaccard_similarity
from university_graph import clean_fields, load_sample_data


def similarity_all_pairs(academics):
    """Yöntem A: Tüm akademisyen çiftlerini karşılaştırarak Jaccard benzerliği hesaplar."""
    records = [
        (str(academic["name"]).strip(), clean_fields(academic))
        for academic in academics
    ]
    results = {}
    comparisons = 0

    for (name_a, fields_a), (name_b, fields_b) in combinations(records, 2):
        comparisons += 1
        score = jaccard_similarity(fields_a, fields_b)
        if score > 0:
            pair = (name_a, name_b) if name_a < name_b else (name_b, name_a)
            results[pair] = score

    return results, comparisons


def similarity_inverted_index(academics):
    """Yöntem B: 'alan -> akademisyenler' sözlüğü (inverted index) ile benzerlik hesaplar."""
    names = []
    field_counts = []
    inverted_index = defaultdict(list)

    for idx, academic in enumerate(academics):
        name = str(academic["name"]).strip()
        fields = clean_fields(academic)
        names.append(name)
        field_counts.append(len(fields))
        for field in fields:
            inverted_index[field].append(idx)

    common_counts = defaultdict(int)
    for academic_indices in inverted_index.values():
        for i, j in combinations(academic_indices, 2):
            pair = (i, j) if i < j else (j, i)
            common_counts[pair] += 1

    results = {}
    for (i, j), common in common_counts.items():
        union = field_counts[i] + field_counts[j] - common
        if union > 0:
            name_a, name_b = names[i], names[j]
            pair = (name_a, name_b) if name_a < name_b else (name_b, name_a)
            results[pair] = common / union

    return results, len(common_counts)


def benchmark_similarity(academics, repeats=5):
    """İki yöntemin çalışma sürelerini time modülüyle ölçer ve özet döndürür."""
    all_pairs_times = []
    inv_index_times = []
    all_pairs_res = {}
    inv_index_res = {}
    all_pairs_cmp = 0
    inv_index_cmp = 0

    for _ in range(repeats):
        start = time.perf_counter()
        all_pairs_res, all_pairs_cmp = similarity_all_pairs(academics)
        all_pairs_times.append(time.perf_counter() - start)

        start = time.perf_counter()
        inv_index_res, inv_index_cmp = similarity_inverted_index(academics)
        inv_index_times.append(time.perf_counter() - start)

    avg_all = sum(all_pairs_times) / repeats
    avg_inv = sum(inv_index_times) / repeats
    speedup = avg_all / avg_inv if avg_inv > 0 else 0.0

    return {
        "academic_count": len(academics),
        "repeats": repeats,
        "all_pairs_avg_ms": avg_all * 1000,
        "inverted_index_avg_ms": avg_inv * 1000,
        "all_pairs_comparisons": all_pairs_cmp,
        "inverted_index_comparisons": inv_index_cmp,
        "similar_pairs_found": len(inv_index_res),
        "results_match": all_pairs_res == inv_index_res,
        "speedup": speedup,
    }


def format_benchmark_table(stats):
    """Ölçüm sonuçlarını rapor ve konsol için tablo biçiminde döndürür."""
    lines = [
        f"Akademisyen sayısı: {stats['academic_count']} (Tekrar: {stats['repeats']})",
        "-" * 74,
        f"{'Yöntem':<30} | {'Ortalama Süre (ms)':>18} | {'Karşılaştırma':>18}",
        "-" * 74,
        f"{'Tüm Çiftler ':<30} | {stats['all_pairs_avg_ms']:>18.4f} | {stats['all_pairs_comparisons']:>18}",
        f"{'Inverted Index':<30} | {stats['inverted_index_avg_ms']:>18.4f} | {stats['inverted_index_comparisons']:>18}",
        "-" * 74,
        f"Bulunan benzer çift sayısı: {stats['similar_pairs_found']} | "
        f"Sonuçlar birebir aynı mı: {'Evet' if stats['results_match'] else 'Hayır'} | "
        f"Hızlanma: {stats['speedup']:.2f}x",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    sample_data = load_sample_data()
    stats = benchmark_similarity(sample_data, repeats=20)
    print(format_benchmark_table(stats))