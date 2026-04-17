"""
RTT vs. Speed-of-Light
Networks Assignment — Measurement & Geography

Run with: python rtt_speedoflight.py   (no sudo needed)
Requires: pip install requests matplotlib numpy
"""

import math, time, os, requests, numpy as np

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import urllib.request

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

TARGETS = {
    "Tokyo":        {"url": "http://www.google.co.jp",   "coords": (35.6762,  139.6503), "continent": "Asia"},
    "São Paulo":    {"url": "http://www.google.com.br",  "coords": (-23.5505, -46.6333), "continent": "S. America"},
    "Lagos":        {"url": "http://www.google.com.ng",  "coords": (6.5244,     3.3792), "continent": "Africa"},
    "Frankfurt":    {"url": "http://www.google.de",      "coords": (50.1109,    8.6821), "continent": "Europe"},
    "Sydney":       {"url": "http://www.google.com.au",  "coords": (-33.8688, 151.2093), "continent": "Oceania"},
    "Mumbai":       {"url": "http://www.google.co.in",   "coords": (19.0760,   72.8777), "continent": "Asia"},
    "London":       {"url": "http://www.google.co.uk",   "coords": (51.5074,   -0.1278), "continent": "Europe"},
    "Singapore":    {"url": "http://www.google.com.sg",  "coords": (1.3521,   103.8198), "continent": "Asia"},
}

PROBES           = 15
FIBER_SPEED_KM_S = 200_000
FIGURES_DIR      = "figures"

CONTINENT_COLORS = {
    "Asia":      "#e63946",
    "S. America":"#2a9d8f",
    "Africa":    "#e9c46a",
    "Europe":    "#457b9d",
    "Oceania":   "#a8dadc",
}

# ─────────────────────────────────────────────
# TASK 1 — MEASURE RTTs
# ─────────────────────────────────────────────

def measure_rtt(url: str, probes: int = PROBES) -> dict:
    """
    Measure RTT to `url` using HTTP requests.

    Return:
        {
            "min_ms":   float | None,
            "mean_ms":  float | None,
            "median_ms":float | None,
            "loss_pct": float,
            "samples":  list[float],
        }

    TODO:
        1. Loop `probes` times.
        2. Record time before and after urllib.request.urlopen(url, timeout=3).
           elapsed_ms = (time.perf_counter() - start) * 1000
        3. On any exception, count as lost.
        4. Compute min, mean, median using numpy.
        5. loss_pct = (lost / probes) * 100
        6. Sleep 0.2s between probes.
        7. If ALL probes lost, return None for all stats.
    """
    samples = []
    lost    = 0

    for _ in range(probes):
        try:
            start = time.perf_counter()
            with urllib.request.urlopen(url, timeout=3) as response:
                response.read(1)
            elapsed_ms = (time.perf_counter() - start) * 1000
            samples.append(elapsed_ms)
        except Exception:
            lost += 1
        time.sleep(0.2)

    if not samples:
        return {"min_ms": None, "mean_ms": None, "median_ms": None,
                "loss_pct": 100.0, "samples": []}

    return {
        "min_ms": float(np.min(samples)),
        "mean_ms": float(np.mean(samples)),
        "median_ms": float(np.median(samples)),
        "loss_pct": (lost / probes) * 100,
        "samples": samples,
    }


# ─────────────────────────────────────────────
# TASK 2 — HAVERSINE + INEFFICIENCY
# ─────────────────────────────────────────────

def great_circle_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute great-circle distance in km using the Haversine formula.

    Haversine:
        a = sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlon/2)
        c = 2 * atan2(√a, √(1−a))
        d = R * c       where R = 6371 km

    TODO: implement from scratch. Use math.radians() to convert degrees.
    Do NOT use geopy or any distance library.
    """
    R = 6371
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def get_my_location() -> tuple[float, float, str]:
    """Return (lat, lon, city) for this machine's public IP."""
    try:
        r = requests.get("https://ipinfo.io/json", timeout=5).json()
        lat, lon = map(float, r["loc"].split(","))
        return lat, lon, r.get("city", "Your Location")
    except Exception:
        print("Could not auto-detect location. Defaulting to Boston.")
        return 42.3601, -71.0589, "Boston"


def compute_inefficiency(results: dict, src_lat: float, src_lon: float) -> dict:
    """
    Annotate each city in results with:
        "distance_km"        — great-circle distance from source
        "theoretical_min_ms" — 2 * (distance / FIBER_SPEED_KM_S) * 1000
        "inefficiency_ratio" — median_ms / theoretical_min_ms
        "high_inefficiency"  — True if ratio > 3.0

    TODO:
        1. For each city, unpack coords and call great_circle_km().
        2. Compute theoretical_min_ms (* 2 for round-trip, * 1000 for ms).
        3. Compute ratio. If median_ms is None, set ratio to None.
        4. Annotate results[city] in place.
    """
    for city, data in results.items():
        dst_lat, dst_lon = data["coords"]
        distance_km = great_circle_km(src_lat, src_lon, dst_lat, dst_lon)
        theoretical_min_ms = 2 * (distance_km / FIBER_SPEED_KM_S) * 1000
        median_ms = data.get("median_ms")
        ratio = None if median_ms is None else median_ms / theoretical_min_ms

        data["distance_km"] = distance_km
        data["theoretical_min_ms"] = theoretical_min_ms
        data["inefficiency_ratio"] = ratio
        data["high_inefficiency"] = ratio is not None and ratio > 3.0
    return results


# ─────────────────────────────────────────────
# TASK 3 — PLOTS
# ─────────────────────────────────────────────

def make_plots(results: dict):
    """
    Produce two figures saved to FIGURES_DIR/.

    Figure 1 — fig1_rtt_comparison.png
        Grouped bar chart: measured median RTT vs. theoretical min RTT per city.
        Sort cities by distance_km ascending.
        Label axes, add legend and title.

    Figure 2 — fig2_distance_scatter.png
        Scatter: x = distance_km, y = measured median RTT.
        Draw a dashed line for theoretical minimum.
        Label each point with city name.
        Color by continent using CONTINENT_COLORS.
        Add continent legend and title.

    TODO: implement both figures.
    Hints:
        fig, ax = plt.subplots(figsize=(11, 6))
        ax.bar() / ax.scatter()
        plt.tight_layout()
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
    """
    os.makedirs(FIGURES_DIR, exist_ok=True)
    valid  = {c: d for c, d in results.items() if d.get("median_ms") is not None}
    cities = sorted(valid, key=lambda c: valid[c]["distance_km"])

    if not cities:
        print("No reachable targets; skipping plot generation.")
        return

    # ── Figure 1 ──────────────────────────────
    fig, ax = plt.subplots(figsize=(11, 6))
    x = np.arange(len(cities))
    width = 0.38
    measured = [valid[city]["median_ms"] for city in cities]
    theoretical = [valid[city]["theoretical_min_ms"] for city in cities]

    ax.bar(x - width / 2, measured, width=width, label="Measured median RTT", color="#457b9d")
    ax.bar(x + width / 2, theoretical, width=width, label="Theoretical minimum RTT", color="#e9c46a")
    ax.set_xticks(x)
    ax.set_xticklabels(cities, rotation=30, ha="right", fontsize=12)
    ax.set_xlabel("City", fontsize=14)
    ax.set_ylabel("RTT (ms)", fontsize=14)
    ax.set_title("Measured Median RTT vs. Theoretical Minimum RTT", fontsize=16)
    ax.tick_params(axis="y", labelsize=12)
    ax.legend(fontsize=12)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/fig1_rtt_comparison.png", dpi=150, bbox_inches="tight")
    plt.close()

    # ── Figure 2 ──────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 7))
    distances = [valid[city]["distance_km"] for city in cities]
    medians = [valid[city]["median_ms"] for city in cities]
    theor_line = [valid[city]["theoretical_min_ms"] for city in cities]

    for city in cities:
        data = valid[city]
        ax.scatter(
            data["distance_km"],
            data["median_ms"],
            s=90,
            color=CONTINENT_COLORS[data["continent"]],
            edgecolor="black",
            linewidth=0.5,
        )
        ax.annotate(
            city,
            (data["distance_km"], data["median_ms"]),
            xytext=(6, 6),
            textcoords="offset points",
            fontsize=12,
        )

    ax.plot(distances, theor_line, linestyle="--", color="black", linewidth=1.5, label="Theoretical minimum")
    ax.set_xlabel("Great-circle distance (km)", fontsize=14)
    ax.set_ylabel("Measured median RTT (ms)", fontsize=14)
    ax.set_title("Distance vs. Measured RTT", fontsize=16)
    ax.tick_params(axis="both", labelsize=12)
    ax.grid(True, linestyle="--", alpha=0.35)

    legend_handles = [
        mpatches.Patch(color=color, label=continent)
        for continent, color in CONTINENT_COLORS.items()
        if any(valid[city]["continent"] == continent for city in cities)
    ]
    legend_handles.append(plt.Line2D([0], [0], color="black", linestyle="--", label="Theoretical minimum"))
    ax.legend(handles=legend_handles, fontsize=12)
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/fig2_distance_scatter.png", dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Figures saved to {FIGURES_DIR}/")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    src_lat, src_lon, src_city = get_my_location()
    print(f"Your location: {src_city} ({src_lat:.4f}, {src_lon:.4f})\n")

    results = {}
    for city, info in TARGETS.items():
        print(f"Probing {city} ({info['url']}) ...", end=" ", flush=True)
        stats = measure_rtt(info["url"])
        results[city] = {**stats, "coords": info["coords"], "continent": info["continent"]}
        med = stats.get("median_ms")
        print(f"median={med:.1f} ms  loss={stats['loss_pct']:.0f}%" if med else "unreachable")

    results = compute_inefficiency(results, src_lat, src_lon)

    print(
        f"\n{'City':<14} {'Min ms':>8} {'Mean ms':>9} {'Median ms':>10} "
        f"{'Loss %':>7} {'Dist km':>8} {'Theor. ms':>10} {'Ratio':>7}"
    )
    print("-" * 86)
    for city, d in sorted(results.items(), key=lambda x: x[1].get("distance_km", 0)):
        min_ms = d.get("min_ms")
        mean_ms = d.get("mean_ms")
        dist  = d.get("distance_km", 0)
        med   = d.get("median_ms")
        loss  = d.get("loss_pct")
        theor = d.get("theoretical_min_ms")
        ratio = d.get("inefficiency_ratio")
        flag  = " ⚠️" if d.get("high_inefficiency") else ""
        print(
            f"{city:<14} "
            f"{(f'{min_ms:.1f}' if min_ms is not None else 'N/A'):>8} "
            f"{(f'{mean_ms:.1f}' if mean_ms is not None else 'N/A'):>9} "
            f"{(f'{med:.1f}' if med is not None else 'N/A'):>10} "
            f"{(f'{loss:.0f}' if loss is not None else 'N/A'):>7} "
            f"{dist:>8.0f} "
            f"{(f'{theor:.1f}' if theor is not None else 'N/A'):>10} "
            f"{(f'{ratio:.2f}' if ratio is not None else 'N/A'):>7}{flag}"
        )

    make_plots(results)

if __name__ == "__main__":
    main()
