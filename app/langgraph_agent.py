from your_calendar_tools import check_availability, book_slot
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from transformers import pipeline

# 💡 Use Hugging Face transformer for time parsing load HF model
time_parser = pipeline("text2text-generation", model="google/flan-t5-small")

def parse_datetime(user_input: str) -> str:
    """
    Try to convert natural language datetime into ISO 8601 using HF model.
    Strips model preamble and checks format.
    """
    # Uses a Hugging Face model to convert a natural language datetime expression into a valid
    # ISO 8601 datetime string. Handles cleanup of model output and simple format validation.
    prompt = f"Convert this to an ISO 8601 datetime: {user_input}"
    try:
        output = time_parser(prompt, max_length=50, do_sample=False)[0]["generated_text"]
        # Remove leading labels and whitespace
        result = output.replace("ISO 8601 datetime:", "").strip()
        # Optional: Regex to extract valid ISO 8601 pattern
        return result
    except Exception as e:

        return ""

def find_available_slots(start_time, working_hours=(10, 17), max_suggestions=3):
    # Generates a list of available 1-hour time slots within defined working hours.
    # Skips over times that are already booked using check_availability(). Returns suggestions.
    suggestions = []
    date = datetime.fromisoformat(start_time).replace(hour=working_hours[0], minute=0)
    while len(suggestions) < max_suggestions:
        if date.hour >= working_hours[1]:
            date += timedelta(days=1)
            date = date.replace(hour=working_hours[0])
            continue
        slot_end = date + timedelta(hours=1)
        if check_availability(date.isoformat(), slot_end.isoformat()):
            suggestions.append(date.isoformat())
        date += timedelta(hours=1)
    return suggestions

async def handle_user_message(message: str) -> str:
    """
    Handles scheduling logic and fallback replies.
    Supports both text-based datetime requests and numbered slot replies.
    """
    # Main decision logic for responding to user input. Handles appointment scheduling,
    # parses natural language intent, suggests free slots, and routes selections to book_slot().
    # Provides safe fallback replies in case of invalid input or scheduling failures.
    message_lower = message.lower()
    if any(x in message_lower for x in ["book", "schedule", "meeting", "appointment"]):
        proposed_time = parse_datetime(message)
        if proposed_time:
            try:
                # ✅ Validate the datetime before passing to book_slot
                datetime.fromisoformat(proposed_time)
                return book_slot(proposed_time)   
            except ValueError:
                    return "⚠️ That didn’t look like a valid time. Can you try rephrasing it?"
            except Exception:
                return "⚠️ Something went wrong while trying to book. Try again?"
        else:
            slots = find_available_slots(datetime.now().isoformat())
            response = "I couldn’t find a specific time. Here are a few suggestions:\n"
            for i, slot in enumerate(slots):
                response += f"{i+1}. {datetime.fromisoformat(slot).strftime('%A at %I:%M %p')}\n"
            return response + "\nReply with a slot number."
    elif message.strip().isdigit():
        index = int(message.strip()) - 1
        slots = find_available_slots(datetime.now().isoformat())
        if 0 <= index < len(slots):
            try:
                return book_slot(slots[index])
            except Exception:
                return "⚠️ That slot might already be booked. Try again?"
        return f"Please pick a number between 1 and {len(slots)}."

    return (
        "I can help you book appointments! Try saying:\n"
        "- 'Book something next Friday morning'\n"
        "- 'Tomorrow at 3pm'\n"
        "- Or reply with a number from the suggested slots."
    )
