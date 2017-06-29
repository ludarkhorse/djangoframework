from __future__ import unicode_literals

from datetime import datetime

from django.utils import six, timezone
from django.test import TestCase
from mock import patch
from rest_framework_simplejwt.utils import (
    aware_utcnow, datetime_from_timestamp, datetime_to_epoch, format_lazy,
    make_utc
)


class TestMakeUtc(TestCase):
    def test_it_should_return_the_correct_values(self):
        # It should make a naive datetime into an aware, utc datetime if django
        # is configured to use timezones and the datetime doesn't already have
        # a timezone

        # Naive datetime
        dt = datetime(year=1970, month=12, day=1)

        with self.settings(USE_TZ=False):
            self.assertEqual(dt, make_utc(dt))

        with self.settings(USE_TZ=True):
            self.assertNotEqual(dt, make_utc(dt))
            self.assertEqual(timezone.make_aware(dt, timezone=timezone.utc), make_utc(dt))

            dt = timezone.now()
            self.assertEqual(dt, make_utc(dt))


class TestAwareUtcnow(TestCase):
    def test_it_should_return_the_correct_value(self):
        now = datetime.utcnow()

        with patch('rest_framework_simplejwt.utils.datetime') as fake_datetime:
            fake_datetime.utcnow.return_value = now

            # Should return aware utcnow if USE_TZ == True
            with self.settings(USE_TZ=True):
                self.assertEqual(timezone.make_aware(now, timezone=timezone.utc), aware_utcnow())

            # Should return naive utcnow if USE_TZ == False
            with self.settings(USE_TZ=False):
                self.assertEqual(now, aware_utcnow())


class TestDatetimeToEpoch(TestCase):
    def test_it_should_return_the_correct_values(self):
        self.assertEqual(datetime_to_epoch(datetime(year=1970, month=1, day=1)), 0)
        self.assertEqual(datetime_to_epoch(datetime(year=1970, month=1, day=1, second=1)), 1)
        self.assertEqual(datetime_to_epoch(datetime(year=2000, month=1, day=1)), 946684800)


class TestDatetimeFromEpoch(TestCase):
    def test_it_should_return_the_correct_values(self):
        with self.settings(USE_TZ=False):
            self.assertEqual(datetime_from_timestamp(0), datetime(year=1970, month=1, day=1))
            self.assertEqual(datetime_from_timestamp(1), datetime(year=1970, month=1, day=1, second=1))
            self.assertEqual(datetime_from_timestamp(946684800), datetime(year=2000, month=1, day=1), 946684800)

        with self.settings(USE_TZ=True):
            self.assertEqual(datetime_from_timestamp(0), make_utc(datetime(year=1970, month=1, day=1)))
            self.assertEqual(datetime_from_timestamp(1), make_utc(datetime(year=1970, month=1, day=1, second=1)))
            self.assertEqual(datetime_from_timestamp(946684800), make_utc(datetime(year=2000, month=1, day=1)))


class TestFormatLazy(TestCase):
    def test_it_should_work(self):
        obj = format_lazy('{} {}', 'arst', 'zxcv')

        self.assertNotIsInstance(obj, str)
        self.assertEqual(six.text_type(obj), 'arst zxcv')
