from __future__ import annotations

from app import content


def recommendation_by_answers(goal: str, lifestyle: str, preferred_format: str) -> tuple[str, list[str]]:
    slugs: list[str]
    reason: str

    if goal == "sport":
        slugs = ["activize", "fitness_drink", "restorate"]
        reason = "Для активного ритма логично начать с энергии днём и восстановления пищевой рутины вечером."
    elif goal == "weight":
        slugs = ["topshape", "powercocktail", "restorate"]
        reason = "Для контроля веса важна структура питания, базовая поддержка и регулярность."
    elif goal == "beauty":
        slugs = ["beauty", "skin", "powercocktail"]
        reason = "Для beauty-цели лучше сочетать уход, питание и ежедневную базу."
    else:
        slugs = ["powercocktail", "restorate", "optimal_set"]
        reason = "Для мягкого wellness-старта удобнее всего базовый ежедневный набор."

    if lifestyle == "office" and "activize" not in slugs:
        slugs.insert(1, "activize")
    if lifestyle == "evening" and "restorate" not in slugs:
        slugs.append("restorate")
    if preferred_format == "set" and "optimal_set" not in slugs:
        slugs.insert(0, "optimal_set")
    if preferred_format == "consult":
        reason += " Так как вы выбрали консультацию, лучше уточнить состав, ограничения и бюджет у консультанта."

    unique_slugs = list(dict.fromkeys(slugs))[:4]
    names = [content.PRODUCTS[slug]["name"] for slug in unique_slugs]
    text = f"""
🎯 <b>Рекомендация</b>

{reason}

Посмотрите:
{chr(10).join(f'• {name}' for name in names)}

Это стартовая гипотеза, а не медицинское назначение. Перед заказом проверьте состав и ограничения.
""".strip()
    return text, unique_slugs

