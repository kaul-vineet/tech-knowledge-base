# RB-2 Memory pressure

Symptoms: OutOfMemoryError or killed containers, restarts every few minutes, error spikes right after each restart. Heap or memory limits are too small for the current load.

Steps: confirm the restart loop, raise the memory limit for the pod, capture a heap dump before the next restart, reduce batch sizes. Open an incident document for SEV1.
