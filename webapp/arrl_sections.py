SECTIONS = {
    "W0": [
        ("CO", "Colorado"), ("IA", "Iowa"), ("KS", "Kansas"),
        ("MN", "Minnesota"), ("MO", "Missouri"), ("NE", "Nebraska"),
        ("ND", "North Dakota"), ("SD", "South Dakota"),
    ],
    "W1": [
        ("CT", "Connecticut"), ("EMA", "Eastern Massachusetts"),
        ("ME", "Maine"), ("NH", "New Hampshire"), ("RI", "Rhode Island"),
        ("VT", "Vermont"), ("WMA", "Western Massachusetts"),
    ],
    "W2": [
        ("ENY", "Eastern New York"), ("NLI", "New York City/Long Island"),
        ("NNJ", "Northern New Jersey"), ("NNY", "Northern New York"),
        ("SNJ", "Southern New Jersey"), ("WNY", "Western New York"),
        ("VI", "US Virgin Islands (KP2)"),
    ],
    "W3": [
        ("DE", "Delaware"), ("EPA", "Eastern Pennsylvania"),
        ("MDC", "Maryland/DC"), ("WPA", "Western Pennsylvania"),
    ],
    "W4": [
        ("AL", "Alabama"), ("GA", "Georgia"), ("KY", "Kentucky"),
        ("NC", "North Carolina"), ("NFL", "Northern Florida"),
        ("SC", "South Carolina"), ("SFL", "Southern Florida"),
        ("TN", "Tennessee"), ("VA", "Virginia"), ("WCF", "West Central Florida"),
        ("PR", "Puerto Rico (KP4)"),
    ],
    "W5": [
        ("AR", "Arkansas"), ("LA", "Louisiana"), ("MS", "Mississippi"),
        ("NM", "New Mexico"), ("NTX", "North Texas"), ("OK", "Oklahoma"),
        ("STX", "South Texas"), ("WTX", "West Texas"),
    ],
    "W6": [
        ("EB", "East Bay"), ("LAX", "Los Angeles"), ("ORG", "Orange"),
        ("SB", "Santa Barbara"), ("SCV", "Santa Clara Valley"),
        ("SDG", "San Diego"), ("SF", "San Francisco"),
        ("SJV", "San Joaquin Valley"), ("SV", "Sacramento Valley"),
        ("PAC", "Pacific HI/Samoa/Guam (KH6)"),
    ],
    "W7": [
        ("AK", "Alaska (KL7)"), ("AZ", "Arizona"), ("EWA", "Eastern Washington"),
        ("ID", "Idaho"), ("MT", "Montana"), ("NV", "Nevada"),
        ("OR", "Oregon"), ("UT", "Utah"), ("WWA", "Western Washington"),
        ("WY", "Wyoming"),
    ],
    "W8": [
        ("MI", "Michigan"), ("OH", "Ohio"), ("WV", "West Virginia"),
    ],
    "W9": [
        ("IL", "Illinois"), ("IN", "Indiana"), ("WI", "Wisconsin"),
    ],
    "VE": [
        ("AB", "Alberta (VA6/VE6)"), ("BC", "British Columbia (VA7/VE7)"), ("MB", "Manitoba (VA4/VE4)"),
        ("NB", "New Brunswick (VE9)"), ("NL", "Newfoundland/Labrador (VO)"),
        ("NS", "Nova Scotia (VA1/VE1)"), ("ONE", "Ontario East (VA3/VE3)"), ("ONN", "Ontario North (VE3/VA3)"),
        ("ONS", "Ontario South (VA3/VE3)"), ("PE", "Prince Edward Island (VY2/CY9)"),
        ("GTA", "Greater Toronto Area (VA3/VE3)"),
        ("QC", "Quebec (VA2/VE2)"), ("SK", "Saskatchewan (VA4/VE5)"), ("TER", "Northern Territories (VY1/VE8/VY0)"),
        ("MAR", "Canadian Maritime (VE0)"),
        ("DX", "Not US or Canadia"),
    ],
}

BAND_NAMES = {
    "1": "160m", "1.8": "160m", "3": "80m", "3.5": "80m",
    "5": "60m", "7": "40m", "10": "30m", "14": "20m",
    "18": "17m", "21": "15m", "24": "12m", "28": "10m",
    "50": "6m", "144": "2m", "222": "1.25m", "432": "70cm",
    "902": "33cm", "1240": "23cm",
}

ALL_SECTIONS = [(abbr, name) for sections in SECTIONS.values() for abbr, name in sections]
