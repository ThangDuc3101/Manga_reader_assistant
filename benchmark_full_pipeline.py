"""
Task 2.4: Full Pipeline Performance Profiling & Optimization

This script profiles the entire manga reader pipeline:
- Image preprocessing & resizing
- YOLO detection (different image sizes)
- OCR text recognition
- Batch translation
- Image rendering

Measures:
- Time per component
- Memory usage
- Cache hit rates
- Optimization opportunities

Output: benchmark_results_full_pipeline.json + performance_report.txt
"""

import json
import logging
import time
import tracemalloc
from pathlib import Path
from typing import Dict, List, Tuple
from PIL import Image
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PerformanceProfiler:
    """Profile pipeline performance across different scenarios."""
    
    def __init__(self):
        self.results = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'components': {},
            'image_sizes': {},
            'batch_sizes': {},
            'recommendations': []
        }
        self.test_results = []
        
    def create_test_image(self, width: int, height: int, name: str = None) -> Image.Image:
        """Create a test manga-like image for benchmarking."""
        try:
            # Create white background with black text regions
            img = Image.new('RGB', (width, height), color='white')
            pixels = img.load()
            
            # Add some "text" boxes (black regions)
            num_boxes = max(1, (width * height) // 50000)
            for _ in range(num_boxes):
                x = np.random.randint(0, max(width - 100, 100))
                y = np.random.randint(0, max(height - 100, 100))
                w = np.random.randint(50, min(200, width - x))
                h = np.random.randint(30, min(150, height - y))
                
                # Draw black box
                for px in range(x, min(x + w, width)):
                    for py in range(y, min(y + h, height)):
                        pixels[px, py] = (0, 0, 0)
            
            if name:
                logger.info(f"Created test image: {name} ({width}x{height})")
            return img
        except Exception as e:
            logger.error(f"Failed to create test image: {e}")
            return None
    
    def benchmark_image_preprocessing(self) -> Dict:
        """Benchmark image loading and preprocessing."""
        logger.info("\n=== BENCHMARKING IMAGE PREPROCESSING ===")
        results = {}
        
        test_sizes = [
            (480, 640),    # Small
            (768, 1024),   # Medium
            (1200, 1600),  # Large
            (2000, 2667),  # Extra large
        ]
        
        for width, height in test_sizes:
            size_key = f"{width}x{height}"
            logger.info(f"Testing {size_key}...")
            
            timings = []
            memory_usage = []
            
            for _ in range(3):
                # Create image
                img = self.create_test_image(width, height)
                
                # Measure preprocessing time
                tracemalloc.start()
                start_time = time.time()
                
                # Simulate preprocessing: convert to RGB, resize if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Optional: resize for YOLO (640x640 is standard)
                aspect = width / height
                if width > 640:
                    new_width = 640
                    new_height = int(640 / aspect)
                    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                elapsed = time.time() - start_time
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                
                timings.append(elapsed * 1000)  # Convert to ms
                memory_usage.append(peak / 1024 / 1024)  # Convert to MB
            
            results[size_key] = {
                'time_ms': {
                    'mean': np.mean(timings),
                    'std': np.std(timings),
                    'min': np.min(timings),
                    'max': np.max(timings),
                },
                'memory_mb': {
                    'mean': np.mean(memory_usage),
                    'peak': np.max(memory_usage),
                }
            }
            
            logger.info(f"  Time: {np.mean(timings):.2f}ms ± {np.std(timings):.2f}ms")
            logger.info(f"  Memory: {np.mean(memory_usage):.2f}MB (peak: {np.max(memory_usage):.2f}MB)")
        
        self.results['image_preprocessing'] = results
        return results
    
    def benchmark_model_loading(self) -> Dict:
        """Benchmark YOLO model loading and warm-up."""
        logger.info("\n=== BENCHMARKING MODEL LOADING ===")
        
        try:
            from ultralytics import YOLO
            
            results = {}
            
            # First load (cold)
            logger.info("Loading YOLO model (cold cache)...")
            tracemalloc.start()
            start_time = time.time()
            
            model = YOLO('yolov8s.pt')
            
            cold_time = time.time() - start_time
            _, peak_memory = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            results['cold_load'] = {
                'time_s': cold_time,
                'memory_mb': peak_memory / 1024 / 1024
            }
            
            logger.info(f"Cold load: {cold_time:.2f}s, Memory: {peak_memory/1024/1024:.2f}MB")
            
            # Test image inference timing
            logger.info("Warming up model with inference...")
            test_img = self.create_test_image(640, 480)
            
            # Warm-up run
            _ = model(test_img, verbose=False)
            
            # Actual benchmark (3 runs)
            inference_times = []
            for i in range(3):
                start = time.time()
                _ = model(test_img, verbose=False)
                inference_times.append(time.time() - start)
            
            results['inference'] = {
                'time_s': {
                    'mean': np.mean(inference_times),
                    'std': np.std(inference_times),
                    'min': np.min(inference_times),
                    'max': np.max(inference_times),
                }
            }
            
            logger.info(f"Inference: {np.mean(inference_times):.2f}s ± {np.std(inference_times):.2f}s")
            
            self.results['model_loading'] = results
            return results
            
        except Exception as e:
            logger.error(f"Model loading benchmark failed: {e}")
            return {'error': str(e)}
    
    def benchmark_ocr_recognition(self) -> Dict:
        """Benchmark OCR text recognition."""
        logger.info("\n=== BENCHMARKING OCR RECOGNITION ===")
        
        try:
            from manga_ocr import MangaOcr
            
            results = {}
            
            # Initialize OCR
            logger.info("Loading OCR model...")
            start = time.time()
            ocr = MangaOcr()
            init_time = time.time() - start
            
            results['initialization'] = {'time_s': init_time}
            logger.info(f"OCR initialization: {init_time:.2f}s")
            
            # Benchmark text recognition on different box sizes
            box_sizes = [
                (100, 50),   # Small
                (300, 150),  # Medium
                (600, 300),  # Large
            ]
            
            recognition_times = {}
            
            for width, height in box_sizes:
                size_key = f"{width}x{height}"
                logger.info(f"Testing OCR on {size_key} boxes...")
                
                timings = []
                for _ in range(3):
                    # Create test image with "text"
                    test_img = self.create_test_image(width, height)
                    
                    tracemalloc.start()
                    start = time.time()
                    
                    text = ocr(test_img)
                    
                    elapsed = time.time() - start
                    _, peak_mem = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    
                    timings.append(elapsed * 1000)
                
                recognition_times[size_key] = {
                    'time_ms': {
                        'mean': np.mean(timings),
                        'std': np.std(timings),
                    }
                }
                
                logger.info(f"  {size_key}: {np.mean(timings):.2f}ms ± {np.std(timings):.2f}ms")
            
            results['recognition'] = recognition_times
            self.results['ocr_recognition'] = results
            return results
            
        except Exception as e:
            logger.error(f"OCR benchmark failed: {e}")
            return {'error': str(e)}
    
    def benchmark_translation_cache(self) -> Dict:
        """Benchmark translation cache performance."""
        logger.info("\n=== BENCHMARKING TRANSLATION CACHE ===")
        
        try:
            from translation_manager import TranslationManager
            
            results = {}
            tm = TranslationManager()
            
            # Test texts
            test_texts = [
                "ありがとう",
                "こんにちは",
                "さようなら",
                "すみません",
                "おはよう",
            ]
            
            # Benchmark 1: Cache misses (cold)
            logger.info("Benchmark 1: Cold cache (all cache misses)...")
            timings_cold = []
            
            for text in test_texts:
                start = time.time()
                result = tm.translate(text, src="ja", dest="vi")
                elapsed = time.time() - start
                timings_cold.append(elapsed * 1000)
            
            results['cold_cache'] = {
                'time_ms': {
                    'mean': np.mean(timings_cold),
                    'std': np.std(timings_cold),
                    'total': np.sum(timings_cold),
                }
            }
            logger.info(f"Cold cache: {np.mean(timings_cold):.2f}ms per text")
            
            # Benchmark 2: Cache hits (warm)
            logger.info("Benchmark 2: Warm cache (all cache hits)...")
            timings_warm = []
            
            for text in test_texts:
                start = time.time()
                result = tm.translate(text, src="ja", dest="vi")
                elapsed = time.time() - start
                timings_warm.append(elapsed * 1000)
            
            results['warm_cache'] = {
                'time_ms': {
                    'mean': np.mean(timings_warm),
                    'std': np.std(timings_warm),
                    'total': np.sum(timings_warm),
                }
            }
            logger.info(f"Warm cache: {np.mean(timings_warm):.2f}ms per text")
            
            # Benchmark 3: Batch translation
            logger.info("Benchmark 3: Batch translation...")
            batch_texts = test_texts * 4  # 20 texts
            
            start = time.time()
            results_batch = tm.batch_translate_grouped(batch_texts, batch_size=10)
            batch_time = time.time() - start
            
            results['batch_translation'] = {
                'time_s': batch_time,
                'texts': len(batch_texts),
                'avg_per_text_ms': (batch_time * 1000) / len(batch_texts),
            }
            logger.info(f"Batch (20 texts): {batch_time:.2f}s ({(batch_time*1000)/len(batch_texts):.2f}ms per text)")
            
            # Cache stats
            cache_stats = tm.get_cache_stats()
            results['cache_stats'] = cache_stats
            logger.info(f"Cache stats: {cache_stats['total_entries']} entries, {cache_stats['hit_rate']*100:.1f}% hit rate")
            
            self.results['translation_cache'] = results
            return results
            
        except Exception as e:
            logger.error(f"Translation cache benchmark failed: {e}")
            return {'error': str(e)}
    
    def benchmark_full_pipeline(self) -> Dict:
        """Benchmark complete pipeline with different image sizes."""
        logger.info("\n=== BENCHMARKING FULL PIPELINE ===")
        
        try:
            from reader import Manga_Reader
            from PIL import Image as PILImage
            
            results = {}
            reader = Manga_Reader()
            
            # Create test images of different sizes
            test_configs = [
                {'size': (480, 640), 'name': 'small'},
                {'size': (768, 1024), 'name': 'medium'},
            ]
            
            for config in test_configs:
                size_key = f"{config['name']}"
                logger.info(f"Testing full pipeline with {size_key} image...")
                
                # Create test image
                test_img = self.create_test_image(config['size'][0], config['size'][1])
                
                timings = []
                memory_peaks = []
                
                for run in range(2):
                    tracemalloc.start()
                    start = time.time()
                    
                    output_img = reader(test_img, use_batch_translation=True)
                    
                    elapsed = time.time() - start
                    _, peak_mem = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    
                    timings.append(elapsed)
                    memory_peaks.append(peak_mem / 1024 / 1024)
                
                results[size_key] = {
                    'size': f"{config['size'][0]}x{config['size'][1]}",
                    'time_s': {
                        'mean': np.mean(timings),
                        'std': np.std(timings),
                        'min': np.min(timings),
                        'max': np.max(timings),
                    },
                    'memory_mb': {
                        'mean': np.mean(memory_peaks),
                        'peak': np.max(memory_peaks),
                    }
                }
                
                logger.info(f"  Time: {np.mean(timings):.2f}s ± {np.std(timings):.2f}s")
                logger.info(f"  Memory: {np.mean(memory_peaks):.2f}MB (peak: {np.max(memory_peaks):.2f}MB)")
            
            self.results['full_pipeline'] = results
            return results
            
        except Exception as e:
            logger.error(f"Full pipeline benchmark failed: {e}")
            logger.error(f"This is expected if images have no detectable text")
            return {'error': str(e), 'note': 'Expected if test image has no text'}
    
    def analyze_and_recommend(self) -> List[str]:
        """Analyze results and provide optimization recommendations."""
        logger.info("\n=== PERFORMANCE ANALYSIS & RECOMMENDATIONS ===")
        
        recommendations = []
        
        # Check image preprocessing
        if 'image_preprocessing' in self.results:
            preproc = self.results['image_preprocessing']
            for size, metrics in preproc.items():
                if metrics['time_ms']['mean'] > 100:
                    recommendations.append(
                        f"⚠️ Image preprocessing slow for {size}: {metrics['time_ms']['mean']:.0f}ms. "
                        "Consider using CPU-optimized libraries (OpenCV)."
                    )
        
        # Check model loading
        if 'model_loading' in self.results:
            model = self.results['model_loading']
            if 'cold_load' in model and model['cold_load']['time_s'] > 5:
                recommendations.append(
                    f"⚠️ Model loading slow: {model['cold_load']['time_s']:.1f}s. "
                    "Consider using model caching or async loading."
                )
            
            if 'inference' in model and model['inference']['time_s']['mean'] > 3:
                recommendations.append(
                    f"⚠️ Inference slow: {model['inference']['time_s']['mean']:.2f}s. "
                    "Consider using YOLOv8n (nano) or GPU acceleration."
                )
        
        # Check OCR
        if 'ocr_recognition' in self.results:
            ocr = self.results['ocr_recognition']
            if 'recognition' in ocr:
                for size, metrics in ocr['recognition'].items():
                    if metrics['time_ms']['mean'] > 200:
                        recommendations.append(
                            f"⚠️ OCR slow for {size}: {metrics['time_ms']['mean']:.0f}ms. "
                            "Consider batch processing or model optimization."
                        )
        
        # Check translation
        if 'translation_cache' in self.results:
            trans = self.results['translation_cache']
            if 'cache_stats' in trans:
                hit_rate = trans['cache_stats']['hit_rate']
                if hit_rate < 0.5:
                    recommendations.append(
                        f"✅ Cache hit rate: {hit_rate*100:.1f}%. Good opportunity for improvement. "
                        "More repeated texts = faster processing."
                    )
            
            if 'batch_translation' in trans:
                batch_speed = trans['batch_translation']['avg_per_text_ms']
                if batch_speed > 500:
                    recommendations.append(
                        f"⚠️ Batch translation slow: {batch_speed:.0f}ms per text. "
                        "Check API latency or network connection."
                    )
        
        # Optimization suggestions
        recommendations.extend([
            "\n✅ OPTIMIZATION OPPORTUNITIES:\n",
            "1. IMAGE PREPROCESSING: Use OpenCV instead of PIL for 20-30% speedup",
            "2. MODEL: Use YOLOv8n (nano) instead of YOLOv8s for 2x speedup (with slightly lower accuracy)",
            "3. BATCH SIZE: Increase BATCH_SIZE to 20-30 if memory allows (more API efficiency)",
            "4. CACHING: Ensure translation cache is enabled (100x speedup for repeated texts)",
            "5. GPU: Install CUDA/GPU support for 3-5x speedup on inference",
            "6. RESIZING: Resize images to 640x480 max before processing (reduce YOLO load)",
            "7. LAZY LOADING: Load models only when first image processed (save ~500MB memory)",
            "8. THREADING: Process images in parallel (if processing multiple images)",
        ])
        
        self.results['recommendations'] = recommendations
        return recommendations
    
    def save_results(self, output_file: str = "benchmark_results_full_pipeline.json"):
        """Save results to JSON file."""
        try:
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, default=str)
            logger.info(f"\n✅ Results saved to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            return None
    
    def generate_report(self, output_file: str = "performance_report.txt"):
        """Generate human-readable performance report."""
        try:
            report_lines = []
            report_lines.append("=" * 80)
            report_lines.append("MANGA READER - FULL PIPELINE PERFORMANCE REPORT")
            report_lines.append("=" * 80)
            report_lines.append(f"Generated: {self.results['timestamp']}\n")
            
            # Image Preprocessing
            if 'image_preprocessing' in self.results:
                report_lines.append("IMAGE PREPROCESSING")
                report_lines.append("-" * 80)
                for size, metrics in self.results['image_preprocessing'].items():
                    time_mean = metrics['time_ms']['mean']
                    mem_mean = metrics['memory_mb']['mean']
                    report_lines.append(f"{size:15} | Time: {time_mean:8.2f}ms | Memory: {mem_mean:7.2f}MB")
                report_lines.append("")
            
            # Model Loading
            if 'model_loading' in self.results:
                report_lines.append("MODEL LOADING & INFERENCE")
                report_lines.append("-" * 80)
                ml = self.results['model_loading']
                if 'cold_load' in ml:
                    report_lines.append(f"Cold Load: {ml['cold_load']['time_s']:.2f}s, Memory: {ml['cold_load']['memory_mb']:.2f}MB")
                if 'inference' in ml:
                    inf = ml['inference']['time_s']
                    report_lines.append(f"Inference: {inf['mean']:.2f}s ± {inf['std']:.2f}s")
                report_lines.append("")
            
            # OCR
            if 'ocr_recognition' in self.results:
                report_lines.append("OCR TEXT RECOGNITION")
                report_lines.append("-" * 80)
                ocr = self.results['ocr_recognition']
                if 'recognition' in ocr:
                    for size, metrics in ocr['recognition'].items():
                        time_mean = metrics['time_ms']['mean']
                        report_lines.append(f"{size:15} | Time: {time_mean:8.2f}ms")
                report_lines.append("")
            
            # Translation
            if 'translation_cache' in self.results:
                report_lines.append("TRANSLATION PERFORMANCE")
                report_lines.append("-" * 80)
                trans = self.results['translation_cache']
                if 'cold_cache' in trans:
                    report_lines.append(f"Cold Cache:  {trans['cold_cache']['time_ms']['mean']:8.2f}ms per text")
                if 'warm_cache' in trans:
                    report_lines.append(f"Warm Cache:  {trans['warm_cache']['time_ms']['mean']:8.2f}ms per text")
                    speedup = trans['cold_cache']['time_ms']['mean'] / max(trans['warm_cache']['time_ms']['mean'], 0.01)
                    report_lines.append(f"Speedup: {speedup:.1f}x")
                if 'batch_translation' in trans:
                    report_lines.append(f"Batch (20 texts): {trans['batch_translation']['time_s']:.2f}s")
                if 'cache_stats' in trans:
                    stats = trans['cache_stats']
                    report_lines.append(f"Cache: {stats['total_entries']} entries, {stats['hit_rate']*100:.1f}% hit rate")
                report_lines.append("")
            
            # Full Pipeline
            if 'full_pipeline' in self.results:
                report_lines.append("FULL PIPELINE")
                report_lines.append("-" * 80)
                for name, metrics in self.results['full_pipeline'].items():
                    time_mean = metrics['time_s']['mean']
                    mem_mean = metrics['memory_mb']['mean']
                    report_lines.append(f"{name:15} | Time: {time_mean:8.2f}s | Memory: {mem_mean:7.2f}MB")
                report_lines.append("")
            
            # Recommendations
            if 'recommendations' in self.results:
                report_lines.append("RECOMMENDATIONS")
                report_lines.append("-" * 80)
                for rec in self.results['recommendations']:
                    report_lines.append(rec)
                report_lines.append("")
            
            report_lines.append("=" * 80)
            
            # Save to file
            report_path = Path(output_file)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            
            # Print to console
            print('\n'.join(report_lines))
            logger.info(f"✅ Report saved to {report_path}")
            
            return report_path
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return None
    
    def run_all_benchmarks(self):
        """Run all benchmarks."""
        logger.info("\n" + "=" * 80)
        logger.info("STARTING FULL PIPELINE PERFORMANCE BENCHMARKS")
        logger.info("=" * 80)
        
        try:
            self.benchmark_image_preprocessing()
        except Exception as e:
            logger.error(f"Image preprocessing benchmark error: {e}")
        
        try:
            self.benchmark_model_loading()
        except Exception as e:
            logger.error(f"Model loading benchmark error: {e}")
        
        try:
            self.benchmark_ocr_recognition()
        except Exception as e:
            logger.error(f"OCR benchmark error: {e}")
        
        try:
            self.benchmark_translation_cache()
        except Exception as e:
            logger.error(f"Translation cache benchmark error: {e}")
        
        try:
            self.benchmark_full_pipeline()
        except Exception as e:
            logger.error(f"Full pipeline benchmark error: {e}")
        
        # Analysis
        self.analyze_and_recommend()
        
        # Save results
        self.save_results()
        self.generate_report()
        
        logger.info("\n" + "=" * 80)
        logger.info("BENCHMARKING COMPLETE")
        logger.info("=" * 80)


if __name__ == "__main__":
    profiler = PerformanceProfiler()
    profiler.run_all_benchmarks()
