"""
Performance Monitoring Script
Phase 7-5: Load testing and scalability verification
"""

import json
import psutil
import time
import sys
from datetime import datetime
from typing import Dict, Any, List

class PerformanceMonitor:
    """システムパフォーマンスモニタリングクラス"""
    
    def __init__(self, interval: int = 5, duration: int = 300):
        """
        初期化
        
        Args:
            interval: サンプリング間隔（秒）
            duration: 監視期間（秒）、0の場合は無制限
        """
        self.interval = interval
        self.duration = duration
        self.metrics_history: List[Dict[str, Any]] = []
        self.start_time = None
    
    def collect_metrics(self) -> Dict[str, Any]:
        """現在のシステムメトリクスを収集"""
        cpu_percent = psutil.cpu_percent(interval=1, percpu=False)
        cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
        
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        net_io = psutil.net_io_counters()
        
        # プロセス情報
        try:
            process_count = len(psutil.pids())
            connections = len(psutil.net_connections())
        except:
            process_count = 0
            connections = 0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "percent": cpu_percent,
                "per_core": cpu_per_core,
                "count": psutil.cpu_count(),
            },
            "memory": {
                "total_mb": memory.total / (1024 * 1024),
                "available_mb": memory.available / (1024 * 1024),
                "used_mb": memory.used / (1024 * 1024),
                "percent": memory.percent,
            },
            "disk": {
                "total_gb": disk.total / (1024 * 1024 * 1024),
                "used_gb": disk.used / (1024 * 1024 * 1024),
                "free_gb": disk.free / (1024 * 1024 * 1024),
                "percent": disk.percent,
            },
            "disk_io": {
                "read_mb": disk_io.read_bytes / (1024 * 1024),
                "write_mb": disk_io.write_bytes / (1024 * 1024),
                "read_count": disk_io.read_count,
                "write_count": disk_io.write_count,
            } if disk_io else None,
            "network_io": {
                "bytes_sent_mb": net_io.bytes_sent / (1024 * 1024),
                "bytes_recv_mb": net_io.bytes_recv / (1024 * 1024),
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
            } if net_io else None,
            "system": {
                "process_count": process_count,
                "connections": connections,
                "uptime_seconds": time.time() - psutil.boot_time(),
            }
        }
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """収集したメトリクスの統計を計算"""
        if not self.metrics_history:
            return {}
        
        # CPU統計
        cpu_values = [m["cpu"]["percent"] for m in self.metrics_history]
        cpu_stats = {
            "avg": sum(cpu_values) / len(cpu_values),
            "min": min(cpu_values),
            "max": max(cpu_values),
        }
        
        # メモリ統計
        memory_values = [m["memory"]["percent"] for m in self.metrics_history]
        memory_stats = {
            "avg": sum(memory_values) / len(memory_values),
            "min": min(memory_values),
            "max": max(memory_values),
        }
        
        # ディスク統計
        disk_values = [m["disk"]["percent"] for m in self.metrics_history]
        disk_stats = {
            "avg": sum(disk_values) / len(disk_values),
            "min": min(disk_values),
            "max": max(disk_values),
        }
        
        return {
            "cpu": cpu_stats,
            "memory": memory_stats,
            "disk": disk_stats,
            "sample_count": len(self.metrics_history),
        }
    
    def display_current_metrics(self, metrics: Dict[str, Any]):
        """現在のメトリクスをコンソールに表示"""
        print("\r" + " " * 100, end="\r")  # クリア
        
        cpu = metrics["cpu"]["percent"]
        mem = metrics["memory"]["percent"]
        
        # プログレスバー風表示
        cpu_bar = self._create_bar(cpu, 50)
        mem_bar = self._create_bar(mem, 50)
        
        print(f"CPU:  [{cpu_bar}] {cpu:5.1f}%", end=" | ")
        print(f"MEM:  [{mem_bar}] {mem:5.1f}%", end=" | ")
        print(f"Processes: {metrics['system']['process_count']:4d} | ", end="")
        print(f"Connections: {metrics['system']['connections']:4d}", end="")
        
        sys.stdout.flush()
    
    def _create_bar(self, value: float, width: int = 20) -> str:
        """プログレスバーを生成"""
        filled = int(value / 100 * width)
        empty = width - filled
        
        if value >= 80:
            bar_char = "█"
        elif value >= 60:
            bar_char = "▓"
        else:
            bar_char = "▒"
        
        return bar_char * filled + "░" * empty
    
    def run(self):
        """モニタリングを実行"""
        print("="*80)
        print("🔍 Performance Monitoring Started")
        print("="*80)
        print(f"Interval: {self.interval}s")
        print(f"Duration: {self.duration}s" if self.duration > 0 else "Duration: Continuous")
        print("Press Ctrl+C to stop\n")
        
        self.start_time = time.time()
        
        try:
            while True:
                # メトリクス収集
                metrics = self.collect_metrics()
                self.metrics_history.append(metrics)
                
                # 表示
                self.display_current_metrics(metrics)
                
                # 期間チェック
                if self.duration > 0:
                    elapsed = time.time() - self.start_time
                    if elapsed >= self.duration:
                        break
                
                # 待機
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoring stopped by user")
        
        # 結果を表示・保存
        self._show_summary()
        self._save_results()
    
    def _show_summary(self):
        """サマリーを表示"""
        print("\n\n" + "="*80)
        print("📊 Monitoring Summary")
        print("="*80)
        
        stats = self.calculate_statistics()
        
        if stats:
            print(f"\nSamples Collected: {stats['sample_count']}")
            print(f"Duration: {time.time() - self.start_time:.2f}s")
            
            print(f"\nCPU Usage:")
            print(f"  Average: {stats['cpu']['avg']:.2f}%")
            print(f"  Min: {stats['cpu']['min']:.2f}%")
            print(f"  Max: {stats['cpu']['max']:.2f}%")
            
            print(f"\nMemory Usage:")
            print(f"  Average: {stats['memory']['avg']:.2f}%")
            print(f"  Min: {stats['memory']['min']:.2f}%")
            print(f"  Max: {stats['memory']['max']:.2f}%")
            
            print(f"\nDisk Usage:")
            print(f"  Average: {stats['disk']['avg']:.2f}%")
            print(f"  Min: {stats['disk']['min']:.2f}%")
            print(f"  Max: {stats['disk']['max']:.2f}%")
            
            # 警告
            if stats['cpu']['max'] > 80:
                print(f"\n⚠️  Warning: High CPU usage detected ({stats['cpu']['max']:.2f}%)")
            if stats['memory']['max'] > 80:
                print(f"\n⚠️  Warning: High memory usage detected ({stats['memory']['max']:.2f}%)")
    
    def _save_results(self):
        """結果をJSONファイルに保存"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"performance-monitoring-{timestamp}.json"
        
        report = {
            "test_id": f"perf-monitor-{timestamp}",
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_seconds": time.time() - self.start_time,
            "interval_seconds": self.interval,
            "statistics": self.calculate_statistics(),
            "metrics_history": self.metrics_history,
        }
        
        with open(filename, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")
        print("="*80 + "\n")


def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Performance Monitoring Tool")
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Sampling interval in seconds (default: 5)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=0,
        help="Monitoring duration in seconds, 0 for continuous (default: 0)"
    )
    
    args = parser.parse_args()
    
    monitor = PerformanceMonitor(interval=args.interval, duration=args.duration)
    monitor.run()


if __name__ == "__main__":
    main()
