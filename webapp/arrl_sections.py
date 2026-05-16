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
    ],
    "W5": [
        ("AR", "Arkansas"), ("LA", "Louisiana"), ("MS", "Mississippi"),
        ("NM", "New Mexico"), ("NT", "North Texas"), ("OK", "Oklahoma"),
        ("STX", "South Texas"), ("WTX", "West Texas"),
    ],
    "W6": [
        ("EB", "East Bay"), ("LAX", "Los Angeles"), ("ORG", "Orange"),
        ("SB", "Santa Barbara"), ("SCV", "Santa Clara Valley"),
        ("SDG", "San Diego"), ("SF", "San Francisco"),
        ("SJV", "San Joaquin Valley"), ("SV", "Sacramento Valley"),
        ("PAC", "Pacific"),
    ],
    "W7": [
        ("AK", "Alaska"), ("AZ", "Arizona"), ("EWA", "Eastern Washington"),
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
        ("AB", "Alberta"), ("BC", "British Columbia"), ("MB", "Manitoba"),
        ("NB", "New Brunswick"), ("NL", "Newfoundland/Labrador"),
        ("NS", "Nova Scotia"), ("ONE", "Ontario East"), ("ONN", "Ontario North"),
        ("ONS", "Ontario South"), ("PE", "Prince Edward Island"),
        ("QC", "Quebec"), ("SK", "Saskatchewan"), ("TER", "Territories"),
    ],
}

BAND_NAMES = {
    "1.8": "160m", "3.5": "80m", "7": "40m", "14": "20m",
    "21": "15m", "28": "10m", "50": "6m", "144": "2m",
    "222": "1.25m", "432": "70cm", "902": "33cm", "1240": "23cm",
}

ALL_SECTIONS = [(abbr, name) for sections in SECTIONS.values() for abbr, name in sections]
