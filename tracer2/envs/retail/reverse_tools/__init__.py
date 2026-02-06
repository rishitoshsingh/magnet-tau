# Copyright Sierra

from .generate_new_address import GenerateNewAddress
from .get_all_delivered_order_ids import GetAllDeliveredOrderIds
from .get_all_pending_order_ids import GetAllPendingOrderIds
from .get_all_user_ids import GetAllUserIds
from .get_order_details import GetOrderDetails
from .get_product_variants import GetProductVariants
from .get_user_details import GetUserDetails
from .list_all_product_types import ListAllProductTypes


ALL_TOOLS = [
    GenerateNewAddress,
    GetAllDeliveredOrderIds,
    GetAllPendingOrderIds,
    GetAllUserIds,
    GetOrderDetails,
    GetProductVariants,
    GetUserDetails,
    ListAllProductTypes
]
