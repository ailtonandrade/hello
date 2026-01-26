"""Compatibility facade for authentication and DB helpers.

This module preserves the historical `auth` API while delegating
implementation to the `repository` package (clean separation of DB logic).
Callers may continue to `import auth`.
"""

from repository import db as db_repo
from repository import users as users_repo
from repository import templates as templates_repo
from repository import history as history_repo

# ensure DB is initialized
init_db = db_repo.init_db
get_conn = db_repo.get_conn

# Users / auth
create_jwt = users_repo.create_jwt
verify_jwt = users_repo.verify_jwt
create_user = users_repo.create_user
authenticate_user = users_repo.authenticate_user
get_user = users_repo.get_user
add_credits = users_repo.add_credits
consume_credits = users_repo.consume_credits
get_credits = users_repo.get_credits
create_password_reset_for_email = users_repo.create_password_reset_for_email
verify_and_consume_password_reset = users_repo.verify_and_consume_password_reset
set_password = users_repo.set_password
# Billing / payments
get_credit_packages = users_repo.get_credit_packages
get_credit_package = users_repo.get_credit_package
create_payment = users_repo.create_payment
update_payment_status_by_session = users_repo.update_payment_status_by_session
get_payments_for_user = users_repo.get_payments_for_user

# Templates
create_template = templates_repo.create_template
get_templates_for_user = templates_repo.get_templates_for_user
get_template = templates_repo.get_template
update_template = templates_repo.update_template
update_template_admin = templates_repo.update_template_admin
delete_template = templates_repo.delete_template
delete_template_admin = templates_repo.delete_template_admin

# History
update_history_file = history_repo.update_history_file
get_history_for_user = history_repo.get_history_for_user
log_history = history_repo.log_history

__all__ = [
    'init_db','get_conn',
    'create_jwt','verify_jwt','create_user','authenticate_user','get_user',
    'add_credits','consume_credits','get_credits','create_password_reset_for_email',
    'verify_and_consume_password_reset','set_password',
    'create_template','get_templates_for_user','get_template','update_template','update_template_admin',
    'delete_template','delete_template_admin',
    'get_credit_packages','get_credit_package','create_payment','update_payment_status_by_session','get_payments_for_user',
    'update_history_file','get_history_for_user','log_history'
]