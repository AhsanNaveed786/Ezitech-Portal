def mark_attendance(user_id,role):
    if user_id == None or role == None:
        return {"error": "User ID and role are required."}, 400
     