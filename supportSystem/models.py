from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from io import StringIO
import re
import os
import mimetypes
from django.utils.safestring import mark_safe
from markdown import markdown
from markdown.extensions import Extension
import uuid
from customersSupportSystem import settings as cs_settings
from .templated_email import send_templated_mail

try:
    from .validators import validate_file_extension
except:
    from supportSystem.validators import validate_file_extension


class EscapeHtml(Extension):
    def extendMarkdown(self, md, md_globals):
        del md.preprocessors['html_block']
        del md.inlinePatterns['html']

def get_markdown(text):
    if not text:
        return ""

    pattern = fr'([\[\s\S\]]*?)\(([\s\S]*?):([\s\S]*?)\)'
    # Regex check
    if re.match(pattern, text):
        # get get value of group regex
        scheme = re.search(pattern, text, re.IGNORECASE).group(2)
        # scheme check
        if scheme in cs_settings.ALLOWED_URL_SCHEMES:
            replacement = '\\1(\\2:\\3)'
        else:
            replacement = '\\1(\\3)'

        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return mark_safe(
        markdown(
            text,
            extensions=[
                EscapeHtml(), 'markdown.extensions.nl2br',
                'markdown.extensions.fenced_code'
            ]
        )
    )


class Queue(models.Model):

    title = models.CharField(
        _('Title'),
        max_length=100,
    )

    slug = models.SlugField(
        _('Slug'),
        max_length=50,
        unique=True,
    )

    email_address = models.EmailField(
        _('E-Mail Address'),
        blank=True,
        null=True,
    )

    locale = models.CharField(
        _('Locale'),
        max_length=10,
        blank=True,
        null=True,
    )

    allow_email_submission = models.BooleanField(
        _('Allow E-Mail Submission?'),
        blank=True,
        default=False,
    )

    email_box_host = models.CharField(
        _('E-Mail Hostname'),
        max_length=200,
        blank=True,
        null=True,
    )

    email_box_port = models.IntegerField(
        _('E-Mail Port'),
        blank=True,
        null=True,
    )

    email_box_ssl = models.BooleanField(
        _('Use SSL for E-Mail?'),
        blank=True,
        default=False,
    )

    email_box_user = models.CharField(
        _('E-Mail Username'),
        max_length=200,
        blank=True,
        null=True,
    )

    email_box_pass = models.CharField(
        _('E-Mail Password'),
        max_length=200,
        blank=True,
        null=True,
    )

    email_box_imap_folder = models.CharField(
        _('IMAP Folder'),
        max_length=100,
        blank=True,
        null=True,
    )


    permission_name = models.CharField(
        _('Django auth permission name'),
        max_length=72,
        blank=True,
        null=True,
        editable=False,
    )

    email_box_interval = models.IntegerField(
        _('E-Mail Check Interval'),
        blank=True,
        null=True,
        default='5',
    )

    email_box_last_check = models.DateTimeField(
        blank=True,
        null=True,
        editable=False,
    )

    logging_type = models.CharField(
        _('Logging Type'),
        max_length=5,
        choices=(
            ('none', _('None')),
            ('debug', _('Debug')),
            ('info', _('Information')),
            ('warn', _('Warning')),
            ('error', _('Error')),
            ('crit', _('Critical'))
        ),
        blank=True,
        null=True,
    )

    logging_dir = models.CharField(
        _('Logging Directory'),
        max_length=200,
        blank=True,
        null=True,
    )

    default_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='default_owner',
        blank=True,
        null=True,
        verbose_name=_('Default owner'),
    )


    def __str__(self):
        return "%s" % self.title

    class Meta:
        ordering = ('title',)
        verbose_name = _('Queue')
        verbose_name_plural = _('Queues')

    def _from_address(self):
        if not self.email_address:

            # must check if given in format "Foo <foo@example.com>"

            default_email = re.match(".*<(?P<email>.*@*.)>", str(os.getenv('DEFAULT_FROM_EMAIL')))
            if default_email is not None:
                # already in the right format, so just include it here
                return u'NO QUEUE EMAIL ADDRESS DEFINED %s' % os.getenv('DEFAULT_FROM_EMAIL')
            else:
                return u'NO QUEUE EMAIL ADDRESS DEFINED <%s>' % os.getenv('DEFAULT_FROM_EMAIL')
        else:
            return u'%s <%s>' % (self.title, self.email_address)

    from_address = property(_from_address)



    def prepare_permission_name(self):
        # Prepare the permission associated to this Queue
        basename = "queue_access_%s" % self.slug
        self.permission_name = "supportSystem.%s" % basename
        return basename

    def save(self, *args, **kwargs):

        if not self.email_box_imap_folder:
            self.email_box_imap_folder = 'INBOX'

        if not self.email_box_port:
            self.email_box_port = 993

        super(Queue, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(Queue, self).delete(*args, **kwargs)

def mk_secret():
    return str(uuid.uuid4())


class Ticket(models.Model):

    OPEN_STATUS = 1
    REOPENED_STATUS = 2
    RESOLVED_STATUS = 3
    CLOSED_STATUS = 4


    STATUS_CHOICES = (
        (OPEN_STATUS, _('Open')),
        (REOPENED_STATUS, _('Reopened')),
        (RESOLVED_STATUS, _('Resolved')),
        (CLOSED_STATUS, _('Closed')),
    )

    PRIORITY_CHOICES = (
        (1, _('1. Critical')),
        (2, _('2. High')),
        (3, _('3. Normal')),
        (4, _('4. Low')),
        (5, _('5. Very Low')),
    )

    title = models.CharField(
        _('Title'),
        max_length=200,
    )

    queue = models.ForeignKey(
        Queue,
        on_delete=models.CASCADE,
        verbose_name=_('Queue'),
    )

    created = models.DateTimeField(
        _('Created'),
        blank=True,
        help_text=_('Date this ticket was first created'),
    )

    modified = models.DateTimeField(
        _('Modified'),
        blank=True,
        help_text=_('Date this ticket was most recently changed.'),
    )

    submitter_email = models.EmailField(
        _('Submitter E-Mail'),
        blank=True,
        null=True,
        help_text=_('The submitter will receive an email for all public '
                    'follow-ups left for this task.'),
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_to',
        blank=True,
        null=True,
        verbose_name=_('Assigned to'),
    )

    status = models.IntegerField(
        _('Status'),
        choices=STATUS_CHOICES,
        default=OPEN_STATUS,
    )


    description = models.TextField(
        _('Description'),
        blank=True,
        null=True,
        help_text=_('The content of the customers query.'),
    )

    resolution = models.TextField(
        _('Resolution'),
        blank=True,
        null=True,
        help_text=_('The resolution provided to the customer by our staff.'),
    )

    priority = models.IntegerField(
        _('Priority'),
        choices=PRIORITY_CHOICES,
        default=3,
        blank=3,
        help_text=_('1 = Highest Priority, 5 = Low Priority'),
    )

    def send(self, roles, dont_send_to=None, **kwargs):
        recipients = set()

        if dont_send_to is not None:
            recipients.update(dont_send_to)

        recipients.add(self.queue.email_address)

        def send(role, recipient):
            if recipient and recipient not in recipients and role in roles:
                template, context = roles[role]
                send_templated_mail(template, context, recipient, sender=self.queue.from_address, **kwargs)
                recipients.add(recipient)

        send('submitter', self.submitter_email)

        if self.assigned_to:
            send('assigned_to', self.assigned_to.email)

        return recipients

    def _get_assigned_to(self):
        if not self.assigned_to:
            return _('Unassigned')
        else:
            if self.assigned_to.get_full_name():
                return self.assigned_to.get_full_name()
            else:
                return self.assigned_to.get_username()

    get_assigned_to = property(_get_assigned_to)

    def _get_ticket(self):
        return u"[%s]" % self.ticket_for_url

    ticket = property(_get_ticket)

    def _get_ticket_for_url(self):
        return u"%s-%s" % (self.queue.slug, self.id)

    ticket_for_url = property(_get_ticket_for_url)


    def _get_status(self):
        return u'%s' % (self.get_status_display())

    get_status = property(_get_status)



    def get_submitter_userprofile(self):
        User = get_user_model()
        try:
            return User.objects.get(email=self.submitter_email)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None

    class Meta:
        get_latest_by = "created"
        ordering = ('id',)
        verbose_name = _('Ticket')
        verbose_name_plural = _('Tickets')

    def __str__(self):
        return '%s %s' % (self.id, self.title)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('supportSystem:view', args=(self.id,))

    def save(self, *args, **kwargs):
        if not self.id:
            # This is a new ticket as no ID yet exists.
            self.created = timezone.now()

        if not self.priority:
            self.priority = 3

        self.modified = timezone.now()

        if len(self.title) > 200:
            self.title = self.title[:197] + "..."

        super(Ticket, self).save(*args, **kwargs)

    @staticmethod
    def queue_and_id_from_query(query):
        parts = query.split('-')
        queue = '-'.join(parts[0:-1])
        return queue, parts[-1]

    def get_markdown(self):
        return get_markdown(self.description)

    @property
    def get_resolution_markdown(self):
        return get_markdown(self.resolution)

    def add_email_to_ticketcc_if_not_in(self, email=None, user=None, ticketcc=None):
        if ticketcc:
            email = ticketcc.display
        elif user:
            if user.email:
                email = user.email
            else:
                # Ignore if user has no email address
                return
        elif not email:
            raise ValueError('You must provide at least one parameter to get the email from')

        # Prepare all emails already into the ticket
        ticket_emails = [x.display for x in self.ticketcc_set.all()]
        if self.submitter_email:
            ticket_emails.append(self.submitter_email)
        if self.assigned_to and self.assigned_to.email:
            ticket_emails.append(self.assigned_to.email)

        # Check that email is not already part of the ticket
        if email not in ticket_emails:
            if ticketcc:
                ticketcc.ticket = self
                ticketcc.save(update_fields=['ticket'])
            elif user:
                ticketcc = self.ticketcc_set.create(user=user)
            else:
                ticketcc = self.ticketcc_set.create(email=email)
            return ticketcc


class FollowUpManager(models.Manager):

    def private_followups(self):
        return self.filter(public=False)

    def public_followups(self):
        return self.filter(public=True)


class FollowUp(models.Model):

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        verbose_name=_('Ticket'),
    )

    date = models.DateTimeField(
        _('Date'),
        default=timezone.now
    )

    title = models.CharField(
        _('Title'),
        max_length=200,
        blank=True,
        null=True,
    )

    comment = models.TextField(
        _('Comment'),
        blank=True,
        null=True,
    )

    public = models.BooleanField(
        _('Public'),
        blank=True,
        default=False,
        help_text=_(
            'Public tickets are viewable by the submitter and all '
            'staff, but non-public tickets can only be seen by staff.'
        ),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_('User'),
    )

    new_status = models.IntegerField(
        _('New Status'),
        choices=Ticket.STATUS_CHOICES,
        blank=True,
        null=True,
        help_text=_('If the status was changed, what was it changed to?'),
    )

    message_id = models.CharField(
        _('E-Mail ID'),
        max_length=256,
        blank=True,
        null=True,
        help_text=_("The Message ID of the submitter's email."),
        editable=False,
    )

    objects = FollowUpManager()


    class Meta:
        ordering = ('date',)
        verbose_name = _('Follow-up')
        verbose_name_plural = _('Follow-ups')

    def __str__(self):
        return '%s' % self.title

    def get_absolute_url(self):
        return u"%s#followup%s" % (self.ticket.get_absolute_url(), self.id)

    def save(self, *args, **kwargs):
        t = self.ticket
        t.modified = timezone.now()
        t.save()
        super(FollowUp, self).save(*args, **kwargs)

    def get_markdown(self):
        return get_markdown(self.comment)




class TicketChange(models.Model):

    followup = models.ForeignKey(
        FollowUp,
        on_delete=models.CASCADE,
        verbose_name=_('Follow-up'),
    )

    field = models.CharField(
        _('Field'),
        max_length=100,
    )

    old_value = models.TextField(
        _('Old Value'),
        blank=True,
        null=True,
    )

    new_value = models.TextField(
        _('New Value'),
        blank=True,
        null=True,
    )

    def __str__(self):
        out = '%s ' % self.field
        if not self.new_value:
            out += _('removed')
        elif not self.old_value:
            out += _('set to %s') % self.new_value
        else:
            out += _('changed from "%(old_value)s" to "%(new_value)s"') % {
                'old_value': self.old_value,
                'new_value': self.new_value
            }
        return out

    class Meta:
        verbose_name = _('Ticket change')
        verbose_name_plural = _('Ticket changes')


def attachment_path(instance, filename):
    """Just bridge"""
    return instance.attachment_path(filename)


class Attachment(models.Model):

    file = models.FileField(
        _('File'),
        upload_to=attachment_path,
        max_length=1000,
        validators=[validate_file_extension]
    )

    filename = models.CharField(
        _('Filename'),
        blank=True,
        max_length=1000,
    )

    mime_type = models.CharField(
        _('MIME Type'),
        blank=True,
        max_length=255,
    )

    size = models.IntegerField(
        _('Size'),
        blank=True,
        help_text=_('Size of this file in bytes'),
    )

    def __str__(self):
        return '%s' % self.filename

    def save(self, *args, **kwargs):

        if not self.size:
            self.size = self.get_size()

        if not self.filename:
            self.filename = self.get_filename()

        if not self.mime_type:
            self.mime_type = \
                mimetypes.guess_type(self.filename, strict=False)[0] or \
                'application/octet-stream'

        return super(Attachment, self).save(*args, **kwargs)

    def get_filename(self):
        return str(self.file)

    def get_size(self):
        return self.file.file.size

    def attachment_path(self, filename):
        """Provide a file path that will help prevent files being overwritten, by
        putting attachments in a folder off attachments for ticket/followup_id/.
        """
        assert NotImplementedError(
            "This method is to be implemented by Attachment classes"
        )

    class Meta:
        ordering = ('filename',)
        verbose_name = _('Attachment')
        verbose_name_plural = _('Attachments')
        abstract = True


class FollowUpAttachment(Attachment):
    followup = models.ForeignKey(
        FollowUp,
        on_delete=models.CASCADE,
        verbose_name=_('Follow-up'),
    )

    def attachment_path(self, filename):

        os.umask(0)
        path = 'supportSystem/attachments/{id_}'.format(
            id_=self.followup.id)
        att_path = os.path.join(settings.MEDIA_ROOT, path)
        if settings.DEFAULT_FILE_STORAGE == "django.core.files.storage.FileSystemStorage":
            if not os.path.exists(att_path):
                os.makedirs(att_path, 0o777)
        return os.path.join(path, filename)


class EmailTemplate(models.Model):
    template_name = models.CharField(
        _('Template Name'),
        max_length=100,
    )

    subject = models.CharField(
        _('Subject'),
        max_length=100,
    )

    heading = models.CharField(
        _('Heading'),
        max_length=100,
    )


    html = models.TextField(
        _('HTML'),
        help_text=_('The same context is available here as in plain_text, above.'),
    )

    locale = models.CharField(
        _('Locale'),
        max_length=10,
        blank=True,
        null=True,
        help_text=_('Locale of this template.'),
    )

    def __str__(self):
        return '%s' % self.template_name

    class Meta:
        ordering = ('template_name', 'locale')
        verbose_name = _('e-mail template')
        verbose_name_plural = _('e-mail templates')









