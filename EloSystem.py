import csv
import json
import math
import os
from collections import defaultdict
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

    def expected_score(rating_a, rating_b):
        """Calculate the expected score for a player."""
        return 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))
    
    def str_elo_change(elo_one, elo_two, score1, score2) -> str:
        ret = ""
        K_FACTOR = 60

        if score1 > score2:
            actual1, actual2 = 1, 0
        else:
            actual2, actual1 = 1, 0

        expected1 = EloSystem.expected_score(elo_one, elo_two)
        expected2 = EloSystem.expected_score(elo_two, elo_one)
        # Update ratings
        if score1 == 0 or score2 == 0:
            rating1_after = elo_one + (K_FACTOR * 1.33) * (actual1 - expected1)
            rating2_after = elo_two + (K_FACTOR * 1.33) * (actual2 - expected2)
        else:
            rating1_after = elo_one + K_FACTOR * (actual1 - expected1)
            rating2_after = elo_two + K_FACTOR * (actual2 - expected2)
        
        ret += f"player one change: {elo_one} => {rating1_after :5.2f}\n"
        ret += f"player two change: {elo_two} => {rating2_after :5.2f}"
        return ret

    def update_ratings(self, player1, player2, score1, score2) -> str:
        """Update the Elo ratings based on match scores."""
        self.add_player(player1)
        self.add_player(player2)

        # Record ELO before the match
        rating1_before = self.players[player1]
        rating2_before = self.players[player2]

        expected1 = EloSystem.expected_score(rating1_before, rating2_before)
        expected2 = EloSystem.expected_score(rating2_before, rating1_before)

        is_epic = score1 == 0 or score2 == 0
        # Determine actual results
        if score1 > score2:
            actual1, actual2 = 1, 0
        elif score2 > score1:
            actual2, actual1 = 1, 0
        else:
            actual1, actual2 = 0.5, 0.5

        # Update ratings
        if is_epic:
            rating1_after = rating1_before + (self.k_factor * 1.33) * (actual1 - expected1)
            rating2_after = rating2_before + (self.k_factor * 1.33) * (actual2 - expected2)
        else:
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
        return f"{player1}: {rating1_before} => {rating1_after}\n{player2}: {rating2_before} => {rating2_after}"

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

    def calculate_stats_from_history(self):
        """Calculate wins, losses, draws, and total games for each player from match history."""
        stats = defaultdict(lambda: {"games": 0, "wins": 0, "losses": 0, "draws": 0})

        if os.path.exists(self.history_csv):
            with open(self.history_csv, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    player1, player2 = row["Player 1"], row["Player 2"]
                    score1, score2 = float(row["Player 1 Score"]), float(row["Player 2 Score"])

                    # Update total games
                    stats[player1]["games"] += 1
                    stats[player2]["games"] += 1

                    # Update wins, losses, draws
                    if score1 > score2:
                        stats[player1]["wins"] += 1
                        stats[player2]["losses"] += 1
                    elif score2 > score1:
                        stats[player2]["wins"] += 1
                        stats[player1]["losses"] += 1
                    else:
                        stats[player1]["draws"] += 1
                        stats[player2]["draws"] += 1
        return stats

    def display_ratings(self):
        """Display all player ratings and stats."""
        stats = self.calculate_stats_from_history()
        # print("\nCurrent Elo Ratings and Stats:")
        header = f"{'Rank':<5} {'Player':<20} {'Rating':<10} {'Win %':<12}{'Games':<6} {'Wins':<5} {'Losses':<7}"
        print("\nCurrent Elo Ratings and Stats:")
        print(header)
        print("-" * len(header))
        for idx, (player, rating) in enumerate(sorted(self.players.items(), key=lambda x: x[1], reverse=True)):  # Sort alphabetically
            player_stats = stats[player]
            games = player_stats['games']
            wins = player_stats['wins']
            win_rate = (wins / games * 100) if games > 0 else 0.0
            print(
                f"{idx + 1:<5} {player:<20} {round(rating, 2):<10} {win_rate:<11.2f} {player_stats['games']:<6} "
                f"{player_stats['wins']:<5} {player_stats['losses']:<7}"
            )
    def str_rating(self) -> str:
        stats = self.calculate_stats_from_history()
        ret = ""
        # print("\nCurrent Elo Ratings and Stats:")
        header = f"{'Rank':<5} {'Player':<20} {'Rating':<10} {'Win %':<12}{'Games':<6} {'Wins':<5} {'Losses':<7}"
        ret += "Current Elo Ratings and Stats:\n"
        ret += header + "\n"
        ret += "-" * len(header)
        for idx, (player, rating) in enumerate(sorted(self.players.items(), key=lambda x: x[1], reverse=True)):  # Sort alphabetically
            player_stats = stats[player]
            games = player_stats['games']
            wins = player_stats['wins']
            win_rate = (wins / games * 100) if games > 0 else 0.0
            ret += (
                f"{idx + 1:<5} {player:<20} {round(rating, 2):<10} {win_rate:<11.2f} {player_stats['games']:<6} "
                f"{player_stats['wins']:<5} {player_stats['losses']:<7}\n"
            )
        return ret
