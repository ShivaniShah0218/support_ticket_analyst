"""
    This file contains code for API routes
"""

import os
import datetime
from typing import List, Optional
from flask import Flask, request, jsonify, abort
from models import create_ticket, get_tickets, get_last_analysis
from agent_flow import tickets_analyze




app = Flask(__name__)



# Routes
@app.route("/api/tickets", methods=["POST"])
def create_tickets():
    """
        Purpose: API for inserting tickets into database
    """
    payload = request.get_json(force=True, silent=True)
    if not isinstance(payload, list):
        abort(400, description="Request body must be an array of { title, description } objects.")
    tickets_created = []
    for item in payload:
        if not isinstance(item, dict) or "title" not in item:
            abort(400, description="Each item must be an object containing at least a 'title' field.")
        tickets_created.append(create_ticket(item["title"], item.get("description")))

    return jsonify(tickets_created), 201


@app.route("/api/analyze", methods=["POST"])
def analyze_tickets():
    """
        Purpose: API for carrying out analysis
    """
    body = request.get_json(silent=True) or {}
    ticket_ids = body.get("ticketIds") if isinstance(body, dict) else None
    if ticket_ids is not None and not isinstance(ticket_ids, list):
        abort(400, description="ticketIds must be an array of integers if provided.")

    tickets = get_tickets(ticket_ids)
    output=tickets_analyze.run()
    print(output)

    return jsonify({"output":output}), 201


@app.route("/api/analysis/latest", methods=["GET"])
def get_latest_analysis():
    """
        Purpose: API for fetching details of last analysis
    """
    latest_run = get_last_analysis()
    if not latest_run:
        return jsonify({"analysis_run": None, "ticket_analysis": []}), 200

    # Eagerly loaded relationships allow direct access.
    results = []
    for ta in latest_run[1]:
        results.append({"ticket_analysis": ta.to_dict()})

    return jsonify({"analysis_run": latest_run[0], "ticket_analysis": results}), 200


# Only run the app when executed directly (helpful for local testing)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)