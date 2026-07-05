def get_gender_filter(gender_male: bool, gender_female: bool):
    genders = []
    if gender_male:
        genders.append("M")
    if gender_female:
        genders.append("F")
    return genders if genders else None
