import csv
import heapq
from collections import deque

class TicketCostCalculator:
    def __init__(self, data_file):
        self.metro_data, self.transfer_stations = self.load_metro_data(data_file)

    def load_metro_data(self, file_path):
        metro_data = {}
        transfer_stations = set()  # Store transfer stations

        with open(file_path, mode='r', newline='', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Skip the header row

            for row in csv_reader:
                start_station_line = row[0]
                start_station = row[1]
                end_station_line = row[2]
                end_station = row[3]
                cost = int(row[4])  # Convert cost to integer

                if start_station == end_station:
                    continue

                # Create entries in the metro network dictionary for both directions
                if start_station not in metro_data:
                    metro_data[start_station] = {"line": start_station_line}
                if end_station not in metro_data:
                    metro_data[end_station] = {"line": end_station_line}

                # Add the distance for both directions
                metro_data[start_station][end_station] = cost
                metro_data[end_station][start_station] = cost

                # Check if this station is a transfer station (intersection of lines)
                if start_station_line != end_station_line:
                    transfer_stations.add(start_station)
                    transfer_stations.add(end_station)

        return metro_data, transfer_stations
    
    def get_station_line(self, station):
        # Get the line information for a station
        if station in self.metro_data:
            return self.metro_data[station].get("line", "")
        else:
            return ""
        
    def calculate_ticket_cost(self, start_station, end_station):
        if start_station not in self.metro_data or end_station not in self.metro_data:
            return "Invalid stations"

        if start_station == end_station:
            return "Start and end stations are the same"

        # Check if stations are on different lines
        start_station_line = self.get_station_line(start_station)
        end_station_line = self.get_station_line(end_station)

        total_cost = 0

        if start_station_line != end_station_line:
            # Stations are on different lines, find the transfer station
            for transfer_station in self.transfer_stations:
                if transfer_station in self.metro_data[start_station] and transfer_station in self.metro_data[end_station]:
                    # Calculate the cost from start to transfer station
                    start_to_transfer_cost = self.calculate_cost_between_stations(start_station, transfer_station)
                    if start_to_transfer_cost is None:
                        return "No route available"

                    # Calculate the cost from transfer station to end
                    transfer_to_end_cost = self.calculate_cost_between_stations(transfer_station, end_station)
                    if transfer_to_end_cost is None:
                        return "No route available"

                    # Calculate the total cost as the sum of the two segments
                    total_cost = start_to_transfer_cost + transfer_to_end_cost
                    break

        else:
            # Calculate the cost of the remaining part of the journey on the same line
            shortest_path_on_same_line = self.find_shortest_path(start_station, end_station)

            if shortest_path_on_same_line:
                total_cost = self.calculate_total_cost(shortest_path_on_same_line)
            else:
                return "No route available"  # No valid path on the same line

        return total_cost

    def calculate_cost_between_stations(self, start_station, end_station):
        # Calculate the cost between two stations if a valid path exists
        shortest_path = self.find_shortest_path(start_station, end_station)
        if shortest_path:
            return self.calculate_total_cost(shortest_path)
        else:
            return None


    def find_shortest_path(self, start_station, end_station):
        if start_station not in self.metro_data or end_station not in self.metro_data:
            return None  # Invalid stations

        if start_station == end_station:
            return [start_station]  # Start and end stations are the same

        # Initialize the distances dictionary to store the shortest distances from the start station
        distances = {station: float('inf') for station in self.metro_data}
        distances[start_station] = 0

        # Initialize the priority queue (min heap) with the start station and its distance
        priority_queue = [(0, start_station)]

        # Initialize a dictionary to track the previous station in the shortest path
        previous_station = {}

        while priority_queue:
            current_distance, current_station = heapq.heappop(priority_queue)

            # If we reach the end station, reconstruct and return the shortest path
            if current_station == end_station:
                return self.reconstruct_path(previous_station, end_station)

            # If the current distance is greater than the recorded distance, skip it
            if current_distance > distances[current_station]:
                continue

            # Explore neighboring stations
            for neighbor_station, cost in self.metro_data[current_station].items():
                try:
                    cost = int(cost)  # Try to convert cost to integer
                except ValueError:
                    continue  # Skip entries with non-integer costs

                distance_to_neighbor = distances[current_station] + cost

                if distance_to_neighbor < distances[neighbor_station]:
                    distances[neighbor_station] = distance_to_neighbor
                    previous_station[neighbor_station] = current_station
                    heapq.heappush(priority_queue, (distance_to_neighbor, neighbor_station))

        # If we couldn't find a valid path, return None
        return None

    def reconstruct_path(self, previous_station, end_station):
        path = [end_station]
        while end_station in previous_station:
            end_station = previous_station[end_station]
            path.append(end_station)
        return path[::-1]
    
    def calculate_total_cost(self, path):
        total_cost = 0

        for i in range(len(path) - 1):
            start_station = path[i]
            end_station = path[i + 1]

            # Check if stations are in metro_data dictionary
            if start_station not in self.metro_data or end_station not in self.metro_data:
                return "Invalid stations"

            # Check if the connection exists in metro_data
            if end_station not in self.metro_data[start_station]:
                return f"No direct route available between {start_station} and {end_station}"

            # Add the cost to the total
            cost = self.metro_data[start_station][end_station]
            total_cost += cost

        return total_cost  # Return the total cost as a numeric value, not a string
    
    
    
# data_file = "output3.csv"

# # Create an instance of TicketCostCalculator
# ticket_calculator = TicketCostCalculator(data_file)

# # Access the metro_data dictionary
# metro_data_dict = ticket_calculator.metro_data

# # Print the metro_data dictionary
# print("Metro Data Dictionary:")
# print(metro_data_dict)

# calculator = TicketCostCalculator('output3.csv')
# shortest_path = calculator.find_shortest_path('Asok', 'สนามไชย')
# if shortest_path:
#     print(f"Shortest path: {shortest_path}")
#     cost_result = calculator.calculate_total_cost(shortest_path)
#     print(cost_result)
# else:
#     print("No valid route found.")
