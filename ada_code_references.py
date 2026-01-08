"""
ADA Code References Database

Official ADA codes from the 2010 ADA Standards for Accessible Design.
Source: U.S. Department of Justice
URL: https://www.ada.gov/law-and-regs/design-standards/2010-stds/

All codes are from the official federal regulations.
"""

ADA_CODES = {
    # DOORS & ENTRANCES (Section 404)
    "404.2.3": {
        "title": "Clear Width",
        "requirement": "Door openings shall provide a clear width of 32 inches (815 mm) minimum",
        "measurement": "32 inches minimum",
        "section": "404.2.3 - Doors, Doorways, and Gates",
        "source": "2010 ADA Standards Section 404.2.3",
        "url": "https://www.ada.gov/law-and-regs/design-standards/2010-stds/#section-404"
    },
    
    "404.2.5": {
        "title": "Thresholds",
        "requirement": "Thresholds, if provided at doorways, shall be 1/2 inch (13 mm) high maximum",
        "measurement": "0.5 inches maximum",
        "section": "404.2.5 - Doors, Doorways, and Gates",
        "source": "2010 ADA Standards Section 404.2.5",
        "url": "https://www.ada.gov/law-and-regs/design-standards/2010-stds/#section-404"
    },
    
    "404.2.7": {
        "title": "Door Hardware",
        "requirement": "Handles, pulls, latches, locks, and other operable parts shall be operable with one hand and shall not require tight grasping, pinching, or twisting of the wrist",
        "measurement": "Operable with closed fist",
        "section": "404.2.7 - Doors, Doorways, and Gates",
        "source": "2010 ADA Standards Section 404.2.7",
        "url": "https://www.ada.gov/law-and-regs/design-standards/2010-stds/#section-404"
    },
    
    # PARKING SPACES (Section 502)
    "502.2": {
        "title": "Vehicle Spaces",
        "requirement": "Car parking spaces shall be 96 inches (2440 mm) wide minimum",
        "measurement": "96 inches (8 feet) minimum width",
        "section": "502.2 - Parking Spaces",
        "source": "2010 ADA Standards Section 502.2",
        "url": "https://www.ada.gov/law-and-regs/design-standards/2010-stds/#section-502"
    },
    
    "502.3": {
        "title": "Access Aisle",
        "requirement": "Access aisles serving parking spaces shall be 60 inches (1525 mm) wide minimum",
        "measurement": "60 inches (5 feet) minimum width",
        "section": "502.3 - Parking Spaces",
        "source": "2010 ADA Standards Section 502.3",
        "url": "https://www.ada.gov/law-and-regs/design-standards/2010-stds/#section-502"
    },
    
    "502.4": {
        "title": "Floor and Ground Surfaces",
        "requirement": "Parking spaces and access aisles shall comply with Section 302 (stable, firm, and slip resistant)",
        "measurement": "Level surface, max slope 1:48",
        "section": "502.4 - Parking Spaces",
        "source": "2010 ADA Standards Section 502.4",
        "url": "https://www.ada.gov/law-and-regs/design-standards/2010-stds/#section-502"
    },
    
    "502.6": {
        "title": "Identification (Signage)",
        "requirement": "Parking space identification signs shall include the International Symbol of Accessibility and shall be 60 inches (1525 mm) minimum above the finish floor or ground surface",
        "measurement": "Sign at 60 inches minimum height",
        "section": "502.6 - Parking Spaces",
        "source": "2010 ADA Standards Section 502.6",
        "url": "https://www.ada.gov/law-and-regs/design-standards/2010-stds/#section-502"
    },
    
    # ACCESSIBLE ROUTES (Section 403)
    "403.5.1": {
        "title": "Clear Width",
        "requirement": "The clear width of walking surfaces shall be 36 inches (915 mm) minimum",
        "measurement": "36 inches minimum continuous width",
        "section": "403.5.1 - Walking Surfaces",
        "source": "2010 ADA Standards Section 403.5.1",
        "url": "https://www.ada.gov/law-and-regs/design-standards/2010-stds/#section-403"
    },
    
    # PROTRUDING OBJECTS (Section 307)
    "307": {
        "title": "Protruding Objects",
        "requirement": "Objects with leading edges more than 27 inches and not more than 80 inches above the floor shall protrude 4 inches maximum into the circulation path",
        "measurement": "4 inches maximum protrusion",
        "section": "307 - Protruding Objects",
        "source": "2010 ADA Standards Section 307",
        "url": "https://www.ada.gov/law-and-regs/design-standards/2010-stds/#section-307"
    },
    
    # FLOOR SURFACES (Section 302)
    "302": {
        "title": "Floor or Ground Surfaces",
        "requirement": "Floor and ground surfaces shall be stable, firm, and slip resistant",
        "measurement": "Stable, firm, slip-resistant",
        "section": "302 - Floor or Ground Surfaces",
        "source": "2010 ADA Standards Section 302",
        "url": "https://www.ada.gov/law-and-regs/design-standards/2010-stds/#section-302"
    },
    
    # CHANGES IN LEVEL (Section 303)
    "303": {
        "title": "Changes in Level",
        "requirement": "Changes in level up to 1/4 inch may be vertical. Changes between 1/4 inch and 1/2 inch shall be beveled",
        "measurement": "0.25 inch max vertical, 0.5 inch max with bevel",
        "section": "303 - Changes in Level",
        "source": "2010 ADA Standards Section 303",
        "url": "https://www.ada.gov/law-and-regs/design-standards/2010-stds/#section-303"
    },
    
    # RAMPS (Section 405)
    "405.2": {
        "title": "Slope",
        "requirement": "Ramp runs shall have a running slope not steeper than 1:12",
        "measurement": "1:12 ratio maximum (8.33%)",
        "section": "405.2 - Ramps",
        "source": "2010 ADA Standards Section 405.2",
        "url": "https://www.ada.gov/law-and-regs/design-standards/2010-stds/#section-405"
    },
    
    "405.5": {
        "title": "Clear Width",
        "requirement": "The clear width of a ramp run shall be 36 inches (915 mm) minimum",
        "measurement": "36 inches minimum",
        "section": "405.5 - Ramps",
        "source": "2010 ADA Standards Section 405.5",
        "url": "https://www.ada.gov/law-and-regs/design-standards/2010-stds/#section-405"
    },
    
    "405.7": {
        "title": "Landings",
        "requirement": "Ramps shall have landings at the top and bottom of each ramp run. Landings shall be 60 inches minimum in length",
        "measurement": "60 inches minimum landing length",
        "section": "405.7 - Ramps",
        "source": "2010 ADA Standards Section 405.7",
        "url": "https://www.ada.gov/law-and-regs/design-standards/2010-stds/#section-405"
    },
    
    "405.8": {
        "title": "Handrails",
        "requirement": "Ramp runs with a rise greater than 6 inches shall have handrails complying with Section 505",
        "measurement": "Required if rise > 6 inches",
        "section": "405.8 - Ramps",
        "source": "2010 ADA Standards Section 405.8",
        "url": "https://www.ada.gov/law-and-regs/design-standards/2010-stds/#section-405"
    },
    
    "405.9": {
        "title": "Edge Protection",
        "requirement": "Edge protection shall be provided on each side of ramp runs and at each side of ramp landings",
        "measurement": "Curb or barrier required",
        "section": "405.9 - Ramps",
        "source": "2010 ADA Standards Section 405.9",
        "url": "https://www.ada.gov/law-and-regs/design-standards/2010-stds/#section-405"
    },
    
    # SIGNAGE (Section 703)
    "703.2": {
        "title": "Raised Characters",
        "requirement": "Raised characters shall be 5/8 inch (16 mm) minimum in height and 2 inches (51 mm) maximum in height",
        "measurement": "0.625 - 2 inches height",
        "section": "703.2 - Signs",
        "source": "2010 ADA Standards Section 703.2",
        "url": "https://www.ada.gov/law-and-regs/design-standards/2010-stds/#section-703"
    },
    
    "703.4": {
        "title": "Installation Height",
        "requirement": "Signs shall be located 48 inches minimum above the finish floor measured to the baseline of the lowest character",
        "measurement": "48-60 inches above floor",
        "section": "703.4 - Signs",
        "source": "2010 ADA Standards Section 703.4",
        "url": "https://www.ada.gov/law-and-regs/design-standards/2010-stds/#section-703"
    },
    
    "703.5": {
        "title": "Visual Characters",
        "requirement": "Characters and their background shall have a non-glare finish and contrast with light characters on dark background or vice versa",
        "measurement": "High contrast required",
        "section": "703.5 - Signs",
        "source": "2010 ADA Standards Section 703.5",
        "url": "https://www.ada.gov/law-and-regs/design-standards/2010-stds/#section-703"
    }
}


def get_ada_code(code: str) -> dict:
    """
    Get ADA code information.
    
    Args:
        code: ADA code number (e.g., "404.2.3")
        
    Returns:
        Dictionary with code information, or None if not found
    """
    return ADA_CODES.get(code)


def get_all_codes() -> list:
    """Get list of all ADA codes in the database."""
    return list(ADA_CODES.keys())


def search_codes(keyword: str) -> list:
    """
    Search for ADA codes by keyword.
    
    Args:
        keyword: Search term (e.g., "door", "parking", "ramp")
        
    Returns:
        List of matching ADA codes
    """
    keyword_lower = keyword.lower()
    matches = []
    
    for code, info in ADA_CODES.items():
        if (keyword_lower in info['title'].lower() or 
            keyword_lower in info['requirement'].lower() or
            keyword_lower in info['section'].lower()):
            matches.append(code)
    
    return matches


# Test function
if __name__ == "__main__":
    print("=" * 70)
    print("ADA Code References - Test")
    print("=" * 70)
    
    # Test getting a specific code
    print("\nTest 1: Get door width code")
    door_code = get_ada_code("404.2.3")
    print(f"Code: 404.2.3")
    print(f"Title: {door_code['title']}")
    print(f"Requirement: {door_code['requirement']}")
    print(f"Measurement: {door_code['measurement']}")
    
    # Test search
    print("\n\nTest 2: Search for 'parking' codes")
    parking_codes = search_codes("parking")
    print(f"Found {len(parking_codes)} parking-related codes:")
    for code in parking_codes:
        info = get_ada_code(code)
        print(f"  - {code}: {info['title']}")
    
    # Show all codes
    print(f"\n\nTotal ADA codes in database: {len(get_all_codes())}")
    
    print("\n✓ ADA code references test complete!")
