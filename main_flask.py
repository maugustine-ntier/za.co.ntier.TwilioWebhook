from flask import Flask, request, Response
import os
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine, MetaData, Table, Column, Numeric, Integer, VARCHAR, update
from sqlalchemy import select
import logging
import datetime
from validate_twilio_request import validate_twilio_request

app = Flask(__name__)

@app.route("/hook", methods=["POST"])
@validate_twilio_request
def hook():
    resp = MessagingResponse()
    incoming_msg = request.values.get('Body', '').lower()
    from_ph = request.values.get('From', '').lower()
    # response = MessagingResponse()
    # msg = response.message(f"Hi {request.form['From']}, you said: {request.form['Body']}")
    # establish connections
    engine = create_engine("postgresql+psycopg2://" + os.environ["DB_USER"] + ":" + os.environ["DB_PASSWORD"] + "@" + os.environ["DB_HOST"] + ":" + os.environ["DB_PORT"] + "/" + os.environ["DB_NAME"])

    # initialize the Metadata Object
    meta = MetaData()
    meta.reflect(bind=engine)
    # Get the `books` table from the Metadata object
    ADUSER = meta.tables['ad_user']

    # update
    if incoming_msg == "subscribe" or incoming_msg == "start":
        with engine.begin() as conn:
            #stmt = select(ADUSER.c.name,ADUSER.c.opt_in_date,ADUSER.c.phone).where(ADUSER.c.phone == request.form['From'].removeprefix("whatsapp:"))
            #output = conn.execute(stmt).fetchall()
            #print(output)
            u = update(ADUSER)
            u = u.values(opt_in_date=datetime.datetime.now())
            u = u.where(ADUSER.c.phone == request.form['From'].removeprefix("whatsapp:"))
            print(u)
            conn.execute(u)
            #stmt = select(ADUSER.c.name,ADUSER.c.opt_in_date,ADUSER.c.phone).where(ADUSER.c.phone == request.form['From'].removeprefix("whatsapp:"))
            #output = conn.execute(stmt).fetchall()
            #print(output)
    if incoming_msg == "unsubscribe" or incoming_msg == "stop":
        with engine.begin() as conn:
            u = update(ADUSER)
            u = u.values(opt_out_date=datetime.datetime.now())
            u = u.where(ADUSER.c.phone == from_ph.removeprefix("whatsapp:"))
            print(u)
            conn.execute(u)

    return Response(str(resp), mimetype="application/xml")


if __name__ == '__main__':
    app.run(debug=True)
