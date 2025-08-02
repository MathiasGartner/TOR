import logging
log = logging.getLogger(__name__)

import yagmail

from tor.base.utils import Utils
import tor.TORSettings as ts

yag = None
try:
    yag = yagmail.SMTP(ts.MAIL_USERNAME, oauth2_file=ts.MAIL_OAUTH_FILE)
except Exception as e:
    log.warning("could not initialize MailManager")
    log.warning(f"{repr(e)}")

def trySendMessage(to, subject, contents, description):
    log.info("will send mail")
    if yag is not None:
        if ts.SEND_MAIL:
            try:
                yag.send(to=to, subject=subject, contents=contents)
                log.info(f"Mail \"{subject}\" sent to \"{to}\".")
            except Exception as e:
                log.warning(f"Could not send message \"{subject}\" to \"{to}\". Message: \"{contents}\"")
                log.warning(f"{repr(e)}")
        else:
            log.warning("Sending Mail Messages is disabled (SEND_MAIL = False)")
    else:
        log.warning("MailManager not initialized")

def sendTestMessage(to=ts.MAIL_RECIPIENTS):
    s = "TOR: test"
    b = "This is a test message from The Transparency of Randomness."
    trySendMessage(to, s, b, "Test message")

def sendDeactiveClient(clientIdentity, to=ts.MAIL_RECIPIENTS):
    s = f"TOR: deactivate client {clientIdentity.Id} ({clientIdentity.Material})"
    b = (f"<h3>The Transparency of Randomness has deactivated a client</h3>"
         f"<p>"
         f"<b>Client details:</b><br />"
         f"Id: {clientIdentity.Id}<br />"
         f"Position: {clientIdentity.Position}<br />"
         f"IP: {clientIdentity.IP}<br />"
         f"Material: {clientIdentity.Material}<br />"
         f"Latin: {clientIdentity.Latin}"
         f"</p>"
        )
    #TODO: add error log to message
    trySendMessage(to, s, b, "deactivate client")

def sendTestDeactiveClient(to=ts.MAIL_RECIPIENTS):
    cid = Utils.EmptyObject()
    setattr(cid, "Id", 11)
    setattr(cid, "IP", "192.134.34.23")
    setattr(cid, "Material", "Pfeffer")
    setattr(cid, "Position", 15)
    setattr(cid, "Latin", "Schinus")
    setattr(cid, "Id", 11)
    sendDeactiveClient(cid, to)

def sendStatisticMail(data, to=ts.MAIL_RECIPIENTS):
    s = "TOR: status report"

    tdstyle = 'style="padding: 12px 15px;"'
    tdstyleBold = 'style="padding: 12px 15px; font-weight: bold;"'
    tdstyleRightAlign = 'style="padding: 12px 15px; text-align: right;"'
    b = '<table>'
    b = b + '<thead style="background-color: #009879; color: #ffffff; text-align: left;">'
    b = b + f'<tr style="background-color: #009879; color: #ffffff; text-align: left;">'
    b = b + f'<td {tdstyle}>Position</td>'
    b = b + f'<td {tdstyle}>Name</td>'
    b = b + f'<td {tdstyle}>2 Hour</td>'
    b = b + f'<td {tdstyle}>avg.</td>'
    b = b + f'<td {tdstyle}>4 Hour</td>'
    b = b + f'<td {tdstyle}>avg.</td>'
    b = b + f'<td {tdstyle}>Day</td>'
    b = b + f'<td {tdstyle}>avg.</td>'
    b = b + f'<td {tdstyle}>Event</td>'
    b = b + f'<td {tdstyle}>avg.</td>'
    b = b + f'</tr>'
    b = b + f'</thead>'
    b = b + f'<tbody>'
    i = 0
    for d in data:
        b = b + f'<tr  style="border-bottom: 2px solid #009879; background-color: {"#f3f3f3" if (i % 2 == 0) else "#fcfcfc"};">'
        b = b + f'<td {tdstyleBold}>{str(d[0])}</td>'
        b = b + f'<td {tdstyleBold}>{str(d[1])}</td>'
        b = b + f'<td {tdstyleRightAlign}>{d[2]}</td>'
        b = b + f'<td {tdstyleRightAlign}>{float(d[3]):.2f}</td>'
        b = b + f'<td {tdstyleRightAlign}>{d[4]}</td>'
        b = b + f'<td {tdstyleRightAlign}>{float(d[5]):.2f}</td>'
        b = b + f'<td {tdstyleRightAlign}>{d[6]}</td>'
        b = b + f'<td {tdstyleRightAlign}>{float(d[7]):.2f}</td>'
        b = b + f'<td {tdstyleRightAlign}>{d[8]}</td>'
        b = b + f'<td {tdstyleRightAlign}>{float(d[9]):.2f}</td>'
        b = b + '</tr>'
        i += 1
    b = b + '</tbody>'
    b = b + '</table>'
    trySendMessage(to, s, b, "status report")
