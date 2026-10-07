def simulate_sliding_window(packets, window_size):
    sent = []
    ack = []
    for start in range(1, packets + 1, window_size):
        end = min(start + window_size - 1, packets)
        window = list(range(start, end + 1))
        sent += window
        ack += window
    return {"total_packets": packets, "window_size": window_size,
            "sent_packets": sent, "acknowledged_packets": ack, "retransmissions": 0}
