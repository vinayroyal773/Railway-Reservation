const Protocols = (() => {
  // ---- CRC (the bit-flip demo re-checks the codeword in the browser) ----
  function crcHasError(codeword, generator, msgLen) {
    const a = codeword.split("");
    for (let i = 0; i < msgLen; i++) {
      if (a[i] === "1") {
        for (let j = 0; j < generator.length; j++) {
          a[i + j] = a[i + j] === generator[j] ? "0" : "1";
        }
      }
    }
    return a.includes("1");
  }

  function renderCodeword(box, r, bits) {
    const msgLen = r.message.length;
    const original = r.codeword;
    box.innerHTML = bits.map((b, i) =>
      `<button type="button" class="bit ${i >= msgLen ? "crc" : ""} ${b !== original[i] ? "flipped" : ""}" data-i="${i}" title="Click to flip this bit">${b}</button>`
    ).join("");
  }

  async function runCrc(e) {
    e.preventDefault();
    const btn = e.submitter || $("#crcForm button");
    setBusy(btn, true, "Computing…");
    try {
      const r = await Api.crc($("#crcMsg").value.trim(), $("#crcGen").value.trim());
      $("#crcResult").innerHTML = `
        <div class="stats">
          <div class="stat"><span class="mono">${esc(r.crc)}</span><label>CRC remainder</label></div>
          <div class="stat"><span class="mono">${esc(r.codeword)}</span><label>Transmitted codeword</label></div>
          <div class="stat ${r.error_detected ? "bad" : "ok"}"><span>${r.error_detected ? "Error" : "OK"}</span><label>Receiver check</label></div>
        </div>
        <h3>Try corrupting the transmission</h3>
        <p class="muted small">Click bits to flip them (blue = message, orange = CRC) and see whether the receiver detects the error.</p>
        <div class="bits" id="crcBits"></div>
        <div id="crcLive" class="notice ok">Codeword intact — no error detected.</div>`;

      let bits = r.codeword.split("");
      const bitsBox = $("#crcBits");
      renderCodeword(bitsBox, r, bits);
      bitsBox.addEventListener("click", ev => {
        const i = ev.target.dataset && ev.target.dataset.i;
        if (i === undefined) return;
        bits[i] = bits[i] === "1" ? "0" : "1";
        renderCodeword(bitsBox, r, bits);
        const err = crcHasError(bits.join(""), r.generator, r.message.length);
        const live = $("#crcLive");
        live.className = "notice " + (err ? "bad" : "ok");
        live.textContent = err
          ? "Error detected — the receiver would request retransmission."
          : (bits.join("") === r.codeword
              ? "Codeword intact — no error detected."
              : "Bits changed but the remainder is zero — this error pattern went undetected.");
      });
    } catch (err) {
      toast(err.message, "error");
    } finally {
      setBusy(btn, false);
    }
  }

  // ---- Sliding window ----
  async function runSliding(e) {
    e.preventDefault();
    const btn = e.submitter || $("#swForm button");
    setBusy(btn, true, "Simulating…");
    try {
      const r = await Api.slidingWindow(+$("#swPackets").value, +$("#swWindow").value);
      const windows = [];
      for (let i = 0; i < r.sent_packets.length; i += r.window_size) {
        windows.push(r.sent_packets.slice(i, i + r.window_size));
      }
      $("#swResult").innerHTML = `
        <div class="stats">
          <div class="stat"><span>${r.total_packets}</span><label>Packets</label></div>
          <div class="stat ok"><span>${r.acknowledged_packets.length}</span><label>Acknowledged</label></div>
          <div class="stat"><span>${r.retransmissions}</span><label>Retransmissions</label></div>
        </div>
        ${windows.map((w, i) => `
          <div class="window"><span class="wl">Window ${i + 1}</span>${pktChips(w, () => "ack")}<span class="muted small">ACK ✓</span></div>`).join("")}`;
    } catch (err) {
      toast(err.message, "error");
    } finally {
      setBusy(btn, false);
    }
  }

  // ---- Go-Back-N ----
  async function runGbn(e) {
    e.preventDefault();
    const btn = e.submitter || $("#gbnForm button");
    setBusy(btn, true, "Simulating…");
    try {
      const r = await Api.goBackN(+$("#gbnPackets").value, +$("#gbnWindow").value, +$("#gbnLost").value);
      const again = new Set(r.retransmitted_packets);
      $("#gbnResult").innerHTML = `
        <div class="stats">
          <div class="stat"><span>${r.total_packets}</span><label>Packets</label></div>
          <div class="stat bad"><span>#${r.lost_packet}</span><label>Lost packet</label></div>
          <div class="stat"><span>${r.retransmission_count}</span><label>Retransmitted</label></div>
        </div>
        <h3>First transmission</h3>
        ${pktChips(r.initial_transmission, n => n === r.lost_packet ? "lost" : (again.has(n) ? "discarded" : "ack"))}
        <p class="muted small">Red = lost. Orange = received out of order and discarded by the receiver.</p>
        <h3>After timeout — sender goes back</h3>
        ${r.retransmitted_packets.length ? pktChips(r.retransmitted_packets, () => "retx") : '<span class="muted">Nothing to resend.</span>'}`;
    } catch (err) {
      toast(err.message, "error");
    } finally {
      setBusy(btn, false);
    }
  }

  function init() {
    $("#crcForm").addEventListener("submit", runCrc);
    $("#swForm").addEventListener("submit", runSliding);
    $("#gbnForm").addEventListener("submit", runGbn);
  }

  return { init };
})();
