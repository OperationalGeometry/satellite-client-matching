from typing import Dict, Tuple
from util import Color, Sat, User, Vector3

def service_available(user_pos: Vector3, sat_pos: Vector3) -> bool:
    """Determine if a satellite can provide service to a user based on the angle."""
    origin = Vector3(0, 0, 0)  # Define the origin point for angle calculations
    angle = origin.angle_between(user_pos, sat_pos - user_pos)  # Calculate the angle between the user's position and the satellite
    return angle <= 45  # Check if the angle is within 45 degrees (i.e., the service is available)

def assign_color(user_id, users, sat_id, sats, connection_map) -> Color:
    """Assign a user to a satellite using a non-conflicting color to avoid interference."""
    user_pos = users[user_id]  # Get the user's position
    sat_pos = sats[sat_id]  # Get the satellite's position
    
    # Iterate over each color and the list of users already assigned to that color for the satellite
    for color, user_list in connection_map[sat_id].items():
        if len(user_list) == 0:  # If the color has no users assigned yet, assign the current user to this color
            connection_map[sat_id][color].append(user_id)  # Add user to the color's list for the satellite
            return color  # Return the assigned color

        # Check if the angle between the current user and all other users already assigned to this color is large enough to avoid interference
        if all(sat_pos.angle_between(user_pos, users[other_user_id]) >= 10 for other_user_id in user_list):
            connection_map[sat_id][color].append(user_id)  # Add user to this color if no interference
            return color  # Return the assigned color

    return -1  # Return -1 if no color could be assigned without interference

def solve(users: Dict[User, Vector3], sats: Dict[Sat, Vector3]) -> Dict[User, Tuple[Sat, Color]]:
    """Assign users to satellites, respecting capacity and interference constraints."""
    
    solution = {}  # Dictionary to store the final assignment of users to satellites and their respective color
    colors = [Color.A, Color.B, Color.C, Color.D]  # Define the available color options for each satellite
    available = {sat: 32 for sat in sats.keys()}  # Track the available capacity (32) for each satellite
    
    # Create a connection map to store the list of users assigned to each color for each satellite
    connection = {
        sat: {color: [] for color in colors} for sat in sats
    }

    # List to store each user and the satellites available for them
    user_satellite_options = []

    for user, user_pos in users.items():
        # For each user, find the satellites that can provide service and still have capacity
        available_sats = [
            (sat, sat_pos) for sat, sat_pos in sats.items()
            if service_available(user_pos, sat_pos) and available[sat] > 0
        ]
        # Add the user and their available satellite options to the list
        user_satellite_options.append((user, available_sats))

    # Sort users by the number of available satellites (fewer options come first to prioritize)
    user_satellite_options.sort(key=lambda x: len(x[1]))

    # Iterate over the sorted users and try to assign them to a satellite
    for user, available_sats in user_satellite_options:
        assigned = False  # Flag to indicate if the user has been assigned
        for sat, sat_pos in available_sats:
            if available[sat] > 0:  # Ensure the satellite still has capacity
                color = assign_color(user, users, sat, sats, connection)  # Try to assign the user with a non-conflicting color
                if color != -1:  # If a color was successfully assigned
                    solution[user] = (sat, color)  # Record the assignment in the solution
                    available[sat] -= 1  # Decrement the satellite's available capacity
                    assigned = True  # Mark the user as assigned
                    break  # Stop trying once the user is assigned
        
        if not assigned:
            pass  # If the user couldn't be assigned, we simply skip them (can be modified for error handling)

    return solution  # Return the final solution with all assigned users
