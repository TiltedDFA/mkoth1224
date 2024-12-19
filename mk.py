from EloSystem import *


def main():
    system = EloSystem()
    system.display_ratings()
    print("\nWelcome to the Elo Rating System!")
    while True:
        # Input player names and scores
        player1 = input("\nEnter the name of Player 1: ").strip().lower()
        player2 = input("Enter the name of Player 2: ").strip().lower()

        try:
            score1 = float(input(f"Enter {player1}'s score: "))
            score2 = float(input(f"Enter {player2}'s score: "))
        except ValueError:
            print("Invalid input. Please enter numeric scores.")
            continue

        # Update ratings and record match history
        system.update_ratings(player1, player2, score1, score2)

        # Display updated ratings and stats
        system.display_ratings()

        # Save player data
        system.save_data()

        # Option to continue or quit
        cont = input("\nDo you want to enter another match? (yes/no)(y/n): ").strip().lower()
        if cont != 'yes' and cont != 'y':
            print("Exiting Elo System. Goodbye!")
            break

if __name__ == "__main__":
    main()
