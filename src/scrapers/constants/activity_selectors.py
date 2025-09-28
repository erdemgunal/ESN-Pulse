"""
CSS selectors for activity parsing from activities.esn.org platform.
"""

ACTIVITY_SELECTORS = {
    "title": {
        "primary": ".block--eg-activities-theme-page-title h1 span",
        "fallback": "h1"
    },
    "description": [
        ".ct-physical-activity__field-ct-act-description .field__item",
        ".activity__field-ct-act-description .field__item"
    ],
    "dates": {
        "primary": ".field-top-wrapper.ct-physical-activity__field-ct-act-dates .highlight-data-text span",
        "fallback": ".highlight-dates-single span"
    },
    "location": [
        ".field-top-wrapper.ct-physical-activity__field-ct-act-location .highlight-data-text span",
        ".field-top-wrapper.activity__field-ct-act-location .highlight-data-text span",
        ".highlight-data-text span"
    ],
    "participants": {
        "primary": ".highlight-data-text-big",
        "fallback": ".highlight-data-number .highlight-data-text-big"
    },
    "activity_type": {
        "primary": ".ct-physical-activity__field-ct-act-types .field__item a",
        "fallback": ".activity-types .activity-type a"
    },
    "organisers": {
        "primary": ".pseudo__items.pseudo__organisers a",
        "fallback": ".pseudo__organisers .pseudo__organiser a"
    },
    "causes": {
        "primary": ".activity-cause a",
        "fallback": ".activity-causes .activity-label a"
    },
    "sdgs": ".field-sdgs-wrapper img",
    "objectives": ".activity__objectives .field__item span",
    "activity_goal": [
        ".ct-physical-activity__field-ct-act-goal-activity .field__item",
        ".activity__field-ct-act-goal-activity .field__item",
        ".ct-online-activity__field-ct-act-goal-activity .field__item"
    ],
    "activity_card_title": ".eg-c-card-title a",
    "last_page": "a[title='Go to last page']"
}