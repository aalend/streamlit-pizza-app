PI = 3.14159


def calc_pizza_dough(size_cm, num_pizzas, hydration, thickness):
    std_radius = 30 / 2
    std_area = PI * (std_radius**2)

    wanted_size = size_cm / 2
    target_area = PI * (wanted_size**2)

    size_ratio = target_area / std_area

    thickness_factor = {'thin': 0.8, 'regular': 1.0, 'thick': 1.3}.get(thickness.lower(), 1.0)

    base_flour = 220 * size_ratio * thickness_factor
    total_flour = base_flour * num_pizzas

    # 62% standard hydration
    water = total_flour * (hydration / 100)
    yeast = total_flour * 0.004  # 0.4%
    salt = total_flour * 0.025  # 2.5%
    oil = total_flour * 0.033  # 3.3%

    total_mass = total_flour + water + yeast + salt + oil
    mass_of_dough_ball = total_mass / num_pizzas

    ingredients = {
        'Ingredient': [
            'Wheat flour (12-14% protein)',
            'Cold water (< 15°C)',
            'Dry yeast',
            'Salt',
            'Olive oil',
        ],
        'Amount': [
            f'{round(total_flour)} g',
            f'{round(water)} g',
            f'{round(yeast, 1)} g',
            f'{round(salt, 1)} g',
            f'{round(oil, 1)} g',
        ],
        'Bakers %': [
            '100%',
            f'{int(hydration)}%',
            f'{round((yeast / total_flour) * 100, 1)}%',
            f'{round((salt / total_flour) * 100, 1)}%',
            f'{round((oil / total_flour) * 100, 1)}%',
        ],
    }

    return (
        round(mass_of_dough_ball),
        round(total_flour),
        round(water),
        round(salt, 1),
        round(yeast, 1),
        round(oil, 1),
        int(hydration),
        ingredients,
    )
