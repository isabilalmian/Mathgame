from __future__ import annotations

from typing import Any


ELEMENT_ATOMIC_NUMBERS = {
    "Hydrogen": 1,
    "Helium": 2,
    "Lithium": 3,
    "Carbon": 6,
    "Nitrogen": 7,
    "Oxygen": 8,
    "Neon": 10,
    "Sodium": 11,
    "Magnesium": 12,
    "Aluminium": 13,
    "Silicon": 14,
    "Phosphorus": 15,
    "Sulfur": 16,
    "Chlorine": 17,
    "Argon": 18,
    "Potassium": 19,
    "Calcium": 20,
    "Iron": 26,
    "Copper": 29,
    "Zinc": 30,
}


BIOLOGY_FACTS: list[tuple[str, Any, str]] = [
    ("How many bones does an adult human body have?", 206, "An adult human has 206 bones."),
    ("How many chambers does the human heart have?", 4, "The heart has 4 chambers."),
    ("Which organ pumps blood through the body?", "heart", "The heart pumps blood through the body."),
    ("Which gas do plants absorb for photosynthesis?", "carbon dioxide", "Plants absorb carbon dioxide."),
    ("Which organ is primarily responsible for gas exchange?", "lungs", "The lungs exchange oxygen and carbon dioxide."),
    ("What is the largest organ in the human body?", "skin", "The skin is the largest organ."),
    ("Which blood cells help fight infection?", "white blood cells", "White blood cells fight infection."),
    ("What is the basic unit of life?", "cell", "The cell is the basic unit of life."),
    ("How many pairs of chromosomes do humans usually have?", 23, "Humans usually have 23 chromosome pairs."),
    ("Which part of a plant absorbs water from soil?", "roots", "Roots absorb water and minerals from soil."),
]


ASTRONOMY_FACTS: list[tuple[str, Any, str]] = [
    ("Which planet is known as the Red Planet?", "mars", "Mars is often called the Red Planet."),
    ("Which planet is the largest in our solar system?", "jupiter", "Jupiter is the largest planet in our solar system."),
    ("What is the name of Earth's natural satellite?", "moon", "Earth's natural satellite is the Moon."),
    ("What galaxy contains our solar system?", "milky way", "Our solar system is in the Milky Way galaxy."),
    ("How long does Earth take to orbit the Sun (in days)?", 365, "Earth takes about 365 days to orbit the Sun."),
]


COUNTRY_CAPITALS = {
    "Germany": "Berlin",
    "France": "Paris",
    "Spain": "Madrid",
    "Italy": "Rome",
    "Portugal": "Lisbon",
    "Poland": "Warsaw",
    "Japan": "Tokyo",
    "India": "New Delhi",
    "Egypt": "Cairo",
    "Canada": "Ottawa",
    "Brazil": "Brasilia",
    "Australia": "Canberra",
}


COUNTRY_CONTINENT = {
    "Germany": "Europe",
    "Japan": "Asia",
    "Brazil": "South America",
    "Egypt": "Africa",
    "Australia": "Oceania",
    "Canada": "North America",
}


HISTORY_EVENTS: list[tuple[str, int]] = [
    ("the fall of the Berlin Wall", 1989),
    ("the first Moon landing", 1969),
    ("World War I began", 1914),
    ("World War II ended", 1945),
    ("the United Nations was founded", 1945),
    ("the French Revolution began", 1789),
    ("the Declaration of Independence (USA)", 1776),
    ("the invention of the World Wide Web", 1989),
    ("the Magna Carta was signed", 1215),
    ("the first modern Olympic Games", 1896),
]


PLANETS_FROM_SUN = [
    "Mercury",
    "Venus",
    "Earth",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
]

