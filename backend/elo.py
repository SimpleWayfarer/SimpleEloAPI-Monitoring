def expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

def update_elo(r_a, r_b, score_a, k=32):
    exp_a = expected_score(r_a, r_b)
    new_a = r_a + k * (score_a - exp_a)
    new_b = r_b + k * ((1 - score_a) - (1 - exp_a))
    return round(new_a), round(new_b)
