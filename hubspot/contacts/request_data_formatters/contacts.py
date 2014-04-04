##############################################################################
#
# Copyright (c) 2014, 2degrees Limited.
# All Rights Reserved.
#
# This file is part of hubspot-contacts
# <https://github.com/2degrees/hubspot-contacts>, which is subject to the
# provisions of the BSD at
# <http://dev.2degreesnetwork.com/p/2degrees-license.html>. A copy of the
# license should accompany this distribution. THIS SOFTWARE IS PROVIDED "AS IS"
# AND ANY AND ALL EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST
# INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################

from collections import defaultdict
from decimal import Decimal
from decimal import InvalidOperation
from json import dumps as json_serialize

from hubspot.contacts.exc import HubspotPropertyValueError
from hubspot.contacts.generic_utils import \
    convert_date_to_timestamp_in_milliseconds
from hubspot.contacts.properties import BooleanProperty
from hubspot.contacts.properties import DatetimeProperty
from hubspot.contacts.properties import NumberProperty


def format_contacts_data_for_saving(contacts, property_type_by_property_name):
    contacts_data = []
    for contact in contacts:
        contact_data = _format_contact_data_for_saving(
            contact,
            property_type_by_property_name,
            )
        contacts_data.append(contact_data)
    return contacts_data


def _format_contact_data_for_saving(contact, property_type_by_property_name):
    properties_data = _format_contact_properties_for_saving(
        contact.properties,
        property_type_by_property_name,
        )
    contact_data = {
        'email': contact.email_address,
        'properties': properties_data,
        }
    return contact_data


def _format_contact_properties_for_saving(
    contact_properties,
    property_type_by_property_name,
    ):
    contact_properties_data = []
    for property_name, property_value in contact_properties.items():
        property_type = property_type_by_property_name[property_name]
        property_value_cast = \
            _serialize_property_value(property_value, property_type)
        property_data = \
            {'property': property_name, 'value': property_value_cast}
        contact_properties_data.append(property_data)
    return contact_properties_data


def _serialize_property_value(property_value, property_type):
    converter = _PROPERTY_VALUE_CONVERTER_BY_PROPERTY_TYPE[property_type]
    property_value_cast = converter(property_value)
    property_value_serialized = unicode(property_value_cast)
    return property_value_serialized


def _json_serialize_to_boolean(value):
    value_boolean = bool(value)
    value_serialized = json_serialize(value_boolean)
    return value_serialized


def _convert_to_number(value):
    try:
        number = Decimal(value)
    except InvalidOperation:
        raise HubspotPropertyValueError('{!r} is not a number'.format(value))
    return number


_identity = lambda x: x


_PROPERTY_VALUE_CONVERTER_BY_PROPERTY_TYPE = defaultdict(
    lambda: _identity,
    {
        BooleanProperty: _json_serialize_to_boolean,
        DatetimeProperty: convert_date_to_timestamp_in_milliseconds,
        NumberProperty: _convert_to_number,
        },
    )