**Concept: time-domain alerts - difference imaging, alert packets, and broker filters that code controls**

## Why it matters
Wide-field surveys turn every change in the sky into a message within minutes. A supernova rising, a known variable pulsing, an asteroid crossing and a cosmic ray all produce a residual when tonight's image is compared with a reference. Followers have scarce telescope time, so the stream must be small and mostly real. One systematic error in differencing turns every constant star into a "transient", and the stream becomes a storm. ZTF and Rubin package alerts as Avro records with a fixed schema (candid, objectId, the candidate measurement, the previous detections), and brokers such as Lasair filter them for users.

## Mental model
Subtract what you already knew, keep what changed, and say what it is in a fixed format.

```
reference --blur to tonight's seeing--+--fit flux a, b--> a*ref + b
new image ----------------------------+---------------------------> new - (a*ref + b) --> 5-sigma residuals
residuals --> packet (schema) --> broker: bogus? known variable? moving? else transient --> one alert/object/night
                                              code classifies; a model may only explain (gate)
```

## Design space
- **Differencing.** Plain subtraction is cheap but wrong whenever seeing or transparency change. Kernel matching (Alard & Lupton 1998) fits a convolution kernel by least squares; our version uses one Gaussian plus a flux scale. ZOGY (Zackay et al. 2016) is the optimal statistic for the background-limited case.
- **Where to filter.** A firehose (every residual) leaves the work to the users. A broker classifies with rules or machine learning and drops bogus. Association groups detections into objects and attaches their history.
- **Schema.** JSON for humans, Avro on the wire with versioned schemas and compatibility rules (Rubin uses FORWARD_TRANSITIVE). Validate every packet before publishing.
- **Explanations.** A local model can turn a packet into prose for an observer. Whether it may decide anything is a design decision; here it may not.

## How to decide
The criteria are: alerts per night (follow-up capacity), the real fraction, recall of the event you care about, never mislabelling a catalogued variable, and 100 % schema-valid packets. A seeded sky with known truth measures all of them.

**Worked example (lab run, 8 nights × 2 exposures):**
- Plain subtraction under option C gives 58.2 alerts per night, only 4.5 % real. Every star leaves a ring (seeing σ 1.5–2.1 against the reference's 1.2 px) and a residual (transparency 0.75–1.0).
- With matching, A gives 9.8 per night (46.2 % real), B 4.2 (88.2 %) and C 3.5 (85.7 %).
- The supernova is a transient on every night from 3 to 7, V1 is always `known_variable`, and the asteroid is mostly `moving`.

The fake model explaining alerts called V1 "a new transient" and invented "2.5 magnitudes". The gate blocked all three explanations, and no class changed.

## Failure modes at scale
- **Spatially varying PSF:** one kernel leaves residuals at the field edges, so bogus alerts cluster by position. Use a spatially varying kernel or ZOGY.
- **Dependency on catalogues:** without the known-variable catalogue, V1 produced 2 transient alerts (tryIt 2). Treat cross-match services as part of the pipeline, with health checks.
- **Partial matching hides real fades:** matching the PSF but not the flux turns stars into negative residuals (320 bogus in the firehose). The broker drops them, and a real fading source is dropped with them.
- **Association radius against motion:** a 2 px object grid cannot follow an asteroid moving 4 px per 20 min, which gets a new objectId per exposure. Moving-object linking is its own stage.

## Common mistakes
- Blurring the new image instead of the sharper reference, which throws away the night's resolution.
- Validating only the first packet, or validating after publishing.
- Letting a model's wording set or override a class. Explanations are published only if they name code's class and quote only the facts.
