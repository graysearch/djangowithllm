import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse

# Base URL for your FastAPI service (ensure this matches your configuration)
FASTAPI_BASE_URL = "http://127.0.0.1:8001"

def home(request):
    """
    Page 1: Display a form with a dropdown for sport selection.
    On POST, store the sport in the session, call the FastAPI endpoint
    for sport info, and redirect to page2.
    """
    if request.method == "POST":
        sport = request.POST.get("sport")
        if sport not in ["soccer", "cricket", "basketball"]:
            return render(request, "sports/home.html", {"error": "Invalid sport selected."})
        
        # Save the selected sport in the session
        request.session["selected_sport"] = sport

        # Call FastAPI /sport-info endpoint
        try:
            response = requests.get(f"{FASTAPI_BASE_URL}/sport-info", params={"sport": sport})
            response.raise_for_status()
            data = response.json()
            request.session["sport_info"] = data["description"]
        except Exception as e:
            return HttpResponse(f"Error calling FastAPI: {e}")

        return redirect("page2")
    return render(request, "sports/home.html")


def page2(request):
    """
    Page 2: Display the sport description.
    Provides links to go back to home or proceed to page3.
    """
    sport = request.session.get("selected_sport")
    sport_info = request.session.get("sport_info")
    if not sport or not sport_info:
        return redirect("home")
    return render(request, "sports/page2.html", {"sport": sport, "sport_info": sport_info})


def page3(request):
    """
    Page 3: Display a form for the user to ask a free-form query about the sport.
    On submission, call the FastAPI /gpt endpoint (with context) and store the response.
    """
    if request.method == "POST":
        query = request.POST.get("query")
        if not query:
            return render(request, "sports/page3.html", {"error": "Please enter a query."})
        request.session["user_query"] = query

        # Retrieve the selected sport and its description from the session
        sport = request.session.get("selected_sport")
        sport_info = request.session.get("sport_info")

        # Call FastAPI /gpt endpoint with context information
        try:
            headers = {"Content-Type": "application/json"}
            json_data = {
                "query": query,
                "sport": sport,
                "sport_info": sport_info,
            }
            response = requests.post(f"{FASTAPI_BASE_URL}/gpt", json=json_data, headers=headers)
            response.raise_for_status()
            data = response.json()
            request.session["gpt_response"] = data["response"]
        except Exception as e:
            return HttpResponse(f"Error calling GPT API: {e}")

        return redirect("page4")
    return render(request, "sports/page3.html")


def page4(request):
    """
    Page 4: Display the GPT-generated answer.
    Provides a navigation link to go back to page3.
    """
    gpt_response = request.session.get("gpt_response")
    if not gpt_response:
        return redirect("page3")
    return render(request, "sports/page4.html", {"gpt_response": gpt_response})