"""
    This file contains the AI agent flow
"""
from langgraph.graph import LangGraph, END
from typing import TypedDict, List, Dict
from models import analyze_tickets, create_ticket_analysis, get_tickets


def tickets_analyze(tickets):
    fetch_tickets_node=LangGraph.node(
        "fetch_tickets_ids",
        func=get_tickets,
        inputs=[tickets]
    )
    summarize_node = LangGraph.node(
        "summarize_all_tickets",
        model="google/flan-t5-base",
        prompt="Summarize these tickets into a brief description: {tickets_text}",
        inputs=[fetch_tickets_node]
    )

    # Insert data into analysis_runs table
    analysis_runs_insert_node=LangGraph.node(
        "analyze_tickets",
        func=analyze_tickets,
        inputs=[summarize_node]  # Input will be the output from the summarize node
    )

    # Iterate over individual tickets
    def iterate_tck(analysis_id,tickets):
        ticket_analysis_nodes = [analysis_id]
        for ticket in tickets:
            # Call individual ticket analysis logic here for each ticket
            ticket_id = ticket[0]  # Assuming each ticket has a ticket_id field
            ticket_text=ticket[1]
            summarize_tck_node = LangGraph.node(
                "summarize_ticket",
                model="google/flan-t5-base",
                prompt="Summarize the ticket into a brief description: {ticket_text}",
                input=[ticket_text]
            )
            
            categorize_tck_node = LangGraph.node(
                "categorizer",
                model="google/flan-t5-base",
                prompt="Categorize this ticket as one of the following: billing, bug, feature request. Ticket text: {ticket_text}",
                input=[ticket_text]
            )

            priority_tck_node = LangGraph.node(
                "priority_assigner",
                model="google/flan-t5-base",
                prompt="Given the following ticket, assign a priority (low, medium, high) based on urgency and complexity: {ticket_text}",
                input=[ticket_text]
            )
            
            # Each ticket gets its analysis inserted in the database
            analysis_tck_ind_insert_node = LangGraph.node(
                "analyze_ticket_ind",
                func=create_ticket_analysis,
                inputs=[analysis_id,ticket_id, categorize_tck_node, priority_tck_node, summarize_tck_node]  # Inputs are node outputs and ticket_id
            )
            ticket_analysis_nodes.append(analysis_tck_ind_insert_node)
            # Return result for further analysis or final actions
            return ticket_analysis_nodes
        # Individual ticket analysis node
    individual_ticket_analysis_node = LangGraph.node(
        "ind_process_nodes",
        func=iterate_tck,
        inputs=[analysis_runs_insert_node,fetch_tickets_node]
    )
    workflow=LangGraph()
    # Adding nodes to the workflow
    workflow.add_node("fetching_tickets",fetch_tickets_node)
    workflow.add_node("summarizing_tickets", summarize_node)  # Summarizing all tickets
    workflow.add_node("analyzing_summary", analysis_runs_insert_node)  # Analyzing summary of tickets
    workflow.add_node("individual_ticket_analysis", individual_ticket_analysis_node)  # Process individual ticket analysis

    # Define the entry point of the workflow
    workflow.set_entry_point("fetching_tickets")

    # Define the edges between the nodes (defining the flow of actions)
    workflow.add_edge("fetching_tickets","summarizing_tickets")
    workflow.add_edge("summarizing_tickets", "analyzing_summary")  # Summarize tickets -> Analyze summary
    workflow.add_edge("analyzing_summary", "individual_ticket_analysis")  # Analyze summary -> Individual ticket analysis

    # End of the workflow
    workflow.add_edge("individual_ticket_analysis", "END")  # Insert ticket data -> END of the workflow

    return workflow
