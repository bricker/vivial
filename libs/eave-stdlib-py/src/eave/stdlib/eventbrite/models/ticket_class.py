from enum import StrEnum
from typing import TypedDict

from .shared import CurrencyCost


class PointOfSale(StrEnum):
    ONLINE = "online"
    AT_THE_DOOR = "at_the_door"


class DeliveryMethod(StrEnum):
    ELECTRONIC = "electronic"
    """Tickets are attached to the confirmation email."""

    WILL_CALL = "will_call"
    """Tickets are delivered by an alternative method."""

    STANDARD_SHIPPING = "standard_shipping"
    """Tickets are mailed to the shipping address by Eventbrite."""

    THIRD_PARTY_SHIPPING = "third_party_shipping"
    """Tickets are mailed to the shipping address by a third party company."""


class SalesChannel(StrEnum):
    ONLINE = "online"

    ATD = "atd"


class OnSaleStatus(StrEnum):
    """
    The status of the ticket class. These can change based on on/off sale dates, ticket class state, or current inventory.
    """

    UNKNOWN = "UNKNOWN"
    """The current on sale state of this ticket class is not known."""

    NOT_YET_ON_SALE = "NOT_YET_ON_SALE"
    """Sales have not yet started for this ticket class. The on sale date is in the future."""

    AVAILABLE = "AVAILABLE"
    """Tickets are currently on sale and still have available inventory."""

    HIDDEN = "HIDDEN"
    """The ticket class is marked as hidden currently and is not visible to customers."""

    SOLD_OUT = "SOLD_OUT"
    """There is no available inventory for this ticket class."""

    UNAVAILABLE = "UNAVAILABLE"
    """The ticket class is not available for sale currently."""


class VariantInputType(StrEnum):
    """
    Type of variants for this ticket.
    A ticket may have more than one variant.
    Those multiple variants may be offered to purchaser as a flat list (multiple) or a dropdown choice (single).
    """

    ONE = "one"
    """This ticket has only one variant. Thus, quantity selection of multiple variants is not applicable."""

    MULTIPLE = "multiple"
    """
    A primary variant for "multiple" variants is a "Full Price" base ticket.
    "multiple" variants are typically displayed as a flat list with a quantity selection for each variant.
    """

    SINGLE = "single"
    """
    'Single' variants are typically displayed as a dropdown choice with a single quantity selection.
    A primary variant for 'single' variants is a 'Best Available' option across all variants for this ticket.
    """


class TicketClassCategory(StrEnum):
    ADMISSION = "admission"
    """ticket variant counts against event capacity."""

    ADD_ON = "add_on"
    """ticket variant does not count against event capacity."""

    DONATION = "donation"
    """ticket variant is marked as donation, requiring currency input."""


class TicketClassCostBreakdown(TypedDict, total=False):
    """Cost of the ticket"""

    actual_cost: CurrencyCost | None
    """The total cost for this ticket class less the fee"""

    actual_fee: CurrencyCost | None
    """The fee for this ticket class"""

    cost: CurrencyCost | None
    """The display cost for the ticket"""

    fee: CurrencyCost | None
    """The fee that should be included in the price (0 if include_fee is false)."""

    tax: CurrencyCost | None
    """The ticket's base or discounted tax amount"""


class Variant(TypedDict, total=False):
    id: str
    """ID of this ticket variant."""

    category: TicketClassCategory
    """Ticket category to which a ticket variant belongs."""

    primary: bool | None
    """
    If this value is true, this ticket variant is the primary default variant of the ticket.
    For public discounts, primary variant is the main "Full Price" ticket without discounts applied.
    For reserved seating tiered inventory ticket, primary variant is the "Best Available" option.
    """

    code: str | None
    """Discount code or public discount name if discounted."""

    name: str | None
    """
    Name of this ticket variant.
    For a primary default variant like "Best Available" or "Full Price", name is not returned.
    """

    display_name: str
    """
    Pretty long name of this ticket variant.
    For tiered inventory tickets, this includes the tier name.
    For public discount, this includes ticket class name and discount name.
    """

    description: str | None
    """Long description of this ticket variant if defined."""

    free: bool
    """whether this ticket variant is free. for donation ticket variant, this value is false."""

    cost: CurrencyCost | None
    """The display cost for the variant"""

    total_cost: CurrencyCost | None
    """The total cost for the variant including fee and tax"""

    fee: CurrencyCost | None
    """The fee that should be included in the price."""

    tax: CurrencyCost | None
    """The variant's base or discounted tax amount."""

    tax_and_fee: CurrencyCost | None
    """fee plus tax."""

    original_cost: CurrencyCost | None
    """The original cost before discount is applied if this variant is discounted."""

    original_total_cost: CurrencyCost | None
    """The original total cost before discount is applied if this variant is discounted."""

    original_fee: CurrencyCost | None
    """The original fee before discount is applied if this variant is discounted."""

    original_tax: CurrencyCost | None
    """The original tax before discount is applied if this variant is discounted."""

    display_shipping_fee: CurrencyCost | None
    """not documented"""

    on_sale_status: OnSaleStatus
    """The status of the ticket variant. These can change based on on/off sale dates, ticket variant state, or current inventory."""

    amount_off: CurrencyCost | None
    """The discounted amount if this variant is discounted."""

    percent_off: str | None
    """Percentage of discount if this variant is discounted and if discount is defined as a percentage discount."""

    color: str | None
    """Hex representation of tier color if a color is defined for this ticket variant."""

    image_id: str | None
    """Image ID for this ticket varint if image is set."""

    currency: str | None
    """not documented"""

    checkout_group_id: str | None
    """not documented"""

    hide_sale_dates: bool | None
    """not documented"""

    include_fee: bool | None
    """not documented"""

    use_all_in_price: bool | None
    """not documented"""

    # None of the following are documented and it's unclear what they are for

    # payment_constraints: list[object] | None
    # ticket_options_range: list[object] | None
    # shipping_components: list[object] | None
    # fee_components: list[object] | None
    #     {
    #         "name": "eventbrite.service_fee",
    #         "payer": "attendee",
    #         "title": "Eventbrite Service Fee",
    #         "bucket": "fee",
    #         "value": {
    #             "currency": "USD",
    #             "major_value": "2.35",
    #             "value": 235,
    #             "display": "2.35 USD"
    #         },
    #         "group_name": "eventbrite.service_fee",
    #         "base": "item.net-includable",
    #         "rule": {
    #             "fee": {
    #                 "name": "eventbrite.service_fee",
    #                 "payer": "attendee",
    #                 "title": "Eventbrite Service Fee",
    #                 "bucket": "fee",
    #                 "base": "item.net-includable",
    #                 "recipient": "eventbrite"
    #             },
    #             "min": 0,
    #             "max": 4294967295,
    #             "percent": 370,
    #             "fixed": 179,
    #             "id": "1289279"
    #         },
    #         "internal_name": "eventbrite.service_fee",
    #         "intermediate": false,
    #         "recipient": "eventbrite"
    #     },
    #     {
    #         "name": "eventbrite.payment_fee_v2",
    #         "payer": "attendee",
    #         "title": "Payment Fee",
    #         "bucket": "fee",
    #         "value": {
    #             "currency": "USD",
    #             "major_value": "0.50",
    #             "value": 50,
    #             "display": "0.50 USD"
    #         },
    #         "group_name": "eventbrite.payment_fee_v2",
    #         "base": "item.display_royalty_esf",
    #         "rule": {
    #             "fee": {
    #                 "name": "eventbrite.payment_fee_v2",
    #                 "payer": "attendee",
    #                 "title": "Payment Fee",
    #                 "bucket": "fee",
    #                 "base": "item.display_royalty_esf",
    #                 "recipient": "eventbrite"
    #             },
    #             "min": 0,
    #             "max": 4294967295,
    #             "percent": 290,
    #             "fixed": 0,
    #             "id": "1289309"
    #         },
    #         "internal_name": "eventbrite.payment_fee_v2",
    #         "intermediate": false,
    #         "recipient": "eventbrite"
    #     }
    # ],

    # tax_components: list[object] | None


class TicketClass(TypedDict, total=False):
    """https://www.eventbrite.com/platform/api#/reference/ticket-class"""

    # Expansions: event, image

    id: str
    """nodoc"""

    resource_uri: str
    """nodoc"""

    description: str | None
    """Description of the ticket"""

    donation: bool | None
    """Is this a donation? (user-supplied cost)"""

    free: bool | None
    """Is this a free ticket?"""

    minimum_quantity: int | None
    """Minimum number per order"""

    maximum_quantity: int | None
    """Maximum number per order (blank uses default value)"""

    delivery_methods: list[DeliveryMethod] | None
    """A list of the available delivery methods for this ticket class"""

    cost: CurrencyCost | None
    """
    Cost of the ticket (currently currency must match event currency) e.g. $45 would be 'USD,4500'
    NOTE: This type is incorrectly documented in the API documentation. It's documented as a `TicketClassCostBreakdown` but the actual response is a `Price`.
    """

    fee: CurrencyCost | None
    """not documented"""

    tax: CurrencyCost | None
    """not documented"""

    image_id: str | None
    """Image ID for this ticket class. null if no image is set."""

    name: str | None
    """Name of this ticket class."""

    display_name: str | None
    """Pretty long name of this ticket class. For tiered inventory tickets, this includes the tier name."""

    sorting: int | None
    """
    Sorting determines the order in which ticket classes are listed during purchase flow on the event listing page.
    Always populated when requested by a user with proper permissions.
    Defaults to 0 if not supplied on creation.
    Values are listed in ascending order; if ticket classes have the same sorting value, they are sorted by creation date.
    """

    # PRIVATE FIELD
    # capacity: int | None
    """
    Total capacity of this ticket.
    For donation ticket, null means unlimited.
    For tiered inventory ticket, null means capacity is only limited by tier capacity and/or event capacity.
    """

    # PRIVATE FIELD
    # quantity_total: int | None
    """
    Total available number of this ticket, limited by the the smallest of event capacity, inventory tier capacity, and ticket capacity.
    For donation ticket, 0 means unlimited.
    """

    # PRIVATE FIELD
    # quantity_sold: int | None
    """The number of sold tickets."""

    sales_start: str | None
    """When the ticket is available for sale (leave empty for 'when event published')"""

    sales_end: str | None
    """When the ticket stops being on sale (leave empty for 'one hour before event start')"""

    # PRIVATE FIELD
    # hidden: bool | None
    """Hide this ticket"""

    include_fee: bool | None
    """Absorb the fee into the displayed cost"""

    # PRIVATE FIELD
    # split_fee: bool | None
    """Absorb the payment fee, but show the eventbrite fee"""

    secondary_assignment_enabled: bool
    """Has secondary barcode assignment enabled (for ex/ RFID)"""

    inventory_tier_id: str | None
    """Optional ID of Inventory Tier with which to associate the ticket class"""

    sales_channels: list[SalesChannel] | None
    """A list of all supported sales channels"""

    maximum_quantity_per_order: int | None
    """not documented"""

    maximum_quantity_per_order_without_pending: int | None
    """not documented"""

    on_sale_status: OnSaleStatus
    """The status of the ticket class. These can change based on on/off sale dates, ticket class state, or current inventory."""

    has_pdf_ticket: bool | None
    """not documented"""

    category: TicketClassCategory | None
    """not documented"""

    event_id: str | None
    """not documented"""

    variant_id: str | None
    """not documented"""

    variant_input_type: VariantInputType
    """
    Type of variants for this ticket.
    A ticket may have more than one variant.
    Those multiple variants may be offered to purchaser as a flat list (multiple) or a dropdown choice (single).
    """

    variants: list[Variant] | None
    """A list of ticket variants for sale."""
