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

def trySendMessage(to, subject, contents):
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

def sendDeactiveClient(clientIdentity, msg, errorLog=None, to=ts.MAIL_RECIPIENTS):
    tdstyle = 'style="padding: 12px 15px;"'
    tdstyleRightAlign = 'style="padding: 12px 15px; text-align: right;"'

    s = f"Client Deactivated: {clientIdentity.Material} ({clientIdentity.Id})"
    b = f'''
        <h3>The Transparency of Randomness has deactivated a client</h3>
        <p style="color: #5A3C78;">
            Stop message: {msg}
        </p>
        <p>
            <b>Client details:</b><br />
            Id: {clientIdentity.Id}<br />
            Position: {clientIdentity.Position}<br />
            IP: {clientIdentity.IP}<br />
            Material: {clientIdentity.Material}<br />
            Latin: {clientIdentity.Latin}
        </p>
    '''
    if errorLog is not None:
        b = b + f'''
            <table>
                <thead>
                    <tr style="background-color: #288C78; color: #FFFFFF; text-align: left;">
                        <td {tdstyle}>Time</td>
                        <td {tdstyle}>Code</td>
                        <td {tdstyle}>Type</td>
                        <td {tdstyle}>Message</td>
                    </tr>
                </thead>
                <tbody>
        '''
        i = 0
        for log in errorLog:
            col = "#F1F1F1" if (i % 2 == 0) else "#FCFCFC"
            if log.Type == "ERROR":
                col = "#5A3C78"
            b = b + f'''
                <tr  style="border-bottom: 2px solid #009879; background-color: {col};">
                    <td {tdstyle}>{log.Time}</td>
                    <td {tdstyle}>{log.MessageCode}</td>
                    <td {tdstyle}>{log.Type}</td>
                    <td {tdstyle}>{log.Message}</td>
                </tr>
            '''
            i += 1
    b = b + '''
            </tbody>
        </table>
    '''
    b = b.replace("\n", "")
    trySendMessage(to, s, b)

def sendStatisticMail(data, to=ts.MAIL_RECIPIENTS):
    tdstyle = 'style="padding: 12px 15px;"'
    tdstyleBold = 'style="padding: 12px 15px; font-weight: bold;"'
    tdstyleRightAlign = 'style="padding: 12px 15px; text-align: right;"'

    s = "Status Report"
    b = f'''
        <table>
            <thead style="background-color: #288C78; color: #FFFFFF; text-align: left;">
                <tr style="background-color: #288C78; color: #FFFFFF; text-align: left;">
                    <td {tdstyle}>Position</td>
                    <td {tdstyle}>Name</td>
                    <td {tdstyle}>2 Hour</td>
                    <td {tdstyle}>avg.</td>
                    <td {tdstyle}>4 Hour</td>
                    <td {tdstyle}>avg.</td>
                    <td {tdstyle}>Day</td>
                    <td {tdstyle}>avg.</td>
                    <td {tdstyle}>Event</td>
                    <td {tdstyle}>avg.</td>
                </tr>
            </thead>
            <tbody>
    '''
    i = 0
    for d in data:
        b = b + f'''
            <tr  style="border-bottom: 2px solid #009879; background-color: {"#F1F1F1" if (i % 2 == 0) else "#FCFCFC"};">
                <td {tdstyleBold}>{str(d[0])}</td>
                <td {tdstyleBold}>{str(d[1])}</td>
                <td {tdstyleRightAlign}>{d[2]}</td>
                <td {tdstyleRightAlign}>{float(d[3]):.2f}</td>
                <td {tdstyleRightAlign}>{d[4]}</td>
                <td {tdstyleRightAlign}>{float(d[5]):.2f}</td>
                <td {tdstyleRightAlign}>{d[6]}</td>
                <td {tdstyleRightAlign}>{float(d[7]):.2f}</td>
                <td {tdstyleRightAlign}>{d[8]}</td>
                <td {tdstyleRightAlign}>{float(d[9]):.2f}</td>
            </tr>
        '''
        i += 1
    b = b + '''
            </tbody>
        </table>
    '''
    b = b.replace("\n", "")
    trySendMessage(to, s, b)

def sendTestMessage(to=ts.MAIL_RECIPIENTS):
    s = "Test message"
    b = "This is a test message from The Transparency of Randomness."
    trySendMessage(to, s, b)

def sendTestDeactiveClient(to=ts.MAIL_RECIPIENTS):
    from tor.base import DBManager
    cid = Utils.EmptyObject()
    setattr(cid, "Id", 11)
    setattr(cid, "IP", "192.134.34.23")
    setattr(cid, "Material", "Pfeffer")
    setattr(cid, "Position", 15)
    setattr(cid, "Latin", "Schinus")
    setattr(cid, "Id", 11)
    errorLog = DBManager.getClientLogByClientId(cid.Id, 20)
    sendDeactiveClient(cid, "Test message", errorLog, to)
