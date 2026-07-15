#!/usr/bin/env python3
"""Teste de carga simples para Aula 9.

Uso:
  python scripts/load-test-simple.py --url http://localhost:8000/health --concurrency 20 --duration 30
"""

from __future__ import annotations

import argparse
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass
class Stats:
    total: int = 0
    success: int = 0
    fail: int = 0


def worker(url: str, deadline: float, stats: Stats, lock: threading.Lock) -> None:
    while time.time() < deadline:
        ok = False
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                ok = 200 <= response.status < 400
        except (urllib.error.URLError, TimeoutError, ValueError):
            ok = False

        with lock:
            stats.total += 1
            if ok:
                stats.success += 1
            else:
                stats.fail += 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Load test simples para CloudTask")
    parser.add_argument("--url", required=True, help="URL alvo")
    parser.add_argument("--concurrency", type=int, default=10, help="Numero de workers")
    parser.add_argument("--duration", type=int, default=20, help="Duracao em segundos")
    args = parser.parse_args()

    deadline = time.time() + args.duration
    stats = Stats()
    lock = threading.Lock()

    threads = [
        threading.Thread(target=worker, args=(args.url, deadline, stats, lock), daemon=True)
        for _ in range(args.concurrency)
    ]

    start = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = max(time.time() - start, 0.001)

    rps = stats.total / elapsed
    success_rate = (stats.success / stats.total * 100) if stats.total else 0.0

    print("=== Resultado ===")
    print(f"URL: {args.url}")
    print(f"Concurrencia: {args.concurrency}")
    print(f"Duracao: {args.duration}s")
    print(f"Total: {stats.total}")
    print(f"Sucesso: {stats.success}")
    print(f"Falha: {stats.fail}")
    print(f"Sucesso (%): {success_rate:.2f}")
    print(f"RPS: {rps:.2f}")


if __name__ == "__main__":
    main()
