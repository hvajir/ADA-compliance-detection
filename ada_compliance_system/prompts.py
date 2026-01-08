"""
Prompt Templates for ADA Compliance Analysis

This module contains specialized prompts for Claude to analyze different
types of accessibility features.

Key Concept - Prompt Engineering:
The quality of AI responses depends heavily on the prompt. Good prompts:
1. Provide context (you're an expert)
2. Be specific about what to check
3. Request structured output (JSON)
4. Include relevant standards/codes
"""

# Base system prompt - sets Claude's role
SYSTEM_PROMPT = """You are an ADA (Americans with Disabilities Act) compliance expert 
specializing in accessibility auditing for retail spaces. You analyze images to identify 
potential accessibility violations based on ADA standards.

Your analysis should be:
- Specific: Reference exact ADA codes when possible
- Practical: Focus on visually detectable issues
- Cautious: Note when precise measurements cannot be determined from images alone
- Helpful: Provide actionable recommendations

Remember: Visual analysis has limitations. Always recommend professional verification 
for critical measurements."""


def get_doorway_prompt() -> str:
    """
    Prompt for analyzing doorway/entrance accessibility.
    
    ADA Requirements (Summary):
    - Clear opening width: minimum 32 inches
    - Threshold: maximum 0.5 inches (1/2 inch)
    - Door hardware: operable with one hand, no tight grasping
    - Maneuvering clearance: depends on approach direction
    """
    return """Analyze this doorway/entrance for ADA compliance.

Check for these potential violations:

1. **Door Width**: Does the opening appear to be at least 32 inches clear width?
   - ADA Code: 404.2.3
   - Note: Cannot measure exactly from photo, but assess if it appears narrow

2. **Threshold**: Is there a visible threshold or step?
   - ADA Code: 404.2.5
   - Maximum allowed: 0.5 inches (1/2 inch)

3. **Door Hardware**: Can you see the door handle/hardware?
   - ADA Code: 404.2.7
   - Should be operable with one hand without tight grasping

4. **Approach Clearance**: Is there adequate space to approach and open the door?
   - ADA Code: 404.2.4

Provide your response in JSON format:
{
    "violations": [
        {
            "type": "Door Width" | "Threshold" | "Hardware" | "Clearance",
            "severity": "Critical" | "Moderate" | "Minor",
            "ada_code": "section number",
            "description": "brief description of the issue",
            "recommendation": "how to fix it",
            "confidence": 0.0 to 1.0
        }
    ],
    "overall_assessment": "brief summary",
    "notes": "any limitations or caveats about the analysis"
}

If the image quality is insufficient or the relevant features are not visible, 
indicate this in the notes and use lower confidence scores."""


def get_parking_prompt() -> str:
    """
    Prompt for analyzing parking area accessibility.
    
    ADA Requirements (Summary):
    - Accessible parking spaces: 96 inches minimum width
    - Access aisle: 60 inches minimum (96" for van-accessible)
    - Signage: Required at each space
    - Surface: Stable, firm, slip-resistant
    """
    return """Analyze this parking area for ADA compliance.

Check for these potential violations:

1. **Accessible Parking Signage**: Are there signs with the International Symbol of Accessibility?
   - ADA Code: 502.6
   - Required: Sign at each accessible space, minimum 60 inches above ground

2. **Parking Space Dimensions**: Do the spaces appear adequately sized?
   - ADA Code: 502.2
   - Standard: 96 inches (8 feet) wide minimum
   - Van-accessible: 132 inches (11 feet) wide

3. **Access Aisle**: Is there a marked access aisle adjacent to the space?
   - ADA Code: 502.3
   - Minimum width: 60 inches (5 feet)
   - Van-accessible: 96 inches (8 feet)

4. **Surface Condition**: Does the surface appear level and well-maintained?
   - ADA Code: 502.4
   - Maximum slope: 1:48 (2%)

5. **Location**: Is the accessible parking close to the accessible entrance?
   - ADA Code: 502.7

Provide your response in JSON format:
{
    "violations": [
        {
            "type": "Signage" | "Dimensions" | "Access Aisle" | "Surface" | "Location",
            "severity": "Critical" | "Moderate" | "Minor",
            "ada_code": "section number",
            "description": "brief description of the issue",
            "recommendation": "how to fix it",
            "confidence": 0.0 to 1.0
        }
    ],
    "overall_assessment": "brief summary",
    "notes": "any limitations or caveats"
}"""


def get_pathway_prompt() -> str:
    """
    Prompt for analyzing pathway/aisle accessibility.
    
    ADA Requirements (Summary):
    - Minimum width: 36 inches continuous
    - Passing space: 60 x 60 inches every 200 feet
    - No protruding objects
    - Changes in level: maximum 0.5 inches
    """
    return """Analyze this pathway/aisle for ADA compliance.

Check for these potential violations:

1. **Pathway Width**: Does the clear path appear to be at least 36 inches wide?
   - ADA Code: 403.5.1
   - Minimum: 36 inches continuous clear width

2. **Obstructions**: Are there any objects blocking or narrowing the path?
   - ADA Code: 307
   - Examples: displays, carts, merchandise, furniture

3. **Surface Condition**: Does the floor appear level and well-maintained?
   - ADA Code: 302
   - Should be stable, firm, and slip-resistant

4. **Protruding Objects**: Are there any objects protruding into the pathway?
   - ADA Code: 307.2
   - Objects can't protrude more than 4 inches if below 27 inches high

5. **Changes in Level**: Are there any visible steps, curbs, or level changes?
   - ADA Code: 303
   - Maximum: 0.5 inches, must be beveled if 0.25-0.5 inches

Provide your response in JSON format:
{
    "violations": [
        {
            "type": "Width" | "Obstruction" | "Surface" | "Protrusion" | "Level Change",
            "severity": "Critical" | "Moderate" | "Minor",
            "ada_code": "section number",
            "description": "brief description of the issue",
            "recommendation": "how to fix it",
            "confidence": 0.0 to 1.0
        }
    ],
    "overall_assessment": "brief summary",
    "notes": "any limitations or caveats"
}"""


def get_ramp_prompt() -> str:
    """
    Prompt for analyzing ramp accessibility.
    
    ADA Requirements (Summary):
    - Maximum slope: 1:12 (8.33%)
    - Minimum width: 36 inches
    - Handrails: Required if rise > 6 inches
    - Edge protection: Required
    """
    return """Analyze this ramp for ADA compliance.

Check for these potential violations:

1. **Ramp Slope**: Does the ramp appear to have a gentle slope?
   - ADA Code: 405.2
   - Maximum: 1:12 ratio (8.33% grade, or 1 inch rise per 12 inches run)
   - Steeper ramps are very obvious and difficult to navigate

2. **Width**: Does the ramp appear to be at least 36 inches wide?
   - ADA Code: 405.5
   - Minimum clear width: 36 inches

3. **Handrails**: Are there handrails on both sides?
   - ADA Code: 405.8
   - Required if rise is greater than 6 inches
   - Should be 34-38 inches above ramp surface

4. **Edge Protection**: Is there edge protection (curb or barrier)?
   - ADA Code: 405.9
   - Required to prevent wheelchairs from slipping off

5. **Surface**: Does the surface appear slip-resistant and well-maintained?
   - ADA Code: 405.4

6. **Landings**: Are there level landings at top and bottom?
   - ADA Code: 405.7
   - Minimum: 60 inches long

Provide your response in JSON format:
{
    "violations": [
        {
            "type": "Slope" | "Width" | "Handrails" | "Edge Protection" | "Surface" | "Landings",
            "severity": "Critical" | "Moderate" | "Minor",
            "ada_code": "section number",
            "description": "brief description of the issue",
            "recommendation": "how to fix it",
            "confidence": 0.0 to 1.0
        }
    ],
    "overall_assessment": "brief summary",
    "notes": "any limitations or caveats"
}"""


def get_signage_prompt() -> str:
    """
    Prompt for analyzing signage accessibility.
    
    ADA Requirements (Summary):
    - Raised characters: 5/8 to 2 inches high
    - Braille: Required for permanent room identification
    - Mounting height: 48-60 inches above floor
    - Color contrast: Required for visibility
    """
    return """Analyze this signage for ADA compliance.

Check for these potential violations:

1. **Braille**: Is there visible braille below the text?
   - ADA Code: 703.2
   - Required for permanent room/space identification signs

2. **Character Height**: Are the characters appropriately sized?
   - ADA Code: 703.5
   - Raised characters: 5/8 to 2 inches high
   - Visual characters: based on viewing distance

3. **Mounting Height**: Can you assess if the sign appears at proper height?
   - ADA Code: 703.4
   - Should be 48-60 inches above floor (to baseline of lowest character)

4. **Color Contrast**: Is there adequate contrast between text and background?
   - ADA Code: 703.5
   - Required for visual readability

5. **Finish**: Does the sign appear to have a non-glare finish?
   - ADA Code: 703.5

Provide your response in JSON format:
{
    "violations": [
        {
            "type": "Braille" | "Character Height" | "Mounting Height" | "Contrast" | "Finish",
            "severity": "Critical" | "Moderate" | "Minor",
            "ada_code": "section number",
            "description": "brief description of the issue",
            "recommendation": "how to fix it",
            "confidence": 0.0 to 1.0
        }
    ],
    "overall_assessment": "brief summary",
    "notes": "any limitations or caveats"
}"""


def get_general_prompt() -> str:
    """
    General prompt for objects that don't fit specific categories.
    
    Used for: furniture, obstacles, general accessibility features
    """
    return """Analyze this image for general ADA accessibility concerns.

Look for:

1. **Obstructions**: Objects blocking pathways or access
2. **Hazards**: Trip hazards, protruding objects, unstable items
3. **Reach Ranges**: Items placed too high or low for wheelchair users
   - Forward reach: 15-48 inches
   - Side reach: 9-54 inches (unobstructed)
4. **Clear Floor Space**: Adequate maneuvering space (30x48 inches minimum)
5. **Surface Conditions**: Level floors, slip resistance

Provide your response in JSON format:
{
    "violations": [
        {
            "type": "descriptive type",
            "severity": "Critical" | "Moderate" | "Minor",
            "ada_code": "section number if applicable",
            "description": "brief description of the issue",
            "recommendation": "how to fix it",
            "confidence": 0.0 to 1.0
        }
    ],
    "overall_assessment": "brief summary",
    "notes": "any limitations or caveats"
}

If no accessibility concerns are visible, return an empty violations array."""


# Mapping of object types to their specific prompts
PROMPT_MAPPING = {
    "door": get_doorway_prompt,
    "entrance": get_doorway_prompt,
    "car": get_parking_prompt,
    "truck": get_parking_prompt,
    "parking": get_parking_prompt,
    "person": get_pathway_prompt,  # Person in pathway context
    "chair": get_pathway_prompt,   # Potential obstruction
    "couch": get_pathway_prompt,   # Potential obstruction
    "bench": get_pathway_prompt,   # Potential obstruction
    "potted_plant": get_pathway_prompt,  # Potential obstruction
    "ramp": get_ramp_prompt,
    "sign": get_signage_prompt,
    "stop_sign": get_signage_prompt,
}


def get_prompt_for_object(object_name: str) -> str:
    """
    Get the appropriate prompt template for an object type.
    
    Args:
        object_name: Name of the detected object (e.g., "door", "car")
        
    Returns:
        Appropriate prompt string
        
    Why this function?
    - Central place to map objects to prompts
    - Easy to add new object types
    - Falls back to general prompt if no specific one exists
    """
    # Normalize object name (lowercase, handle variations)
    obj_lower = object_name.lower().strip()
    
    # Check if we have a specific prompt for this object
    if obj_lower in PROMPT_MAPPING:
        return PROMPT_MAPPING[obj_lower]()
    
    # Default to general prompt
    return get_general_prompt()


if __name__ == "__main__":
    """
    Demo: Show what prompts look like for different objects
    """
    print("=" * 70)
    print("ADA COMPLIANCE PROMPTS - Demo")
    print("=" * 70)
    
    test_objects = ["door", "car", "chair", "sign", "unknown_object"]
    
    for obj in test_objects:
        print(f"\n{'='*70}")
        print(f"OBJECT TYPE: {obj}")
        print('='*70)
        prompt = get_prompt_for_object(obj)
        # Show first 500 characters
        print(prompt[:500] + "...")
        print(f"\n(Total prompt length: {len(prompt)} characters)")
