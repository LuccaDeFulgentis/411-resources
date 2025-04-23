import logging
import os
import requests

from boxing.utils.logger import configure_logger

from functools import wraps
from flask import request, jsonify

logger = logging.getLogger(__name__)
configure_logger(logger)

RANDOM_ORG_URL = os.getenv(
    "RANDOM_ORG_URL",
    "https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new"
)

def validate_json(schema):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            data = request.get_json()
            if not data:
                return jsonify({'error': 'JSON required'}), 400
            # TODO: Validate data against schema
            return f(*args, **kwargs)
        return wrapper
    return decorator

def error_handler(e):
    return jsonify({'error': str(e)}), 500

def get_random() -> float:
    """
    Fetches a random float between 0 and 1 from random.org.

    Returns:
        float: The random number fetched from random.org.

    Raises:
        ValueError: If the response from random.org is not a valid float.
        RuntimeError: If the request to random.org fails.
    """
    try:
        logger.info(f"Fetching random number from {RANDOM_ORG_URL}")
        response = requests.get(RANDOM_ORG_URL, timeout=5)
        response.raise_for_status()
        random_number_str = response.text.strip()

        try:
            return float(random_number_str)
        except ValueError:
            logger.error(f"Invalid response from random.org: {random_number_str}")
            raise ValueError(f"Invalid response from random.org: {random_number_str}")

    except requests.exceptions.Timeout:
        logger.error("Request to random.org timed out.")
        raise RuntimeError("Request to random.org timed out.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Request to random.org failed: {e}")
        raise RuntimeError(f"Request to random.org failed: {e}")

# Flask-related helpers

def boxer_to_dict(boxer):
    return {
        "id": boxer.id,
        "name": boxer.name,
        "weight": boxer.weight,
        "height": boxer.height,
        "reach": boxer.reach,
        "age": boxer.age,
        "wins": boxer.wins,
        "losses": boxer.losses
    }

def create_boxer_from_json(data):
    from boxing.models.boxer_model import Boxers
    return Boxers(
        name=data["name"],
        weight=data["weight"],
        height=data["height"],
        reach=data["reach"],
        age=data["age"],
        wins=data.get("wins", 0),
        losses=data.get("losses", 0)
    )


