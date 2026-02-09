"""
AnkiConnect API integration.
"""

import requests
from config import ANKI_CONNECT_URL


def anki_request(action, params=None):
    """
    Make a request to AnkiConnect.
    
    Args:
        action: The AnkiConnect action to perform
        params: Optional parameters for the action
        
    Returns:
        JSON response from AnkiConnect
    """
    return requests.post(ANKI_CONNECT_URL, json={
        "action": action,
        "version": 6,
        "params": params or {}
    }).json()


def get_deck_names():
    """
    Get all deck names from Anki.
    
    Returns:
        List of deck names
    """
    resp = anki_request("deckNames")
    return resp.get("result", [])


def get_card_ids(deck_name):
    """
    Get all card IDs in a deck.
    
    Args:
        deck_name: Name of the Anki deck
        
    Returns:
        List of card IDs
    """
    resp = anki_request("findCards", {"query": f"deck:{deck_name}"})
    return resp.get("result", [])


def get_cards_info(card_ids):
    """
    Get card info for a list of card IDs.
    
    Args:
        card_ids: List of card IDs
        
    Returns:
        List of card info dictionaries
    """
    resp = anki_request("cardsInfo", {"cards": card_ids})
    return resp.get("result", [])
