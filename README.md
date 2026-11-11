# MLM Network Manager

A small Flask + SQLite starter app for managing a member/referral network. It lets you add members, assign an optional sponsor, view the organization tree, and remove members. This is a demo scaffold: it does not calculate commissions, process payments, or provide legal/compliance advice.

## Run locally

Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000>.

The SQLite database is created as `mlm_project.db` in the project directory on first run. Set `DATABASE_PATH` to use another location and set a strong `SECRET_KEY` before deploying. For local development, the app uses a development-only fallback secret. Do not deploy the built-in Flask development server; use a production WSGI server and add authentication, authorization, CSRF protection, backups, and appropriate privacy/security controls before using real member data.

## Features

- Add a member with an optional sponsor
- Prevent duplicate email addresses
- View a nested referral tree and member list
- Remove a member (their direct referrals become top-level members)

## Disclaimer

This project is for educational/demo use. Verify all applicable laws and regulations before operating any real-world referral or compensation program.
