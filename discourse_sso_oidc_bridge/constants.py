# UPDATED 3 Jul 2021 with values from:
# https://github.com/discourse/discourse/blob/master/lib/single_sign_on.rb

ALL_ATTRIBUTES = {
    "add_groups",
    "admin",
    "avatar_force_update",
    "avatar_url",
    "bio",
    "card_background_url",
    "email",
    "external_id",
    "groups",
    "locale",
    "locale_force_update",
    "logout",
    "moderator",
    "name",
    "nonce",
    "profile_background_url",
    "remove_groups",
    "require_activation",
    "return_sso_url",
    "suppress_welcome_message",
    "title",
    "username",
    "website",
    "location",
}

BOOL_ATTRIBUTES = {
    "admin",
    "avatar_force_update",
    "locale_force_update",
    "logout",
    "moderator",
    "require_activation",
    "suppress_welcome_message",
}

REQUIRED_ATTRIBUTES = {
    "email",
    "external_id",
}
