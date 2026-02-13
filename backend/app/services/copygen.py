from __future__ import annotations

import re
from collections import Counter

from app.models import BrandVoice, Product

HOOKS = [
    "This tiny upgrade changes everything",
    "Stop scrolling if you want easier days",
    "The product everyone keeps asking about",
    "3 seconds to see why this sells out",
    "I wish I found this sooner",
    "From cluttered to clean instantly",
    "The simple fix for your daily frustration",
    "One product. Big difference.",
    "Proof that practical can look premium",
    "Watch this before your next checkout",
]

CTA_BY_TONE = {
    "minimalist": ["Shop the look", "Tap to explore"],
    "playful": ["Grab yours fast ✨", "Try it today 🎯"],
    "luxury": ["Discover the premium edit", "Own the upgrade"],
    "direct-response": ["Tap to buy now", "Get yours before it’s gone"],
}

HASHTAGS = ["#tiktokmademebuyit", "#productfind", "#smallbusiness", "#reels", "#shopnow"]


def extract_benefits(description: str, max_items: int = 3) -> list[str]:
    raw = re.split(r"[\.;\n]\s*", description)
    candidates = []
    for line in raw:
        line = line.strip(" -•")
        if 12 <= len(line) <= 90:
            candidates.append(line)
    if not candidates:
        words = [w for w in re.findall(r"[a-zA-Z]+", description.lower()) if len(w) > 4]
        common = [w for w, _ in Counter(words).most_common(max_items)]
        return [f"Built for {word}" for word in common] or ["Designed for everyday ease"]
    return candidates[:max_items]


def scrub_phrases(lines: list[str], banned: list[str]) -> list[str]:
    out = []
    for line in lines:
        cleaned = line
        for phrase in banned:
            cleaned = re.sub(re.escape(phrase), "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
        out.append(cleaned)
    return out


def generate_pack(product: Product, voice: BrandVoice, variant_index: int = 1) -> dict:
    benefits = extract_benefits(product.description)
    hook_offset = (variant_index - 1) % len(HOOKS)
    hooks = [HOOKS[hook_offset], HOOKS[(hook_offset + 3) % len(HOOKS)], HOOKS[(hook_offset + 6) % len(HOOKS)]]
    ctas = voice.preferred_ctas or CTA_BY_TONE.get(voice.tone, CTA_BY_TONE["minimalist"])
    ctas = scrub_phrases(ctas, voice.banned_phrases)
    hooks = scrub_phrases(hooks, voice.banned_phrases)
    benefits = scrub_phrases(benefits, voice.banned_phrases)

    caption = f"{hooks[0]} — {product.title}. {benefits[0]}"
    return {
        "hooks": hooks,
        "benefits": benefits,
        "ctas": ctas,
        "hashtags": HASHTAGS,
        "caption": caption[:220],
    }
