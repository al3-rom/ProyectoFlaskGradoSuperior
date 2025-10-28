# wannapop/helper_role.py
from flask import current_app
from flask_login import current_user
from flask_principal import (
    identity_loaded, identity_changed,
    ActionNeed, RoleNeed, Permission,
    Identity, AnonymousIdentity
)
from enum import Enum

class RoleName(str, Enum):
    wanner = "wanner"
    moderator = "moderator"
    admin = "admin"

class Action(str, Enum):
    view = "Ver, crear, actualizar y eliminar productos."
    edit = "Ver, actualizar y eleminar usuarios."
    manage = "All permisions"

class HelperRole:

    view_action_need = ActionNeed(Action.view)
    edit_action_need = ActionNeed(Action.edit)
    manage_action_need = ActionNeed(Action.manage)

    view_permission = Permission(view_action_need)
    edit_permission = Permission(edit_action_need)
    manage_permission = Permission(manage_action_need)

    wanner_role_need = RoleNeed(RoleName.wanner.value)
    moderator_role_need = RoleNeed(RoleName.moderator.value)
    admin_role_need = RoleNeed(RoleName.admin.value)

    wanner_role_permission = Permission(wanner_role_need)
    moderator_role_permission = Permission(moderator_role_need)
    admin_role_permission = Permission(admin_role_need)

    @staticmethod
    def notify_identity_changed():
      
        if getattr(current_user, "is_authenticated", False):
            ident = Identity(getattr(current_user, "id", getattr(current_user, "email", "anon")))
        else:
            ident = AnonymousIdentity()
        identity_changed.send(current_app._get_current_object(), identity=ident)


@identity_loaded.connect
def on_identity_loaded(sender, identity):
    identity.user = current_user

    role_name = getattr(getattr(current_user, "role", None), "name", None)
    role_name = (role_name or "").lower()


    role_name = (str(role_name).lower() if role_name else None)

    if role_name == RoleName.wanner.value:         
        identity.provides.add(HelperRole.wanner_role_need)
        identity.provides.add(HelperRole.view_action_need)

    elif role_name == RoleName.moderator.value:    
        identity.provides.add(HelperRole.moderator_role_need)
        identity.provides.add(HelperRole.wanner_role_need)      
        identity.provides.add(HelperRole.view_action_need)
        identity.provides.add(HelperRole.edit_action_need)

    elif role_name == RoleName.admin.value:       
        identity.provides.add(HelperRole.admin_role_need)
        identity.provides.add(HelperRole.moderator_role_need)    
        identity.provides.add(HelperRole.wanner_role_need)       
        identity.provides.add(HelperRole.view_action_need)
        identity.provides.add(HelperRole.edit_action_need)
        identity.provides.add(HelperRole.manage_action_need)
