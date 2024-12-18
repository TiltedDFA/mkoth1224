import csv
import json
import math
import os
from datetime import datetime


class EloSystem:
    def __init__(self, k_factor=60, json_file="elo_ratings.json", ratings_csv="elo_ratings.csv", history_csv="match_history.csv"):
        self.players = {}  # Dictionary to store player ratings
        self.k_factor = k_factor  # K-factor for Elo adjustments
        self.json_file = json_file  # File to save/load JSON data
        self.ratings_csv = ratings_csv  # File to save/load player ratings in CSV
        self.history_csv = history_csv  # File to save match history in CSV

        # Load player data if files exist
        self.load_data()

        # Ensure the match history file exists
        self.initialize_history_file()

    def add_player(self, name):
        """Add a player with a default Elo rating if not already in the system."""
        if name not in self.players:
            self.players[name] = 1000

    def expected_score(self, rating_a, rating_b):
        """Calculate the expected score for a player."""
        return 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))

    def update_ratings(self, player1, player2, score1, score2):
        """Update the Elo ratings based on match scores."""
        self.add_player(player1)
        self.add_player(player2)

        # Record ELO before the match
        rating1_before = self.players[player1]
        rating2_before = self.players[player2]

        expected1 = self.expected_score(rating1_before, rating2_before)
        expected2 = self.expected_score(rating2_before, rating1_before)

        # Determine actual results
        if score1 > score2:
            actual1, actual2 = 1, 0
        elif score2 > score1:
            actual1, actual2 = 0, 1
        else:
            actual1, actual2 = 0.5, 0.5

        # Update ratings
        rating1_after = rating1_before + self.k_factor * (actual1 - expected1)
        rating2_after = rating2_before + self.k_factor * (actual2 - expected2)

        # Save updated ratings
        self.players[player1] = rating1_after
        self.players[player2] = rating2_after

        print(f"\nUpdated Ratings:")
        print(f"{player1}: {round(rating1_after, 2)}")
        print(f"{player2}: {round(rating2_after, 2)}")

        # Save match history
        self.save_match_history(player1, player2, score1, score2, rating1_before, rating1_after, rating2_before, rating2_after)

    def save_match_history(self, player1, player2, score1, score2, rating1_before, rating1_after, rating2_before, rating2_after):
        """Save a single match record to the history CSV file."""
        date = datetime.now().strftime("%Y-%m-%d")
        with open(self.history_csv, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                player1, player2, score1, score2,
                round(rating1_before, 2), round(rating1_after, 2),
                round(rating2_before, 2), round(rating2_after, 2),
                date
            ])
        print(f"Match recorded: {player1} ({score1}) vs {player2} ({score2}) on {date}")

    def initialize_history_file(self):
        """Ensure the match history file has headers if it doesn't already exist."""
        if not os.path.exists(self.history_csv):
            with open(self.history_csv, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([
                    "Player 1", "Player 2", "Player 1 Score", "Player 2 Score",
                    "Player 1 Elo Before", "Player 1 Elo After",
                    "Player 2 Elo Before", "Player 2 Elo After", "Date"
                ])

    def save_data(self):
        """Save player data to both JSON and CSV files."""
        # Save to JSON
        with open(self.json_file, "w") as json_file:
            json.dump(self.players, json_file, indent=4)
        print(f"\nPlayer data saved to {self.json_file}.")

        # Save to CSV
        with open(self.ratings_csv, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Player", "Rating"])
            for player, rating in self.players.items():
                writer.writerow([player, round(rating, 2)])
        print(f"Player data saved to {self.ratings_csv}.")

    def load_data(self):
        """Load player data from JSON or CSV if available."""
        if os.path.exists(self.json_file):
            with open(self.json_file, "r") as json_file:
                self.players = json.load(json_file)
            print(f"Loaded player data from {self.json_file}.")
        elif os.path.exists(self.ratings_csv):
            with open(self.ratings_csv, "r") as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    self.players[row["Player"]] = float(row["Rating"])
            print(f"Loaded player data from {self.ratings_csv}.")
        else:
            print("No existing player data found. Starting fresh.")

    def display_ratings(self):
        """Display all player ratings."""
        print("\nCurrent Elo Ratings:")
        self.players = dict(sorted(self.players.items(), key=lambda kv: kv[1], reverse=True))
        for idx, (player, rating) in enumerate(self.players.items()):
            print(f"{idx+1}. {player}: {round(rating, 2)}")

def main():
    system = EloSystem()
    system.display_ratings()
    print("Welcome to the Elo Rating System!")
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

        # Display updated ratings
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
