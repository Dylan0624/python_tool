import socket
import time
import argparse
import multiprocessing
import struct
import os
import dpkt

# 設定參數
parser = argparse.ArgumentParser(description="PCAP File UDP Packet Sender")
parser.add_argument("--mbps", type=float, default=150.0, help="目標傳輸速率 (MB/s)")
parser.add_argument("--processes", type=int, default=8, help="使用多少個獨立進程 (CPU 核心)")
parser.add_argument("--pcap", type=str, default="input/bu25_no6_20250319.pcap", help="PCAP 檔案路徑")
args = parser.parse_args()

# 設備的 IP 和埠 (目標 Android 設備)
TARGET_IP = "192.168.48.20"
TARGET_PORT = 7000

# 共享變數，用來統計傳輸速率
total_bytes_sent = multiprocessing.Value("L", 0)  # 64-bit 整數
running = multiprocessing.Value("b", True)  # 共享布林值，用來控制程序終止

# 計算目標速率
BYTES_PER_MB = 1024 * 1024
target_rate_bps = args.mbps * BYTES_PER_MB  # 轉成 Bytes

def read_pcap_packets(pcap_file):
    """讀取 PCAP 檔案中的封包內容"""
    packets = []
    
    try:
        with open(pcap_file, 'rb') as f:
            pcap = dpkt.pcap.Reader(f)
            for ts, buf in pcap:
                # 取得乙太網路封包
                eth = dpkt.ethernet.Ethernet(buf)
                
                # 確保是 IP 封包
                if isinstance(eth.data, dpkt.ip.IP):
                    ip = eth.data
                    
                    # 確保是 UDP 封包
                    if isinstance(ip.data, dpkt.udp.UDP):
                        udp = ip.data
                        
                        # 取得 UDP 封包內容
                        payload = bytes(udp.data)
                        if payload:  # 確保不為空
                            packets.append(payload)
    except Exception as e:
        print(f"讀取 PCAP 檔案時出錯: {e}")
        return []
    
    print(f"從 PCAP 檔案讀取了 {len(packets)} 個封包")
    return packets

def send_packets(process_id, shared_bytes, pcap_packets):
    """子進程發送 PCAP 檔案中的 UDP 封包，並將統計資訊回報給主進程"""
    if not pcap_packets:
        print("沒有封包可發送")
        return
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 0))
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4 * 1024 * 1024)  # 增加發送緩衝區
    
    local_bytes_sent = 0
    packet_index = 0
    total_packets = len(pcap_packets)
    
    # 計算每個封包的平均大小用於控制速率
    avg_packet_size = sum(len(p) for p in pcap_packets) / total_packets
    packets_per_second = target_rate_bps / (avg_packet_size * args.processes)
    packet_interval = 1.0 / packets_per_second
    
    print(f"進程 {process_id}: 平均封包大小 {avg_packet_size:.2f} 字節, 間隔 {packet_interval * 1_000_000:.2f} µs")
    
    while running.value:
        start_time = time.perf_counter()
        
        # 取得當前要發送的封包
        packet = pcap_packets[packet_index]
        packet_size = len(packet)
        
        # 發送封包
        sock.sendto(packet, (TARGET_IP, TARGET_PORT))
        local_bytes_sent += packet_size
        
        # 更新總計數
        with shared_bytes.get_lock():
            shared_bytes.value += packet_size
        
        # 移到下一個封包，如果到達結尾則重新開始
        packet_index = (packet_index + 1) % total_packets
        
        # 如果已經發送完所有封包，打印一條消息並從頭開始
        if packet_index == 0:
            print(f"進程 {process_id}: 已發送完所有封包，從頭開始發送")
        
        # 控制發送間隔，確保不超過目標速率
        elapsed_time = time.perf_counter() - start_time
        sleep_time = max(0, packet_interval - elapsed_time)
        time.sleep(sleep_time)

def monitor_speed(shared_bytes):
    """主進程監測傳輸速率"""
    start_time = time.perf_counter()
    last_bytes = 0

    while running.value:
        time.sleep(1)  # 每秒更新一次
        current_time = time.perf_counter()
        elapsed_time = current_time - start_time
        
        with shared_bytes.get_lock():
            current_bytes = shared_bytes.value
            bytes_since_last = current_bytes - last_bytes
            mbps_actual = (bytes_since_last / (1024 * 1024))  # 每秒 MB
            mbps_avg = (current_bytes / (1024 * 1024)) / elapsed_time  # 平均 MB/s
            
            print(f"📡 總計已發送: {current_bytes/(1024*1024):.2f} MB, 當前速率: {mbps_actual:.2f} MB/s, 平均速率: {mbps_avg:.2f} MB/s")
            last_bytes = current_bytes

if __name__ == "__main__":
    pcap_file = args.pcap
    
    # 檢查檔案是否存在
    if not os.path.exists(pcap_file):
        print(f"錯誤：找不到 PCAP 檔案 '{pcap_file}'")
        exit(1)
    
    print(f"⚡ 讀取 PCAP 檔案: {pcap_file}")
    pcap_packets = read_pcap_packets(pcap_file)
    
    if not pcap_packets:
        print("錯誤：PCAP 檔案中沒有找到有效的 UDP 封包")
        exit(1)
    
    print(f"⚡ 開始發送 PCAP 封包到 {TARGET_IP}:{TARGET_PORT}")
    print(f"📦 目標速率: {args.mbps} MB/s")
    print(f"🖥️ 使用 {args.processes} 個獨立 CPU 進程發送封包")
    print(f"🔄 設定為循環發送模式: 發送完所有封包後將從頭開始")
    
    # 啟動發送封包的子進程
    processes = []
    for i in range(args.processes):
        p = multiprocessing.Process(target=send_packets, args=(i, total_bytes_sent, pcap_packets))
        p.daemon = True
        p.start()
        processes.append(p)
    
    # 啟動監測速率的進程
    monitor = multiprocessing.Process(target=monitor_speed, args=(total_bytes_sent,))
    monitor.daemon = True
    monitor.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 停止發送")
        running.value = False
        for p in processes:
            p.terminate()
        monitor.terminate()