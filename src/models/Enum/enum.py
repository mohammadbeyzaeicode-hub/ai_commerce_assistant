from enum import Enum

class SenderType(Enum):
    USER = "user"
    BOT = "bot"
    HUMAN = "human"
    SYSTEM = "system"

# Print the enum members
for member in SenderType:
    print(f"{member.name} = {member.value}")
    
#
class ChatState(str, Enum):
    BOT_ACTIVE = "BOT_ACTIVE"
    WAITING_FOR_HUMAN = "WAITING_FOR_HUMAN"
    HUMAN_ACTIVE = "HUMAN_ACTIVE"
    
# class UIAction(Enum):
#     NONE = "none"
#     SHOW_SUPPORT_DONE = "show_support_done"
#     RESTORE_MAIN_MENU = "restore_main_menu"    
#forfutureclass 
# UIAction(Enum):
#     NONE = "none"
#     SET_MODE = "set_mode"
#     RESET_MODE = "reset_mode"    
    
# class UIMode(Enum):
#     DEFAULT = "default"
#     SUPPORT_CHAT = "support_chat"
#     ORDER_FLOW = "order_flow"
#     ADMIN_REVIEW = "admin_review"    