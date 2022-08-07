import os
from icalendar import Calendar, Event, vCalAddress, vText
import datetime
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


"""
Renders the content based on a html or txt template 
  templateName: string name of the template that should be retrieved. Both a .txt file should be retrieved from ./plaintext and a html file from ./html 
  context: a dictionary with the context that should be replaced in the template
  returns a dictionary containing the 'text_content' and the 'html_content'
"""


def render_content(templateName, context):
    # Txt template
    path = os.path.join(".", "plaintext", templateName+".txt")
    text_content = render_to_string(path, context)

    # HTML template
    path = os.path.join(".", "html", templateName+".html")
    html_content = render_to_string(path, context)

    return [text_content, html_content]


""" 
Function used to send a mail through our smtp server
  fromAddres: string containing the from address. Needs to be set in the google workspace
  toAddress: list of strings containing the receivers
  toAddress: list of strings containing the receivers
  subject: string containing the subject
  templateName: string name of the template that should be retrieved. Both a .txt file should be retrieved from ./plaintext and a html file from ./html 
  context: a dictionary with the context that should be replaced in the template
  ccAddresses: list of strings containing the receivers
  bccAddresses: list of strings containing the receivers
  calendar: in case provided a calendar meeting is created using the following possible options:
              attendees: string[] a list of attendee email adresses. Example [chris@dejong.lu, djchris261@hotmail.com]
              summary: string, the name of the meeting
              start: datetime object containing the start date 
              end: datetime object containing the end date 
              organizer_email: the organizer email of the event
              organizer_name: the name of the organizer
              location: the adres of the event
"""


def send_mail(fromAddres, toAdresses, subject, templateName, context={}, ccAddresses=[], bccAdresses=[], calendar={}):
    # First render the content from the template
    text_content, html_content = render_content(templateName, context)

    # Then create the message based on the information provided and add the html content as alternative
    # Adding the html content as alternative ensures that everybody is able to read the message
    email = EmailMultiAlternatives(subject=subject, body=text_content,
                                   from_email=fromAddres, to=toAdresses, cc=ccAddresses, bcc=bccAdresses, headers={'List-Unsubscribe': 'https://www.<your-website.here>.lu/unsubscribe'})
    email.attach_alternative(html_content, "text/html")

    # Next add the calendar invite in case one has been provided
    if calendar:
        # Create the calendar event iself
        cal = Calendar()

        # Add the attendees of the calendar file
        attendees = calendar['attendees']
        for attendee in attendees:
            ics_value = 'MAILTO:' + attendee
            cal.add('attendee', ics_value)

        # Next we need to create the event itself
        event = Event()
        event.add('summary', calendar['summary'])
        event.add('dtstart', calendar['start'])
        event.add('dtend', calendar['end'])
        event.add('dtstamp', datetime.datetime.today())

        # Add the organizer
        organizer = vCalAddress('MAILTO:' + calendar['organizer_email'])
        organizer.params['cn'] = vText(calendar['organizer_name'])
        organizer.params['role'] = vText('Agent')
        event['organizer'] = organizer
        event['location'] = vText(calendar['location'])

        # Add the event to the ics file
        cal.add_component(event)

        # Store the ics file in a temporary directory
        # To make sure that we do not send a wrong invite, we use first 5 letters of the summary, organizer and attendees of the event to create the file temporarely
        filename = calendar['summary'][0:5] + calendar['organizer_email'][0:5]
        for attendee in attendees:
            filename += attendee[0:5]
        filename += ".ics"
        path = os.path.join('.', filename)
        f = open(path, 'wb')
        f.write(cal.to_ical())
        f.close()

        # Attach the file to the email
        email.attach_file(path, 'text/calendar')

        # And delete the temporary .ics file
        os.remove(path)

    email.send()
