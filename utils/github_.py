from github import Github
from django.conf import settings


class GitHub(Github):
    def __init__(self):
        super().__init__(settings.GITHUB_API_TOKEN)

    # TODO: Implement search in github
