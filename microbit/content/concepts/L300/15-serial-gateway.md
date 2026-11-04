# Concept: a serial gateway that survives a dirty link

## Why it matters
A board on a USB cable is the cheapest sensor-to-cloud path: the micro:bit prints, a PC program reads the port and forwards each reading to a broker. The link is not clean. Boot messages, a cable pulled mid-line, a dropped byte or a flipped bit all reach your gateway. A gateway that crashes on line 1, or forwards 22 °C as truth when the board sent 20 °C, breaks every system behind it.

## Mental model
**Envelopes on a conveyor belt.** Each reading travels in an envelope with a start mark, the length written on it and a seal. The clerk looks for a start mark, checks the length and the seal, and passes on only intact envelopes. Anything else: discard one byte and look for the next start mark.

```
bytes: ..\xff boot\r\n$0081,20,100*1DA1\r\n$008 1,20,1 $0083,20,102*B245\r\n
            skip      ^ $  LLL payload *CRC   ^ cut short: length/star fail -> resync
framer:  find "$" → read LLL → wait for LLL+5 bytes → "*" in place? → CRC ok? → publish
```

## How it works
1. **Frame on the device.** `frame()` prints `$`, a 3-digit length, the payload, `*` and a 4-hex-digit CRC-16/CCITT-FALSE → see lab step 1
2. **A line is not a message.** The naive gateway splits a text line and trusts it; boot garbage raises `ValueError` and stops everything → see lab step 3
3. **Length, then CRC.** The framer reads the length, waits until the whole frame has arrived (serial reads come in any chunk size), checks `*` and the line end at the expected place, then the CRC → see lab step 4
4. **Resync by one byte.** On any failure drop one byte and search for the next `$`; count `resyncs`, `bad_len`, `bad_crc` and skipped bytes → see lab step 4
5. **Publish MQTT-style JSON.** Valid readings go out as `{"topic", "qos", "payload"}` lines, or to a broker with paho-mqtt; counters go to `microbit/gateway/metrics` → see lab step 5
6. **Code alarms, agent explains.** Thresholds on the counters raise `LINK_NOISY` and `SEQ_GAP`; a local model only explains them, and code checks its text → see lab step 5

Worked example (from `research/concept_examples_l300.py`): 200 frames, seeded faults: 3 dropped bytes, 5 flipped bits, 2 lines cut short, plus boot garbage. The naive gateway raises `ValueError` on the first line and forwards nothing. The framer accepts 190 frames with 9 resyncs (6 bad length, 3 bad CRC): 4.5% damaged, and every forwarded value matches what the board sent. Random corruption passes a 16-bit CRC about once in 65,536.

## Failure modes
- **Chunk-dependent logic.** A metrics line was first emitted per batch of frames, so its numbers depended on how the bytes were chunked; `test_chunk_size_does_not_matter` caught it while this lab was written.
- **No CRC.** Without it a flipped digit is published as a real value (2 wrong values in tryIt 1).
- **Line ends.** Accept `\r\n` and `\n`.
- **Broker down.** Publishing must not block reading the port; QoS 1 waits for the broker's ack with a timeout.

## Common mistakes
- Using `readline()` and assuming one line is one valid message.
- Resyncing by dropping the whole buffer and the good frame behind the bad one.
- Letting the model decide alarms instead of explaining the ones code raised.
