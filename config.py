import os

FROM_EMAIL = os.environ.get("FROM_EMAIL", "monit.qualidade@outlook.com")
EMAIL_PASSWORD = 'gYIh!CWZ3LOu'

# EMAIL_PASSWORD =	os.environ.get("EMAIL_PASSWORD")
TO_EMAIL = os.environ.get("TO_EMAIL", "danilo.medeiros@elumini.com.br")

