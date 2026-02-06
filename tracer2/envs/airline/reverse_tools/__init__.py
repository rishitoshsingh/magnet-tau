# Copyright Sierra

from .get_all_user_ids import GetAllUserIds
from .get_cancelled_flights import GetCancelledFlights
from .get_delayed_flights import GetDelayedFlights
from .get_earliest_flight_date import GetEarliestFlightDate
from .get_flight_details import GetFlightDetails
from .get_latest_bookable_flight_date import GetLatestBookableFlightDate
from .get_reservation_details import GetReservationDetails
from .get_reservation_ids_for_flight import GetReservationIdsForFlight
from .get_todays_date import GetTodaysDate
from .get_user_details import GetUserDetails
from .get_user_ids_with_n_reservations import GetUserIdsWithNReservations
from .update_reservation_passengers import UpdateReservationPassengers
from .update_reservation_flights import UpdateReservationFlights
from .update_reservation_baggages import UpdateReservationBaggages
from .cancel_reservation import CancelReservation
from .book_reservation import BookReservation
from .calculate import Calculate
from .think import Think

ALL_TOOLS = [
    # GetAllUserIds,
    GetCancelledFlights,
    GetDelayedFlights,
    GetFlightDetails,
    GetReservationDetails,
    GetReservationIdsForFlight,
    GetUserDetails,
    GetEarliestFlightDate,
    GetLatestBookableFlightDate,
    GetTodaysDate,
    GetUserIdsWithNReservations,
    # UpdateReservationPassengers,
    # UpdateReservationFlights,
    # UpdateReservationBaggages,
    # CancelReservation,
    # BookReservation,
    Calculate,
    Think,
]
