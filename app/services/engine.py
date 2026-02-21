from __future__ import annotations

import math
import random
import re
import uuid
from typing import Any, Callable

from app.config import MAX_AGE, MIN_AGE
from app.models import Grade, Question
from app.services.question_bank import (
    ASTRONOMY_FACTS,
    BIOLOGY_FACTS,
    COUNTRY_CAPITALS,
    COUNTRY_CONTINENT,
    ELEMENT_ATOMIC_NUMBERS,
    HISTORY_EVENTS,
    PLANETS_FROM_SUN,
)


class GameEngine:
    def get_grade_from_age(self, age: int) -> Grade:
        if age < 8:
            return 4
        if age >= 19:
            return "university"
        if age >= 18:
            return 12
        if age >= 17:
            return 11
        if age >= 16:
            return 10
        if age >= 15:
            return 9
        if age >= 14:
            return 8
        if age >= 12:
            return 7
        if age >= 11:
            return 6
        if age >= 10:
            return 5
        return 4

    def is_valid_age(self, age: int) -> bool:
        return MIN_AGE <= age <= MAX_AGE

    def normalize_text(self, raw: str) -> str:
        raw = (raw or "").strip().lower()
        raw = re.sub(r"\s+", " ", raw)
        return raw

    def parse_number(self, raw: str) -> float | None:
        candidate = (raw or "").strip().replace(",", ".")
        if candidate in {"", "-"}:
            return None
        try:
            value = float(candidate)
        except ValueError:
            return None
        if not math.isfinite(value):
            return None
        return value

    def format_answer(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, int):
            return str(value)
        if isinstance(value, float):
            if value.is_integer():
                return str(int(value))
            return f"{value:.2f}".rstrip("0").rstrip(".")
        return str(value)

    def answers_match(self, user_raw: str, correct: Any) -> bool:
        if isinstance(correct, str):
            return self.normalize_text(user_raw) == self.normalize_text(correct)

        numeric = self.parse_number(user_raw)
        if numeric is None:
            return False
        precision = 5
        scale = 10**precision
        return round(numeric * scale) == round(float(correct) * scale)

    def generate_question(
        self,
        subject: str,
        age: int,
        rng: random.Random,
        used_prompts: set[str],
    ) -> Question:
        generator = self._resolve_generator(subject)
        prompt = ""
        answer: Any = ""
        explanation = ""
        diagram_html: str | None = None

        # Try to avoid duplicates within one session/subject.
        for _ in range(24):
            prompt, answer, explanation, diagram_html = generator(age, rng)
            if prompt not in used_prompts:
                used_prompts.add(prompt)
                break

        return Question(
            id=uuid.uuid4().hex[:12],
            subject=subject,
            prompt=prompt,
            answer=answer,
            explanation=explanation,
            diagram_html=diagram_html,
        )

    def _resolve_generator(
        self, subject: str
    ) -> Callable[[int, random.Random], tuple[str, Any, str, str | None]]:
        mapping = {
            "maths": self._generate_maths,
            "chemistry": self._generate_chemistry,
            "biology": self._generate_biology,
            "physics": self._generate_physics,
            "astronomy": self._generate_astronomy,
            "geography": self._generate_geography,
            "history": self._generate_history,
        }
        return mapping.get(subject, self._generate_maths)

    def _grade_num(self, grade: Grade) -> int:
        if grade == "university":
            return 13
        return int(grade)

    def _generate_maths(
        self, age: int, rng: random.Random
    ) -> tuple[str, Any, str, str | None]:
        grade = self._grade_num(self.get_grade_from_age(age))
        kinds = ["arithmetic"]
        if grade >= 6:
            kinds.extend(["stats", "geometry"])
        if grade >= 7:
            kinds.append("algebra")
        if grade >= 9:
            kinds.append("trigonometry")

        kind = rng.choice(kinds)
        if kind == "stats":
            prompt, answer, explanation = self._math_stats(rng)
            return prompt, answer, explanation, None
        if kind == "geometry":
            prompt, answer, explanation = self._math_geometry(grade, rng)
            return prompt, answer, explanation, None
        if kind == "algebra":
            prompt, answer, explanation = self._math_algebra(rng)
            return prompt, answer, explanation, None
        if kind == "trigonometry":
            prompt, answer, explanation = self._math_trigonometry(rng)
            return prompt, answer, explanation, None

        prompt, answer, explanation = self._math_arithmetic(grade, rng)
        return prompt, answer, explanation, None

    def _math_arithmetic(
        self, grade: int, rng: random.Random
    ) -> tuple[str, Any, str]:
        if grade <= 4:
            max_n = 50
            ops = ["+", "-", "*", "/"]
            mult_max = 12
            div_max = 12
        elif grade <= 5:
            max_n = 100
            ops = ["+", "-", "*", "/"]
            mult_max = 15
            div_max = 20
        elif grade <= 6:
            max_n = 500
            ops = ["+", "-", "*", "/"]
            mult_max = 25
            div_max = 30
        else:
            max_n = 5000
            ops = ["+", "-", "*", "/"]
            mult_max = 50
            div_max = 80

        op = rng.choice(ops)
        if op == "+":
            a = rng.randint(1, max_n)
            b = rng.randint(1, max_n)
            answer = a + b
            prompt = f"{a} + {b}"
            explanation = f"Add the numbers: {a} + {b} = {answer}."
        elif op == "-":
            a = rng.randint(1, max_n)
            b = rng.randint(1, max_n)
            if b > a:
                a, b = b, a
            answer = a - b
            prompt = f"{a} - {b}"
            explanation = f"Subtract the smaller number from the larger one: {a} - {b} = {answer}."
        elif op == "*":
            a = rng.randint(2, mult_max)
            b = rng.randint(2, mult_max)
            answer = a * b
            prompt = f"{a} * {b}"
            explanation = f"Multiplication gives {a} * {b} = {answer}."
        else:
            divisor = rng.randint(2, div_max)
            quotient = rng.randint(2, max(2, max_n // divisor))
            dividend = divisor * quotient
            answer = quotient
            prompt = f"{dividend} / {divisor}"
            explanation = (
                f"Division is the inverse of multiplication: {divisor} * {quotient} = {dividend}, "
                f"so {dividend} / {divisor} = {quotient}."
            )
        return prompt, answer, explanation

    def _math_stats(self, rng: random.Random) -> tuple[str, Any, str]:
        data_len = rng.randint(4, 6)
        data = sorted(rng.randint(2, 50) for _ in range(data_len))
        kind = rng.choice(["mean", "median", "range", "mode"])

        if kind == "mode":
            if len(set(data)) == len(data):
                data[rng.randint(0, data_len - 1)] = data[0]
                data.sort()
            counts: dict[int, int] = {}
            for value in data:
                counts[value] = counts.get(value, 0) + 1
            answer = max(counts, key=counts.get)
            explanation = f"The mode is the value that appears most often. In {data}, that is {answer}."
            prompt = f"What is the mode of: {', '.join(map(str, data))}?"
            return prompt, answer, explanation

        if kind == "mean":
            total = sum(data)
            answer = round(total / len(data), 2)
            explanation = (
                f"Mean = sum / count = {total} / {len(data)} = {self.format_answer(answer)}."
            )
            prompt = f"What is the mean of: {', '.join(map(str, data))}?"
            return prompt, answer, explanation

        if kind == "median":
            mid = len(data) // 2
            if len(data) % 2 == 1:
                answer = data[mid]
            else:
                answer = round((data[mid - 1] + data[mid]) / 2, 2)
            explanation = f"The median is the middle value of the sorted list {data}: {self.format_answer(answer)}."
            prompt = f"What is the median of: {', '.join(map(str, data))}?"
            return prompt, answer, explanation

        answer = data[-1] - data[0]
        explanation = f"Range = max - min = {data[-1]} - {data[0]} = {answer}."
        prompt = f"What is the range of: {', '.join(map(str, data))}?"
        return prompt, answer, explanation

    def _math_geometry(self, grade: int, rng: random.Random) -> tuple[str, Any, str]:
        kinds = ["rectangle_area", "rectangle_perimeter", "triangle_angle"]
        if grade >= 7:
            kinds.extend(["circle_area", "circle_circumference"])
        if grade >= 8:
            kinds.append("box_volume")
        kind = rng.choice(kinds)

        if kind == "rectangle_area":
            w = rng.randint(2, 25)
            h = rng.randint(2, 25)
            answer = w * h
            return (
                f"What is the area of a rectangle with width {w} and height {h}?",
                answer,
                f"Area = width * height = {w} * {h} = {answer}.",
            )

        if kind == "rectangle_perimeter":
            w = rng.randint(2, 20)
            h = rng.randint(2, 20)
            answer = 2 * (w + h)
            return (
                f"What is the perimeter of a rectangle with width {w} and height {h}?",
                answer,
                f"Perimeter = 2 * (w + h) = 2 * ({w} + {h}) = {answer}.",
            )

        if kind == "triangle_angle":
            a = rng.randint(30, 100)
            b = rng.randint(30, 100)
            missing = 180 - a - b
            if missing <= 0:
                return self._math_geometry(grade, rng)
            return (
                f"In a triangle, two angles are {a} and {b}. What is the third angle?",
                missing,
                f"Angles in a triangle sum to 180. So 180 - ({a} + {b}) = {missing}.",
            )

        if kind == "circle_area":
            r = rng.randint(2, 12)
            answer = round(math.pi * r * r, 2)
            return (
                f"What is the area of a circle with radius {r}? (Use pi, round to 2 decimals.)",
                answer,
                f"Area = pi * r^2 = pi * {r}^2 = {self.format_answer(answer)}.",
            )

        if kind == "circle_circumference":
            r = rng.randint(2, 12)
            answer = round(2 * math.pi * r, 2)
            return (
                f"What is the circumference of a circle with radius {r}? (Use pi, round to 2 decimals.)",
                answer,
                f"Circumference = 2 * pi * r = 2 * pi * {r} = {self.format_answer(answer)}.",
            )

        l = rng.randint(2, 12)
        w = rng.randint(2, 12)
        h = rng.randint(2, 12)
        answer = l * w * h
        return (
            f"What is the volume of a box with length {l}, width {w}, and height {h}?",
            answer,
            f"Volume = l * w * h = {l} * {w} * {h} = {answer}.",
        )

    def _math_algebra(self, rng: random.Random) -> tuple[str, Any, str]:
        x_value = rng.randint(1, 20)
        a = rng.randint(2, 12)
        b = rng.randint(-30, 30)
        c = a * x_value + b
        sign = "+" if b >= 0 else "-"
        prompt = f"Solve for x: {a}x {sign} {abs(b)} = {c}"
        explanation = f"Move constants and divide: x = ({c} - ({b})) / {a} = {x_value}."
        return prompt, x_value, explanation

    def _math_trigonometry(self, rng: random.Random) -> tuple[str, Any, str]:
        table = [
            ("sin", 0, 0),
            ("cos", 0, 1),
            ("tan", 0, 0),
            ("sin", 30, 0.5),
            ("tan", 45, 1),
            ("cos", 60, 0.5),
            ("sin", 90, 1),
            ("cos", 180, -1),
        ]
        fn, deg, answer = rng.choice(table)
        prompt = f"What is {fn}({deg} degrees)?"
        explanation = f"{fn}({deg} deg) = {self.format_answer(answer)}."
        return prompt, answer, explanation

    def _generate_chemistry(
        self, _age: int, rng: random.Random
    ) -> tuple[str, Any, str, str | None]:
        element, atomic_number = rng.choice(list(ELEMENT_ATOMIC_NUMBERS.items()))
        kind = rng.choice(["atomic", "protons", "electrons", "element"])
        if kind == "atomic":
            return (
                f"What is the atomic number of {element}?",
                atomic_number,
                f"The atomic number of {element} is {atomic_number}.",
                None,
            )
        if kind == "protons":
            return (
                f"How many protons does a neutral {element} atom have?",
                atomic_number,
                f"A neutral {element} atom has {atomic_number} protons.",
                None,
            )
        if kind == "electrons":
            return (
                f"How many electrons does a neutral {element} atom have?",
                atomic_number,
                f"In a neutral atom, electrons equal protons: {atomic_number}.",
                None,
            )
        return (
            f"Which element has atomic number {atomic_number}?",
            element,
            f"Atomic number {atomic_number} belongs to {element}.",
            None,
        )

    def _generate_biology(
        self, _age: int, rng: random.Random
    ) -> tuple[str, Any, str, str | None]:
        prompt, answer, explanation = rng.choice(BIOLOGY_FACTS)
        return prompt, answer, explanation, None

    def _generate_physics(
        self, _age: int, rng: random.Random
    ) -> tuple[str, Any, str, str | None]:
        kind = rng.choice(["speed", "force", "potential_energy", "density", "kinetic_energy"])
        if kind == "speed":
            distance = rng.randint(20, 240)
            time_s = rng.randint(2, 12)
            answer = round(distance / time_s, 2)
            return (
                f"Speed = distance / time. If distance is {distance} m and time is {time_s} s, what is speed (m/s)?",
                answer,
                f"Speed = {distance} / {time_s} = {self.format_answer(answer)} m/s.",
                None,
            )
        if kind == "force":
            mass = rng.randint(2, 25)
            acceleration = rng.randint(2, 12)
            answer = mass * acceleration
            return (
                f"Force = mass * acceleration. If mass is {mass} kg and acceleration is {acceleration} m/s^2, what is force (N)?",
                answer,
                f"Force = {mass} * {acceleration} = {answer} N.",
                None,
            )
        if kind == "potential_energy":
            mass = rng.randint(1, 20)
            height = rng.randint(2, 30)
            g = 10
            answer = mass * g * height
            return (
                f"Potential energy = m * g * h. For m={mass} kg, g={g} m/s^2, h={height} m, what is PE (J)?",
                answer,
                f"PE = {mass} * {g} * {height} = {answer} J.",
                None,
            )
        if kind == "kinetic_energy":
            mass = rng.choice([2, 4, 6, 8, 10, 12, 14, 16])
            velocity = rng.randint(2, 20)
            answer = 0.5 * mass * velocity * velocity
            return (
                f"Kinetic energy = 0.5 * m * v^2. For m={mass} kg and v={velocity} m/s, what is KE (J)?",
                answer,
                f"KE = 0.5 * {mass} * {velocity}^2 = {self.format_answer(answer)} J.",
                None,
            )
        mass = rng.randint(20, 200)
        volume = rng.randint(2, 25)
        answer = round(mass / volume, 2)
        return (
            f"Density = mass / volume. If mass is {mass} kg and volume is {volume} m^3, what is density (kg/m^3)?",
            answer,
            f"Density = {mass} / {volume} = {self.format_answer(answer)} kg/m^3.",
            None,
        )

    def _generate_astronomy(
        self, _age: int, rng: random.Random
    ) -> tuple[str, Any, str, str | None]:
        kind = rng.choice(["fact", "planet_position", "position_planet"])
        if kind == "fact":
            prompt, answer, explanation = rng.choice(ASTRONOMY_FACTS)
            return prompt, answer, explanation, None

        if kind == "planet_position":
            idx = rng.randint(0, len(PLANETS_FROM_SUN) - 1)
            planet = PLANETS_FROM_SUN[idx]
            return (
                f"What number planet from the Sun is {planet}?",
                idx + 1,
                f"{planet} is planet number {idx + 1} from the Sun.",
                None,
            )

        idx = rng.randint(0, len(PLANETS_FROM_SUN) - 1)
        answer = PLANETS_FROM_SUN[idx]
        return (
            f"Which planet is number {idx + 1} from the Sun?",
            answer,
            f"Planet number {idx + 1} from the Sun is {answer}.",
            None,
        )

    def _generate_geography(
        self, _age: int, rng: random.Random
    ) -> tuple[str, Any, str, str | None]:
        kind = rng.choice(["capital", "country", "continent"])
        country, capital = rng.choice(list(COUNTRY_CAPITALS.items()))
        if kind == "capital":
            return (
                f"What is the capital city of {country}?",
                capital,
                f"The capital city of {country} is {capital}.",
                None,
            )
        if kind == "country":
            return (
                f"{capital} is the capital city of which country?",
                country,
                f"{capital} is the capital of {country}.",
                None,
            )
        country, continent = rng.choice(list(COUNTRY_CONTINENT.items()))
        return (
            f"Which continent is {country} in?",
            continent,
            f"{country} is in {continent}.",
            None,
        )

    def _generate_history(
        self, _age: int, rng: random.Random
    ) -> tuple[str, Any, str, str | None]:
        event, year = rng.choice(HISTORY_EVENTS)
        kind = rng.choice(["year", "event"])
        if kind == "year":
            return (
                f"In which year did {event} happen?",
                year,
                f"{event} happened in {year}.",
                None,
            )
        return (
            f"What major event happened in {year}?",
            event,
            f"A known event in {year} was {event}.",
            None,
        )
