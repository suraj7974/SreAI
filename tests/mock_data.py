"""Mock data for testing"""

MOCK_LOGS = """
2024-12-02 10:00:00 kernel: Out of memory: Kill process 1234 (python3)
2024-12-02 10:00:01 systemd[1]: nginx.service: Failed with result 'exit-code'
2024-12-02 10:00:02 kernel: CPU0: Package temperature above threshold
2024-12-02 10:00:03 postgres[5678]: ERROR: connection refused
2024-12-02 10:00:04 python3: RuntimeError: maximum recursion depth exceeded
2024-12-02 10:00:05 kernel: TCP: time wait bucket table overflow
2024-12-02 10:00:06 systemd[1]: Failed to start Application Service
2024-12-02 10:00:07 kernel: EXT4-fs warning: mounting fs with errors
2024-12-02 10:00:08 postgres[5679]: FATAL: too many connections
2024-12-02 10:00:09 nginx[8901]: 502 Bad Gateway
"""

MOCK_METRICS = {
    "cpu_usage_percent": 87.5,
    "memory_usage_percent": 92.3,
    "disk_usage_percent": 78.1,
    "load_1min": 5.2,
    "load_5min": 4.8,
    "load_15min": 3.9,
    "network_rx_bytes": 1048576000,
    "network_tx_bytes": 524288000,
    "disk_read_bytes": 2097152000,
    "disk_write_bytes": 1048576000
}
