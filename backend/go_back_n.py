def simulate_go_back_n(packets, window_size, lost_packet):
    transmitted, retransmitted = [], []
    lost_handled = False
    for start in range(1, packets + 1, window_size):
        end = min(start + window_size - 1, packets)
        window = list(range(start, end + 1))
        transmitted += window
        if not lost_handled and lost_packet in window:
            retransmitted += list(range(lost_packet, end + 1))
            lost_handled = True
    return {"total_packets": packets, "window_size": window_size,
            "initial_transmission": transmitted,
            "retransmitted_packets": retransmitted,
            "retransmission_count": len(retransmitted)}
