from flask import Blueprint, jsonify

rune_bp = Blueprint('rune', __name__, url_prefix='/api/rune')

@rune_bp.route('/preview', methods=['GET'])
def get_rune_preview():
    return jsonify({
        "version": "v1.0.0-preview",
        "philosophy": "Rune reads like instructions to a person, not commands to a machine.",
        "examples": [
            {
                "title": "Greeting Program",
                "code": "say \"Welcome to Rune!\"\n\nask \"What is your name?\" into name\nsay \"Hello \" + name + \"!\"",
                "output": "Welcome to Rune!\nWhat is your name?\nJovan\nHello Jovan!"
            },
            {
                "title": "Grade Checker",
                "code": "ask \"Enter your score: \" into score\n\nif score is greater than 90\n    say \"You got an A!\"\notherwise\n    say \"Keep trying!\"\nend",
                "output": "Enter score: 95\nYou got an A!"
            },
            {
                "title": "Shopping List",
                "code": "shopping is []\n\nrepeat 3 times\n    ask \"Item: \" into item\n    add item to shopping\nend\n\nfor each item in shopping\n    say \"  - \" + item\nend",
                "output": "Item: Rice\nItem: Beans\nItem: Oil\n\n  - Rice\n  - Beans\n  - Oil"
            }
        ]
    })
