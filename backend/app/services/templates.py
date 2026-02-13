TEMPLATES = [
    {
        "key": "problem-product-benefit",
        "name": "Problem → Product → Benefit",
        "duration_seconds": 10,
        "scene_count": 4,
        "config": {
            "transitions": "fade",
            "watermark_optional": True,
            "end_card_optional": True,
            "timings": [2.5, 2.5, 2.5, 2.5],
            "scenes": ["problem", "product", "benefit", "cta"],
        },
    },
    {
        "key": "benefits-rapid-fire",
        "name": "3 Benefits Rapid Fire",
        "duration_seconds": 9,
        "scene_count": 5,
        "config": {
            "transitions": "slide",
            "watermark_optional": True,
            "end_card_optional": True,
            "timings": [1.8, 1.8, 1.8, 1.8, 1.8],
            "scenes": ["hook", "benefit1", "benefit2", "benefit3", "cta"],
        },
    },
    {
        "key": "unboxing-highlights",
        "name": "Unboxing / Feature Highlights",
        "duration_seconds": 11,
        "scene_count": 5,
        "config": {
            "transitions": "zoom",
            "watermark_optional": True,
            "end_card_optional": True,
            "timings": [2.2, 2.2, 2.2, 2.2, 2.2],
            "scenes": ["hook", "unbox", "feature1", "feature2", "cta"],
        },
    },
]
