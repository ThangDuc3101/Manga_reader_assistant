#!/usr/bin/env python3
"""
Benchmark script to measure batch translation performance.

Compares:
1. Sequential translation (old method)
2. Batch translation (new method)
3. Cache performance

Metrics:
- Total time
- Time per text
- API calls made
- Cache hit rate
"""

import time
import logging
import json
from pathlib import Path
from translation_manager import TranslationManager, TranslationResult

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test data: Japanese manga text samples
TEST_TEXTS = [
    "ありがとう",           # Thank you
    "こんにちは",          # Hello
    "さようなら",          # Goodbye
    "大好きです",          # I love you
    "新しい",              # New
    "美しい",              # Beautiful
    "強い",               # Strong
    "弱い",               # Weak
    "面白い",             # Interesting
    "つまらない",         # Boring
    "私は学生です",       # I am a student
    "これは本です",       # This is a book
    "猫です",             # It's a cat
    "犬です",             # It's a dog
    "今日は天気がいい",   # Weather is good today
    "明日は雨です",       # Tomorrow it will rain
    "私は日本語を学んでいます",  # I am learning Japanese
    "これはおいしいです",  # This is delicious
    "とても楽しい",       # Very fun
    "少し難しい",         # A bit difficult
]

def clear_cache():
    """Clear translation cache."""
    cache_file = Path(".translation_cache.json")
    if cache_file.exists():
        cache_file.unlink()
        logger.info("✓ Cache cleared")

def benchmark_sequential(tm: TranslationManager, texts: list, label: str) -> dict:
    """
    Benchmark sequential translation (old method).
    
    Parameters:
        tm: TranslationManager instance
        texts: List of texts to translate
        label: Test label
    
    Returns:
        dict with timing metrics
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Benchmark: {label} (Sequential)")
    logger.info(f"{'='*60}")
    
    # Get initial cache stats
    stats_before = tm.get_cache_stats()
    
    # Measure time
    start_time = time.time()
    results = tm.batch_translate(texts, src="ja", dest="vi")
    elapsed = time.time() - start_time
    
    # Get final cache stats
    stats_after = tm.get_cache_stats()
    
    # Calculate metrics
    time_per_text = elapsed / len(texts)
    api_calls = stats_after['cache_misses'] - stats_before['cache_misses']
    
    metrics = {
        'method': 'Sequential (batch_translate)',
        'label': label,
        'total_texts': len(texts),
        'total_time': round(elapsed, 2),
        'time_per_text_ms': round(time_per_text * 1000, 2),
        'api_calls': api_calls,
        'cache_hits': stats_after['cache_hits'] - stats_before['cache_hits'],
        'cache_hit_rate': round(stats_after['hit_rate'] * 100, 2),
    }
    
    logger.info(f"Results:")
    logger.info(f"  Total time:        {metrics['total_time']}s")
    logger.info(f"  Time per text:     {metrics['time_per_text_ms']}ms")
    logger.info(f"  API calls made:    {metrics['api_calls']}")
    logger.info(f"  Cache hits:        {metrics['cache_hits']}")
    logger.info(f"  Cache hit rate:    {metrics['cache_hit_rate']}%")
    
    return metrics

def benchmark_batch(tm: TranslationManager, texts: list, label: str, batch_size: int = 10) -> dict:
    """
    Benchmark batch translation (new method).
    
    Parameters:
        tm: TranslationManager instance
        texts: List of texts to translate
        label: Test label
        batch_size: Texts per batch
    
    Returns:
        dict with timing metrics
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Benchmark: {label} (Batch)")
    logger.info(f"{'='*60}")
    
    # Get initial cache stats
    stats_before = tm.get_cache_stats()
    
    # Measure time
    start_time = time.time()
    results = tm.batch_translate_grouped(texts, src="ja", dest="vi", batch_size=batch_size)
    elapsed = time.time() - start_time
    
    # Get final cache stats
    stats_after = tm.get_cache_stats()
    
    # Calculate metrics
    time_per_text = elapsed / len(texts)
    api_calls = stats_after['cache_misses'] - stats_before['cache_misses']
    expected_calls = (len(texts) + batch_size - 1) // batch_size
    
    metrics = {
        'method': f'Batch (batch_translate_grouped, size={batch_size})',
        'label': label,
        'total_texts': len(texts),
        'total_time': round(elapsed, 2),
        'time_per_text_ms': round(time_per_text * 1000, 2),
        'api_calls': api_calls,
        'expected_api_calls': expected_calls,
        'cache_hits': stats_after['cache_hits'] - stats_before['cache_hits'],
        'cache_hit_rate': round(stats_after['hit_rate'] * 100, 2),
    }
    
    logger.info(f"Results:")
    logger.info(f"  Total time:        {metrics['total_time']}s")
    logger.info(f"  Time per text:     {metrics['time_per_text_ms']}ms")
    logger.info(f"  API calls made:    {metrics['api_calls']}")
    logger.info(f"  Expected calls:    {metrics['expected_api_calls']}")
    logger.info(f"  Cache hits:        {metrics['cache_hits']}")
    logger.info(f"  Cache hit rate:    {metrics['cache_hit_rate']}%")
    
    return metrics

def run_benchmarks():
    """Run all benchmarks."""
    logger.info("=" * 60)
    logger.info("BATCH TRANSLATION BENCHMARK")
    logger.info("=" * 60)
    
    results = []
    
    # Test 1: Clean cache - Sequential vs Batch
    logger.info("\n\n" + "="*60)
    logger.info("TEST 1: Cold Cache (Sequential vs Batch)")
    logger.info("="*60)
    
    clear_cache()
    tm1 = TranslationManager()
    
    r1_seq = benchmark_sequential(tm1, TEST_TEXTS, "Cold cache - Sequential")
    results.append(r1_seq)
    
    clear_cache()
    tm2 = TranslationManager()
    
    r1_batch = benchmark_batch(tm2, TEST_TEXTS, "Cold cache - Batch")
    results.append(r1_batch)
    
    # Calculate speedup
    speedup = r1_seq['total_time'] / r1_batch['total_time']
    logger.info(f"\n✓ SPEEDUP: {speedup:.1f}x faster with batch translation")
    
    # Test 2: Warm cache - All texts cached
    logger.info("\n\n" + "="*60)
    logger.info("TEST 2: Warm Cache (All Cached)")
    logger.info("="*60)
    
    tm3 = TranslationManager()
    
    r2_seq = benchmark_sequential(tm3, TEST_TEXTS, "Warm cache - Sequential")
    results.append(r2_seq)
    
    r2_batch = benchmark_batch(tm3, TEST_TEXTS, "Warm cache - Batch")
    results.append(r2_batch)
    
    # Calculate speedup
    if r2_batch['total_time'] > 0:
        speedup2 = r2_seq['total_time'] / r2_batch['total_time']
        logger.info(f"\n✓ SPEEDUP: {speedup2:.1f}x faster with batch translation")
    
    # Test 3: Large batch
    logger.info("\n\n" + "="*60)
    logger.info("TEST 3: Large Batch (100 texts)")
    logger.info("="*60)
    
    clear_cache()
    tm4 = TranslationManager()
    
    large_texts = TEST_TEXTS * 5  # 100 texts
    
    r3_seq = benchmark_sequential(tm4, large_texts, "Large batch - Sequential")
    results.append(r3_seq)
    
    clear_cache()
    tm5 = TranslationManager()
    
    r3_batch = benchmark_batch(tm5, large_texts, "Large batch - Batch")
    results.append(r3_batch)
    
    # Calculate speedup
    speedup3 = r3_seq['total_time'] / r3_batch['total_time']
    logger.info(f"\n✓ SPEEDUP: {speedup3:.1f}x faster with batch translation")
    logger.info(f"  API reduction: {r3_seq['api_calls']} → {r3_batch['api_calls']} calls ({(1 - r3_batch['api_calls']/r3_seq['api_calls'])*100:.1f}% reduction)")
    
    # Summary
    logger.info("\n\n" + "="*60)
    logger.info("SUMMARY")
    logger.info("="*60)
    
    for r in results:
        logger.info(f"\n{r['label']} ({r['method']})")
        logger.info(f"  Time: {r['total_time']}s")
        logger.info(f"  Avg:  {r['time_per_text_ms']}ms per text")
    
    # Save results
    with open('benchmark_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"\n✓ Results saved to benchmark_results.json")

if __name__ == '__main__':
    try:
        run_benchmarks()
    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        exit(1)
