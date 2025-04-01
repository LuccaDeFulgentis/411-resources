from dataclasses import dataclass
import logging
import sqlite3
from typing import Any, List

from boxing.utils.sql_utils import get_db_connection
from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Boxer:
    id: int
    name: str
    weight: int
    height: int
    reach: float
    age: int
    weight_class: str = None

    def __post_init__(self):
        self.weight_class = get_weight_class(self.weight)  # Automatically assign weight class


def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:
    """Creates a new boxer in the database with the given information.
    
    Args:
        name (str): The name of the boxer. Must have a unique name.
        weight (int): The weight of the boxer. Must be greater than 125 pounds.
        height (int): The height of the boxer in inches. Must be greater than 0 inches.
        reach (float): The reach of the boxer in inches. Must be greater than 0 inches.
        age (int): The age of the boxer. Must be between 18 years old and 40 years old inclusive.
        
    Raises:
        ValueError: The weight is not at least 125 pounds.
        ValueError: The height is not greater than 0 inches.
        ValueError: The reach is not greather than 0 inches.
        ValueError: The age is not in between 18 years old and 40 years old inclusive.
        ValueError: There is a boxer already with the same name and it already exists.
        IntegrityError: Multiple of the same named boxers are inserted.
        Error: If any connection failure to database occurs.
        
    Returns:
        Nothing.
        
    """
    if weight < 125:
        raise ValueError(f"Invalid weight: {weight}. Must be at least 125.")
    if height <= 0:
        raise ValueError(f"Invalid height: {height}. Must be greater than 0.")
    if reach <= 0:
        raise ValueError(f"Invalid reach: {reach}. Must be greater than 0.")
    if not (18 <= age <= 40):
        raise ValueError(f"Invalid age: {age}. Must be between 18 and 40.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the boxer already exists (name must be unique)
            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                raise ValueError(f"Boxer with name '{name}' already exists")

            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))

            conn.commit()

    except sqlite3.IntegrityError:
        raise ValueError(f"Boxer with name '{name}' already exists")

    except sqlite3.Error as e:
        raise e


def delete_boxer(boxer_id: int) -> None:
    """Deletes a boxer from the database based on the given boxer ID.
    
    Args:
        boxer_id (int): A ID associated with a boxer's information in the database.
        
    Raises:
        ValueError: Boxer ID was not found in the fetch.
        Error: If any connection failure to database occurs.
        
    Returns:
        Nothing.
        
    """
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()

    except sqlite3.Error as e:
        raise e


def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """Retreieves a list of boxers from the data base sorted by win percentage or wins if the boxer has at least one match.
    
    Args:
        sort_by (str): Default set to "wins", selects whether the leaderboard is sorted by wins or win percentage based on if equal to "wins" or "win_pct".
        
    Raises:
        ValueError: If sort_by is not set to either "win_pct" or "wins".
        Error: If any connection failure to database occurs.
        
    Returns: 
        leaderboard (list): A list of dictionaries of boxers sorted by win percentage or total wins.
          
    """
    
    query = """
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
    """

    if sort_by == "win_pct":
        query += " ORDER BY win_pct DESC"
    elif sort_by == "wins":
        query += " ORDER BY wins DESC"
    else:
        raise ValueError(f"Invalid sort_by parameter: {sort_by}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        leaderboard = []
        for row in rows:
            boxer = {
                'id': row[0],
                'name': row[1],
                'weight': row[2],
                'height': row[3],
                'reach': row[4],
                'age': row[5],
                'weight_class': get_weight_class(row[2]),  # Calculate weight class
                'fights': row[6],
                'wins': row[7],
                'win_pct': round(row[8] * 100, 1)  # Convert to percentage
            }
            leaderboard.append(boxer)

        return leaderboard

    except sqlite3.Error as e:
        raise e


def get_boxer_by_id(boxer_id: int) -> Boxer:
    """Searches the database for a boxers information given Boxers ID and returns a Boxer object.
    
    Args:
        boxer_id (int): A ID associated with a boxer's information in the database.
        
    Raises:
        ValueError: boxer ID was not found in the fetch.
        Error: If any connection failure to database occurs.
        
    Returns:
        Boxer (object): A Boxer object with the given boxer_id.
        
    """

    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE id = ?
            """, (boxer_id,))

            row = cursor.fetchone()

            if row:
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                return boxer
            else:
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        raise e


def get_boxer_by_name(boxer_name: str) -> Boxer:
    """Searches the database for a str that matches boxer_name and returns a Boxer object.
        
    Args:
        boxer_name (str): The unique name of a boxer.
        
    Raises:
        ValueError: Boxer name was not found in the fetch.
        Error: If any connection failure to database occurs.
        
    Returns:
        Boxer (object): A Boxer object with the given boxer_name.
        
    """
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE name = ?
            """, (boxer_name,))

            row = cursor.fetchone()

            if row:
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                return boxer
            else:
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        raise e


def get_weight_class(weight: int) -> str:
    """Determines the weightclass of given integer.

    Args:
        weight (int): The int the function is comparing. Must be greater than 125 pounds. Represents weigth of boxer.
        
    Raises:
        ValueError: weight was not at least 125.
        
    Returns:
        weight_class (str): returns 'HEAVYWEIGHT','MIDDLEWEIGHT','LIGHTWEIGHT','FEATHERWEIGHT' based on the range varible weight is in.
        
    """
    
    if weight >= 203:
        weight_class = 'HEAVYWEIGHT'
    elif weight >= 166:
        weight_class = 'MIDDLEWEIGHT'
    elif weight >= 133:
        weight_class = 'LIGHTWEIGHT'
    elif weight >= 125:
        weight_class = 'FEATHERWEIGHT'
    else:
        raise ValueError(f"Invalid weight: {weight}. Weight must be at least 125.")

    return weight_class


def update_boxer_stats(boxer_id: int, result: str) -> None:
    """Updates the number of fights a boxer with the given boxer_id has completed and updates the number of wins based on result in the database.
        
    Args:
        boxer_id (int): A ID associated with a boxer's information in the database.
        result (str): The result of a boxers match. Must be 'win' or 'loss.
        
    Raises:
        ValueError: result(str) is not equal to 'win' or 'loss'.
        ValueError: Boxer with the given ID was not found.
        Error: If any connection failure to database occurs.
        
    Returns:
        Nothing.
        
    """
    
    if result not in {'win', 'loss'}:
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
            else:  # result == 'loss'
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            conn.commit()

    except sqlite3.Error as e:
        raise e
