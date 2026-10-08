def simulate_go_back_n(packets, window_size, lost_packet):
    """Go-Back-N with one lost packet.

    The sender keeps up to `window_size` packets in flight. While the lost
    packet is unacknowledged, the sender keeps sending the rest of its window.
    The receiver discards those out-of-order packets, so after the timeout the
    sender goes back and resends the lost packet and everything sent after it.
    """
    transmitted = list(range(1, packets + 1))
    retransmitted = []

    if 1 <= lost_packet <= packets:
        last_sent = min(lost_packet + window_size - 1, packets)
        retransmitted = list(range(lost_packet, last_sent + 1))

    return {"total_packets": packets,
            "window_size": window_size,
            "lost_packet": lost_packet,
            "initial_transmission": transmitted,
            "retransmitted_packets": retransmitted,
            "retransmission_count": len(retransmitted)}
