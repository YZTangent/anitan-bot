class Otp:
    def __init__(self, email, otp, expires_at):
        self.otp = otp
        self.email = email
        self.expires_at = expires_at


otp_cache = {}
authenticated_users_cache = set()
