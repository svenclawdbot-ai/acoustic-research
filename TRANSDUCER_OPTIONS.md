# Ultrasound Transducer Options — TurboQuant V5

**Date:** 2026-04-21
**Searched:** eBay UK (current listings)

---

## What You Actually Need

For acoustic NDE / shear wave elastography with the TurboQuant board:

| Spec | Target | Why |
|------|--------|-----|
| **Type** | Single-element contact | Simple, works with MUX |
| **Frequency** | 2–10 MHz (start with 5 MHz) | Good penetration + resolution balance |
| **Diameter** | 6–20 mm | Matches DG408 input impedance |
| **Connector** | BNC or Microdot | Easy to adapt to SMA |
| **Beam** | Straight (0°) or angled | 0° for initial testing, angle for shear |
| **Quantity** | 2–4 minimum | For TX/RX pair + spares |

---

## ❌ Skip: Medical Imaging Probes

These are **phased arrays or curved arrays** — they have 64-128 elements internally and won't work with your single-channel MUX board:

| Item | Price | Why Skip |
|------|-------|----------|
| SonoSite L38 10-5 MHz linear | £300–£600 | Linear array, 128 elements, incompatible |
| GE 10LB / C60x 5-2 MHz | £600–£1,700 | Curved/phased array, incompatible |
| BK Medical 8545-S 7.5 MHz | £670 | Endocavity probe, incompatible |
| Toshiba / Aloka / Hitachi probes | £1,000+ | Various array types, incompatible |

---

## ✅ Good Options: NDT Probes (eBay — New from China)

These are **single-element NDT probes** with BNC connectors. Perfect for your application.

### Straight Beam (0°) — Start Here

| Item | Price | Specs | Link |
|------|-------|-------|------|
| **Mitech N05/90** | **£34** | 10mm, 5MHz, straight, BNC | eBay UK (orchid) |
| **Mitech N07** | **£32** | 6mm, 7MHz, straight, BNC | eBay UK (orchid) |
| Yushi PT12 | £55 | Dual element, 5MHz, BNC | eBay UK (orchid) |
| Yushi TC510 | £123 | 5MHz, thickness gauge probe | eBay UK (orchid) |
| Yushi 0° 20mm | £74–£98 | 20mm, 1MHz, straight, LEMO | eBay UK (worldwidecardz) |
| Yushi Straight Beam 24mm | £87 | 24mm, 1MHz, straight, BNC | eBay UK (orchid) |

### Angle Beam — For Shear Waves

| Item | Price | Specs | Link |
|------|-------|-------|------|
| **Yushi Angle Beam 5MHz 14×14** | **£51** | 14×14mm, 5MHz, 45°, BNC | eBay UK (orchid) |
| Yushi Angle Beam 6×6mm K3 | £55 | 6×6mm, 5MHz, 63.4°, BNC | eBay UK (orchid) |
| Yushi 5MHz 13×13 56.3° | £52 | 13×13mm, 5MHz, 56.3°, BNC | eBay UK (orchid) |
| Tru-Sonic AWS 70° | £161 | 70° wedge, angle beam, BNC | eBay UK (orchid) |

### Dual Element — For Thickness / Pulse-Echo

| Item | Price | Specs | Link |
|------|-------|-------|------|
| 2MHz 25mm Dual Straight | £59 | 25mm, 2MHz, dual, BNC | eBay UK (orchid) |
| 7.5MHz 6mm Small Probe | £41 | 6mm, 7.5MHz, straight | eBay UK (orchid) |
| Yushi PT-04 10MHz 4mm | £129 | 4mm, 10MHz, fingertip | eBay UK (orchid) |

---

## eBay Search URLs (Bookmark These)

**NDT probes (single element, cheap):**
```
https://www.ebay.co.uk/sch/i.html?_nkw=ultrasonic+transducer+ndt+probe&_sacat=0
```

**Specific brands to watch:**
```
https://www.ebay.co.uk/sch/i.html?_nkw=mitech+ndt+probe+5mhz
https://www.ebay.co.uk/sch/i.html?_nkw=yushi+ultrasonic+probe+straight
https://www.ebay.co.uk/sch/i.html?_nkw=angle+beam+transducer+5mhz
```

---

## My Recommendation

### Starter Set (Under £100)

| Qty | Item | Price | Purpose |
|-----|------|-------|---------|
| 2 | **Mitech N05/90 (10mm, 5MHz, straight)** | £34 each | Primary TX/RX pair |
| 1 | **Yushi Angle Beam 45° (14×14mm, 5MHz)** | £51 | Shear wave testing |
| 1 | Mitech N07 (6mm, 7MHz, straight) | £32 | Higher resolution tests |
| | | **£151 total** | |

### Why This Set?
- **Mitech N05/90 ×2:** 5MHz is the NDT sweet spot. 10mm diameter gives good sensitivity. Buy 2 for pulse-echo (one TX, one RX) or pitch-catch.
- **Yushi 45° angle beam:** For generating shear waves — essential for elastography.
- **N07 (7MHz):** Smaller, higher resolution. Good for near-surface work.

### SMA Adapter Needed
These probes come with BNC connectors. You'll need:
- BNC-to-SMA adapter (£2-5 each on Amazon/eBay)
- Or cut the BNC off and solder SMA directly (better for high frequency)

---

## Alternative: Build Your Own (Advanced)

If you want to experiment:
- **Piezo discs:** 10mm PZT-5A, 5MHz — £5-10 on AliExpress
- **Housing:** 3D print or machine from aluminium rod
- **Backing:** Tungsten-epoxy or silicone rubber
- **Matching layer:** Fused silica or epoxy with alumina filler

**Cost:** £10-20 per transducer if you have access to a lathe/3D printer.
**Time:** 2-3 days per transducer.

Only worth it if you want custom frequencies or can't source commercial probes.

---

## What to Avoid

| Item | Why |
|------|-----|
| TCT40-16 (40kHz air transducer) | Too low frequency, for distance sensing |
| Sonotrode / welding transducers | Continuous wave, not pulsed, wrong impedance |
| Underwater/sonar transducers | Low frequency, different design |
| Any "phased array," "curved array," "linear array" | Multi-element, incompatible with single-channel MUX |

---

## Summary

| Source | Price Range | Quality | Speed |
|--------|-------------|---------|-------|
| eBay China (Yushi/Mitech) | £30–£130 | Good enough for research | 2-3 weeks shipping |
| eBay UK used (Panametrics, etc.) | £300–£900 | Professional grade | 1 week |
| New from NDT supplier | £200–£500 | Certified, calibrated | 1-2 weeks |
| DIY from PZT discs | £10–£20 | Variable | 2-3 days + learning curve |

**Best value for TurboQuant:** eBay China starter set (~£150 for 4 probes).

---

*Searched: April 21, 2026*
*Sources: eBay UK current listings*
