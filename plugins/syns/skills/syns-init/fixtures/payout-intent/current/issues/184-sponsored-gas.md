# Issue 184: sponsored gas can redirect value

Current implementation assigns `recipientOverride` to the sponsor for sponsored calls. Product review is required because sponsorship should not change beneficial ownership.
