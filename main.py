import os
from fastapi import FastAPI, Form, Response, Request, HTTPException
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator 
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine, MetaData,\
    Table, Column, Numeric, Integer, VARCHAR, update
from sqlalchemy import select
import logging
import datetime

app = FastAPI()

@app.post("/hook")
async def chat(
    request: Request, From: str = Form(...), Body: str = Form(...) 
):
    validator = RequestValidator(os.environ["TWILIO_AUTH_TOKEN"])
    form_ = await request.form()
    if not validator.validate(
        str(request.url), 
        form_, 
        request.headers.get("X-Twilio-Signature", "")
    ):
        raise HTTPException(status_code=400, detail="Error in Twilio Signature")

    response = MessagingResponse()
    msg = response.message(f"Hi {From}, you said: {Body}")
    # establish connections
    engine = create_engine("postgresql+psycopg2://" + os.environ["DB_USER"] + ":" + os.environ["DB_PASSWORD"]\
                           + "@" + os.environ["DB_HOST"]\
                           + ":" + os.environ["DB_PORT"]\
                           + "/" + os.environ["DB_NAME"])

    # initialize the Metadata Object
    meta = MetaData()
    meta.reflect(bind=engine)
    # Get the `books` table from the Metadata object
    ADUSER = meta.tables['ad_user']

    # update
    if Body.lower() == "subscribe" or Body.lower() == "start":
        with engine.begin() as conn:
            #stmt = select(ADUSER.c.name,ADUSER.c.opt_in_date,ADUSER.c.phone).where(ADUSER.c.phone == From.removeprefix("whatsapp:"))
            #output = conn.execute(stmt).fetchall()
            #print(output)
            u = update(ADUSER)
            u = u.values(opt_in_date = datetime.datetime.now()) 
            u = u.where(ADUSER.c.phone == From.removeprefix("whatsapp:"))
            print(u)
            conn.execute(u)
            #stmt = select(ADUSER.c.name,ADUSER.c.opt_in_date,ADUSER.c.phone).where(ADUSER.c.phone == From.removeprefix("whatsapp:"))
            #output = conn.execute(stmt).fetchall()
            #print(output)
    if Body.lower() == "unsubscribe" or Body.lower() == "stop":
        with engine.begin() as conn:
            u = update(ADUSER)
            u = u.values(opt_out_date = datetime.datetime.now())
            u = u.where(ADUSER.c.phone == From.removeprefix("whatsapp:")) 
            print(u)
            conn.execute(u)
    
    return Response(content=str(response), media_type="application/xml")