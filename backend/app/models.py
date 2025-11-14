"""
    Purpose: This file contains code for getting and inserting data from the database
"""

import psycopg2
from psycopg2 import sql

def get_db_connection():
    """ 
     Purpose: Create database connection
    """
    return psycopg2.connect(
        host="db",  # Use the service name defined in Docker Compose
        database="ticket_analyze_db",
        user="postgres",
        password="root"
    )

def create_ticket(title, description):
    """ 
        Purpose: Insert ticket into the database
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO tickets (title, description) VALUES (%s, %s) RETURNING id", (title, description))
    ticket_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return ticket_id

def analyze_tickets(summary):
    """
        Purpose: Insert analyze runs detail into the database
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO analysis_runs (summary) VALUES (%s, %s) RETURNING id", (summary))
    analysis_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return analysis_id

def create_ticket_analysis(analysis_run_id,ticket_id,category,priority,notes):
    """
        Purpose: Insert  individual tickets detail into the database
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO ticket_analysis (analysis_run_id,ticket_id,category,priority,notes) VALUES (%s, %s,%s,%s,%s) RETURNING id", (analysis_run_id,ticket_id,category,priority,notes))
    conn.commit()
    cur.close()
    conn.close()
    return None



def get_tickets(ticket_ids=None):
    """
        Purpose: Get the tickets for the given ticket ids
    """
    conn = get_db_connection()
    cur = conn.cursor()
    if ticket_ids:
        query = sql.SQL("SELECT * FROM tickets WHERE id IN %s")
        cur.execute(query, (tuple(ticket_ids),))
    else:
        cur.execute("SELECT * FROM tickets")
    tickets = cur.fetchall()
    cur.close()
    conn.close()
    return tickets


def get_last_analysis():
    """
    Purpose: Get the most recent analysis run and associated ticket analysis results.
    """
    # Create the database connection
    conn = get_db_connection()
    
    try:
        with conn.cursor() as cur:
            # Get the most recent analysis run
            cur.execute("SELECT * FROM analysis_runs ORDER BY id DESC LIMIT 1")
            analysis = cur.fetchone()  # Use fetchone since we expect only 1 row

            if not analysis:
                return None, None  # If no analysis run exists, return None
            
            # Get ticket analysis results for the most recent analysis run
            query = sql.SQL("SELECT * FROM ticket_analysis WHERE analysis_run_id = %s")
            cur.execute(query, (analysis[0],))  # Use analysis[0] as the analysis_run_id
            ticket_analysis_results = cur.fetchall()

        return analysis, ticket_analysis_results

    finally:
        # Always close the connection
        conn.close()


