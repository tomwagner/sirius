import flask
from flask.ext import login

from sirius.models import user
from sirius.models import hardware
from sirius.models.db import db
from sirius.web import webapp
from sirius.testing import base


class TestClaiming(base.Base):

    def test_claim_first(self):
        self.testuser.claim_printer('n5ry-p6x6-kth7-7hc4', 'my test printer')
        hardware.Printer.phone_home('000d6f000273ce0b')
        db.session.commit()
        printer = hardware.Printer.query.first()

        self.assertEqual(printer.owner, self.testuser)

    def test_printer_phone_home_first(self):
        hardware.Printer.phone_home('000d6f000273ce0b')
        self.testuser.claim_printer('n5ry-p6x6-kth7-7hc4', 'my test printer')
        db.session.commit()
        printer = hardware.Printer.query.first()

        self.assertEqual(printer.owner, self.testuser)

    def test_two_claims(self):
        "We expect the newer claim to beat the older claim."
        self.testuser2 = user.User(username="testuser 2")
        db.session.add(self.testuser2)
        db.session.commit()

        self.testuser.claim_printer('n5ry-p6x6-kth7-7hc4', 'my test printer')
        self.testuser2.claim_printer('n5ry-p6x6-kth7-7hc4', 'my test printer 2')

        hardware.Printer.phone_home('000d6f000273ce0b')
        db.session.commit()
        printer = hardware.Printer.query.first()

        self.assertEqual(printer.owner, self.testuser2)


class TestClaimingWeb(base.Base):

    def get_claim_url(self):
        return flask.url_for(
            'landing.claim',
            user_id=self.testuser.id,
            username=self.testuser.username)

    def test_invalid_claim_code(self):
        self.autologin()
        r = self.client.post(self.get_claim_url(), data=dict(
            claim_code='invalid', printer_name='lp'))
        # invalid keeps us on claiming page and doesn't redirect
        self.assert200(r)

    def test_valid_claim_code(self):
        self.autologin()
        r = self.client.post(self.get_claim_url(), data=dict(
            claim_code='n5ry-p6x6-kth7-7hc4', printer_name='lp'))

        # valid code: redirect to overview.
        self.assertRedirects(r, '/')
