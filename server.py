import uvicorn
from fastapi import FastAPI, HTTPException
import utils
from datetime import datetime

app = FastAPI()

@app.get("/respond")
async def respond(lead_id: int, response: str):
    # Validate response
    if response not in ["interested", "not_interested"]:
        raise HTTPException(status_code=400, detail="Invalid response. Use 'interested' or 'not_interested'.")
    if lead_id < 2:
        raise HTTPException(status_code=400, detail="Invalid lead_id. Must be row number >= 2.")
    
    # Map response to sheet status
    status = "Interested" if response == "interested" else "Not Interested"
    
    # Update Google Sheet
    try:
        sheet = utils.get_sheet()
        data = sheet.get_all_values()
        if lead_id > len(data):
            raise HTTPException(status_code=404, detail="Lead ID not found.")
        # Verify lead exists and is in correct state
        row = data[lead_id - 1]
        if row[5] != 'Y' or row[6] != 'Sent/No Response':
            raise HTTPException(status_code=400, detail="Lead not eligible for response update.")
        # Update Response Status and Notes
        sheet.update_cell(lead_id, 7, status)  # Column G (7)
        sheet.update_cell(lead_id, 8, f"Response via link: {status} at {datetime.utcnow().isoformat()}")  # Column H (8)
        return {"message": f"Updated lead {lead_id} to {status}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating sheet: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)