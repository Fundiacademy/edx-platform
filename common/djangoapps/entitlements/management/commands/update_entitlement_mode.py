"""
Management command for updating entitlements modes.
"""


import logging
from textwrap import dedent

from django.core.management import BaseCommand

from entitlements.models import CourseEntitlement

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class Command(BaseCommand):
    """
    Management command for updating entitlements mode.

    Example usage:

    # Change entitlement_mode for given user_id with order_number to new_mode:
    $ ./manage.py lms --settings=devstack_docker update_entitlement_mode \
    ORDER_NUMBER_123,ORDER_NUMBER_456 course_uuid verified
    """
    help = dedent(__doc__).strip()

    def add_arguments(self, parser):
        parser.add_argument(
            'order_numbers',
            help='Order number of entitlement'
        )

        parser.add_argument(
            'course_uuid',
            help='UUID of course'
        )

        parser.add_argument(
            'entitlement_mode',
            help='Entitlement mode to change to.'
        )

    def handle(self, *args, **options):
        logger.info('Updating entitlement_mode for provided Entitlements.')

        order_numbers = options['order_numbers']
        course_uuid = options['course_uuid']
        entitlement_mode = options['entitlement_mode']

        for order_number in order_numbers.split(','):
            entitlement_to_update = CourseEntitlement.objects.get(
                course_uuid=course_uuid,
                order_number=order_number,
            )
            entitlement_to_update.mode = entitlement_mode
            entitlement_to_update.save()
            logger.info('entitlement_mode updated to {} for '
                        'order_number {} for course with UUID {}'.format(entitlement_mode, order_number, course_uuid))

        logger.info('Successfully updated entitlement_mode for Entitlements.')
