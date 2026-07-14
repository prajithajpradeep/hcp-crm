"""
hcp_directory.py
----------------
A small pretend "directory" of Healthcare Professionals (doctors).

In a real company this would come from a big database, but for this assignment a
simple Python dictionary is enough. The `search_hcp` tool looks people up here.
"""

HCP_DIRECTORY = {
    "dr. smith": {
        "name": "Dr. Smith",
        "specialty": "Cardiology",
        "hospital": "City General Hospital",
        "preferred_product": "Prodo-X",
        "last_interaction": "2025-03-10",
    },
    "dr. john": {
        "name": "Dr. John",
        "specialty": "Endocrinology",
        "hospital": "Sunrise Medical Center",
        "preferred_product": "Glyco-Plus",
        "last_interaction": "2025-02-22",
    },
    "dr. lee": {
        "name": "Dr. Lee",
        "specialty": "Oncology",
        "hospital": "Hope Cancer Institute",
        "preferred_product": "Onco-Care",
        "last_interaction": "2025-04-01",
    },
}


def find_hcp(name: str):
    """Return the HCP record if we can find a match, else None.

    We do a loose match so 'smith', 'Dr Smith', 'dr. smith' all work.
    """
    if not name:
        return None
    key = name.strip().lower().replace("dr ", "dr. ")
    # exact key match first
    if key in HCP_DIRECTORY:
        return HCP_DIRECTORY[key]
    # otherwise try to find the surname inside any key
    for k, record in HCP_DIRECTORY.items():
        if key in k or k in key:
            return record
    return None
