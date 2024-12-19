import math

K_FACTOR = 60
# {elo_one, elo_two, player_one_win, epic_win}
def expected_score(e1, e2):
    return 1 / (1 + math.pow(10, (e2 - e1) / 400))
def main():
    elo1 = float(input("Enter player one elo:").strip())
    elo2 = float(input("Enter player two elo:").strip())
    player_one_win = input("Did player one win? (y/n)").strip().lower() == "y"
    epic_win = input("Was it epic win? (y/n)").strip().lower() == "y"

    if player_one_win:
        actual1, actual2 = 1, 0
    else:
        actual2, actual1 = 1, 0
    expected1 = expected_score(elo1, elo2)
    expected2 = expected_score(elo2, elo1)
    # Update ratings
    if epic_win:
        rating1_after = elo1 + (K_FACTOR * 1.33) * (actual1 - expected1)
        rating2_after = elo2 + (K_FACTOR * 1.33) * (actual2 - expected2)
    else:
        rating1_after = elo1 + K_FACTOR * (actual1 - expected1)
        rating2_after = elo2 + K_FACTOR * (actual2 - expected2)
    
    print(f"player one win = {player_one_win}\nepic win = {epic_win}")
    print(f"player one change: {elo1} => {rating1_after :5.2f}")
    print(f"player two change: {elo2} => {rating2_after :5.2f}")

if __name__ == "__main__":
    main()