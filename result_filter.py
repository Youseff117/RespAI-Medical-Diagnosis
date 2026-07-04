"""
result_filter.py
=================
Clinical post-processing layer for RespAI's raw model predictions.

WHY THIS EXISTS
----------------
The raw output of analyze_results() can contain many "positive" findings at
once (5-7 diseases flagged in a single scan), which is not clinically
realistic. This module sits between the model output and *everything else*
(dashboard rendering + PDF report generation) so both consumers see the same,
already-filtered, clinically-structured list of findings:

    - Exactly ONE "primary" finding (the highest-probability disease that
      survives filtering).
    - Zero or more "associated" findings — findings that are clinically
      linked to the primary diagnosis per `clinical_associations`
      (e.g. Cardiomegaly commonly co-occurs with Pleural Effusion).
    - Zero or more "independent" findings — findings that are NOT linked to
      the primary diagnosis but are still strong enough (passed the
      threshold, not an overlap duplicate) to be clinically significant on
      their own. These are intentionally NOT deleted just because they
      aren't in the association map — a strong unrelated finding (e.g. a
      Pneumothorax found alongside Cardiomegaly) can be an independent
      emergency and must not be silently dropped.

    Only the DOMINANCE MARGIN rule (based on probability gap, not on
    map membership) can suppress secondary findings — if nothing comes
    close to the primary's probability, secondary findings are omitted
    because they're not meaningfully significant, not because they're
    "unrelated".

USAGE
-----
    from result_filter import apply_clinical_filtering

    raw_results = analyze_results(image)             # unchanged, existing call
    results = apply_clinical_filtering(raw_results)   # <-- single line

    # `results` is still a plain list (same shape as before), so nothing
    # downstream breaks. results[0] is always the primary diagnosis.
    # Each item now also carries a "relation" key:
    #   "primary"     -> the main diagnosis
    #   "associated"  -> clinically linked to the primary
    #   "independent" -> NOT linked to the primary, but still significant
    # Templates / PDF sections can use this key to render separate groups
    # ("Primary Diagnosis" / "Associated Findings" / "Other Significant
    # Findings") if desired — that's a presentation-layer decision left to
    # you; this module just guarantees the data is already correctly
    # classified and ordered.

All thresholds / rules below are defined in one CONFIG dict so they can be
tuned later without touching the filtering logic itself.
"""

from copy import deepcopy

# ─────────────────────────────────────────────────────────────────────────
# CONFIG — tune everything here, nothing else needs to change
# ─────────────────────────────────────────────────────────────────────────
DEFAULT_CONFIG = {
    # Minimum probability (same scale as your `probability` field — this
    # project uses 0-100, e.g. 99.7) for a disease to be considered at all.
    "disease_threshold": 50.0,

    # Max number of ASSOCIATED findings (clinically linked to primary).
    "max_associated": 2,

    # Max number of INDEPENDENT findings (unrelated to primary, but still
    # strong/significant on their own — e.g. a separate emergency finding).
    "max_independent": 1,

    # Safety cap on total items returned (primary + associated + independent).
    "max_total_results": 4,

    # If the primary finding beats the strongest remaining candidate
    # (associated OR independent) by at least this many points, we show
    # the primary ONLY, because nothing else is close enough to matter.
    # This is a probability-based decision — it does NOT depend on whether
    # the other finding is in the association map.
    "dominance_margin": 30.0,

    # If "No Finding" alone is at/above this probability, we consider the
    # scan normal and suppress every other disease entirely.
    "no_finding_name": "No Finding",
    "no_finding_threshold": 50.0,

    # Groups of diseases that are radiographically/clinically overlapping
    # (i.e. likely the SAME finding described two ways). Only the highest
    # probability member of each group survives — this is the ONLY rule
    # that removes a finding based on similarity; everything else that
    # passes the threshold is kept and classified (never silently dropped).
    "overlap_groups": [
        {"Pneumonia", "Infiltration", "Consolidation"},
        {"Mass", "Nodule"},
        {"Effusion", "Pleural Effusion"},
    ],

    # Clinical association map: primary_disease -> set of diseases commonly
    # seen ALONGSIDE it. Used only to LABEL a secondary finding as
    # "associated" vs "independent" — never to decide whether to keep it.
    "clinical_associations": {
        "Cardiomegaly": {"Effusion", "Pleural Effusion", "Edema", "Atelectasis"},
        "Edema": {"Cardiomegaly", "Effusion", "Pleural Effusion"},
        "Effusion": {"Atelectasis", "Consolidation", "Cardiomegaly", "Pneumonia"},
        "Pleural Effusion": {"Atelectasis", "Consolidation", "Cardiomegaly", "Pneumonia"},
        "Pneumonia": {"Consolidation", "Infiltration", "Effusion", "Pleural Effusion"},
        "Consolidation": {"Pneumonia", "Infiltration", "Effusion", "Pleural Effusion"},
        "Infiltration": {"Pneumonia", "Consolidation"},
        "Atelectasis": {"Effusion", "Pleural Effusion", "Pneumonia"},
        "Pneumothorax": {"Atelectasis"},
        "Fibrosis": {"Emphysema", "Pleural_Thickening"},
        "Emphysema": {"Fibrosis", "Pneumothorax"},
        "Mass": {"Nodule"},
        "Nodule": {"Mass"},
    },

    # Field-name flexibility: the filter will look for the disease name and
    # probability under any of these keys (first match wins).
    "name_keys": ["name", "disease", "label", "class_name", "disease_name", "name_en"],
    "probability_keys": ["probability", "prob", "score", "confidence"],
}


def get_default_config():
    """Return a fresh copy of the default config (safe to mutate)."""
    return deepcopy(DEFAULT_CONFIG)


# ─────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────
def _normalize(text):
    return str(text or "").strip().lower().replace("_", " ")


def _get_name(item, cfg):
    for key in cfg["name_keys"]:
        if key in item and item[key]:
            return item[key]
    return ""


def _get_prob(item, cfg):
    for key in cfg["probability_keys"]:
        if key in item and item[key] is not None:
            return float(item[key])
    return 0.0


def _find_group_index(name_norm, overlap_groups):
    for idx, group in enumerate(overlap_groups):
        normalized_group = {_normalize(g) for g in group}
        if name_norm in normalized_group:
            return idx
    return None


def _dedupe_overlapping(candidates, cfg):
    """
    candidates must already be sorted by probability, descending.
    Keeps only the highest-probability member of each overlap group.
    This is the ONLY step allowed to remove a finding based on similarity.
    """
    kept = []
    covered_groups = set()
    for item in candidates:
        name_norm = _normalize(_get_name(item, cfg))
        group_idx = _find_group_index(name_norm, cfg["overlap_groups"])
        if group_idx is not None:
            if group_idx in covered_groups:
                continue  # a stronger overlapping finding already kept
            covered_groups.add(group_idx)
        kept.append(item)
    return kept


def _associated_names_for(primary_name, cfg):
    """Normalized set of disease names considered 'associated' with this primary."""
    for key, values in cfg["clinical_associations"].items():
        if _normalize(key) == _normalize(primary_name):
            return {_normalize(v) for v in values}
    return set()


# ─────────────────────────────────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────────────────────────────────
def apply_clinical_filtering(results, config=None):
    """
    Apply the full clinical filtering pipeline to a list of raw model
    result dicts and return the final, report-ready list, structured as:

        [primary_finding, associated_finding(s)..., independent_finding(s)...]

    Each returned dict gets an extra "relation" key:
        "primary" | "associated" | "independent"

    Args:
        results: list of dicts, each representing one disease prediction.
        config:  optional dict to override any DEFAULT_CONFIG values for
                 this call only.

    Returns:
        list of dicts (possibly empty, or a single "No Finding" entry).
    """
    if not results:
        return results

    cfg = get_default_config()
    if config:
        cfg.update(config)

    # 1) Sort by probability, descending
    sorted_results = sorted(results, key=lambda r: _get_prob(r, cfg), reverse=True)

    # 2) "No Finding" dominance rule
    no_finding_norm = _normalize(cfg["no_finding_name"])
    no_finding_entry = next(
        (r for r in sorted_results if _normalize(_get_name(r, cfg)) == no_finding_norm),
        None,
    )
    if no_finding_entry and _get_prob(no_finding_entry, cfg) >= cfg["no_finding_threshold"]:
        result = dict(no_finding_entry)
        result["relation"] = "primary"
        return [result]

    # 3) Drop "No Finding" from the disease candidate pool
    candidates = [
        r for r in sorted_results
        if _normalize(_get_name(r, cfg)) != no_finding_norm
    ]

    # 4) Threshold filter
    candidates = [r for r in candidates if _get_prob(r, cfg) >= cfg["disease_threshold"]]
    if not candidates:
        return []

    # 5) Remove clinically overlapping/duplicate findings (only similarity-based removal)
    candidates = _dedupe_overlapping(candidates, cfg)
    if not candidates:
        return []

    # 6) Primary diagnosis = strongest remaining candidate
    primary = dict(candidates[0])
    primary["relation"] = "primary"
    primary_prob = _get_prob(primary, cfg)
    primary_name = _get_name(primary, cfg)

    remaining = candidates[1:]
    if not remaining:
        return [primary]

    # 7) Dominance rule — based purely on probability gap, NOT on whether
    #    the remaining finding is related to the primary.
    strongest_remaining_prob = _get_prob(remaining[0], cfg)
    if (primary_prob - strongest_remaining_prob) >= cfg["dominance_margin"]:
        return [primary]

    # 8) Classify every remaining candidate as associated or independent.
    #    Nothing is deleted here just for being "unrelated" — independent
    #    findings are kept because they may be a separate serious condition.
    allowed_associated_names = _associated_names_for(primary_name, cfg)

    secondary = []
    assoc_count = 0
    indep_count = 0
    for item in remaining:
        name_norm = _normalize(_get_name(item, cfg))
        if name_norm in allowed_associated_names:
            if assoc_count >= cfg["max_associated"]:
                continue
            tagged = dict(item)
            tagged["relation"] = "associated"
            secondary.append(tagged)
            assoc_count += 1
        else:
            if indep_count >= cfg["max_independent"]:
                continue
            tagged = dict(item)
            tagged["relation"] = "independent"
            secondary.append(tagged)
            indep_count += 1

    final_list = [primary] + secondary
    return final_list[: cfg["max_total_results"]]