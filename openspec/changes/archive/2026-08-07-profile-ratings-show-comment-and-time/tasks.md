## 1. Update Profile Ratings Template

- [x] 1.1 In `templates/accounts/_profile_ratings.html`, change the date filter from `{{ submission.created_at|date:"d M Y" }}` to `{{ submission.created_at|date:"d M Y, H:i" }}`
- [x] 1.2 In `templates/accounts/_profile_ratings.html`, add a comment block inside each `.rank-entry` div, after the dish/venue name block: render `{{ submission.comment|truncatewords:100 }}` wrapped in `{% if submission.comment %}...{% endif %}`
