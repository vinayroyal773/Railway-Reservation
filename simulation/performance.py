def performance_metrics(sent, lost, delivered, delay_ms):
    packet_loss = (lost / sent * 100) if sent else 0
    throughput = (delivered / delay_ms) if delay_ms else 0
    return {"packet_loss_percent": round(packet_loss,2),
            "throughput_packets_per_ms": round(throughput,4),
            "delay_ms": delay_ms}
