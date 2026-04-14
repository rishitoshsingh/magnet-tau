from .get_user_ids import GetUserIds
from .calculate import Calculate
from .get_customer_details import GetCustomerDetails
from .get_customers_with_senior_plan import GetCustomersWithSeniorPlan
from .get_customers_with_outstanding_balance import GetCustomersWithOutstandingBalance
from .get_customers_with_open_tickets import GetCustomersWithOpenTickets
from .get_customers_by_service import GetCustomersByService
from .get_customers_with_devices import GetCustomersWithDevices

from tracer2.envs.telecom.tools.add_device import AddDevice
from tracer2.envs.telecom.tools.create_support_ticket import CreateSupportTicket
from tracer2.envs.telecom.tools.find_customer_by_email import FindCustomerByEmail
from tracer2.envs.telecom.tools.find_customer_by_phone import FindCustomerByPhone
from tracer2.envs.telecom.tools.get_billing_details import GetBillingDetails
from tracer2.envs.telecom.tools.get_device_details import GetDeviceDetails
from tracer2.envs.telecom.tools.get_senior_discount import GetSeniorDiscount
from tracer2.envs.telecom.tools.get_service_details import GetServiceDetails
from tracer2.envs.telecom.tools.get_services import GetServices
from tracer2.envs.telecom.tools.get_support_ticket_details import GetSupportTicketDetails
from tracer2.envs.telecom.tools.manage_billing import ManageBilling
from tracer2.envs.telecom.tools.manage_service import ManageService
from tracer2.envs.telecom.tools.modify_support_ticket import ModifySupportTicket
from tracer2.envs.telecom.tools.record_payment import RecordPayment
from tracer2.envs.telecom.tools.think import Think
from tracer2.envs.telecom.tools.troubleshoot_device import TroubleshootDevice

ALL_TOOLS = [
    # Reverse tools (read-only, for task grounding)
    GetUserIds,
    GetCustomersWithSeniorPlan,
    GetCustomersWithOutstandingBalance,
    GetCustomersWithOpenTickets,
    GetCustomersByService,
    GetCustomersWithDevices,
    # Forward tools (used by the agent to solve tasks)
    AddDevice,
    Calculate,
    CreateSupportTicket,
    FindCustomerByEmail,
    FindCustomerByPhone,
    GetBillingDetails,
    GetCustomerDetails,
    GetDeviceDetails,
    GetSeniorDiscount,
    GetServiceDetails,
    GetServices,
    GetSupportTicketDetails,
    ManageBilling,
    ManageService,
    ModifySupportTicket,
    RecordPayment,
    Think,
    TroubleshootDevice,
]
