from collections.abc import Iterable
from django.conf import settings
from github import Github
from github.PaginatedList import PaginatedList
from search.models import Language
from typing import Union
import yaml


class GitHub(Github):
    def __init__(self):
        super().__init__(settings.GITHUB_API_TOKEN)

    @property
    def known_languages(self):
        if not Language.objects.exists():
            languages = self.get_known_languages()
            for language in languages:
                Language.objects.create(
                    name=language.name,
                    file_extensions=language.extensions
                )
        return [language.name for language in Language.objects.all()]

    @known_languages.setter
    def known_languages(self, value):
        raise ValueError("known_languages cannot be set")

    @known_languages.deleter
    def known_languages(self):
        raise ValueError("known_languages cannot be deleted")

    @staticmethod
    def reset_known_languages():
        languages = Language.objects.all()
        if languages.exists():
            for language in languages:
                language.delete()

    def get_known_languages(self):
        user = self.get_user('github')
        repo = user.get_repo('linguist')
        file = repo.get_contents('lib/linguist/languages.yml')
        content = file.decoded_content.decode('utf-8')
        content = "\n".join([x for x in content.split('\n') if not x.startswith('#')])
        languages_dict = yaml.load(content, Loader=yaml.SafeLoader)
        return languages_dict

    # TODO: Implement search in github
    def search_in_topics(self, topics: Iterable) -> PaginatedList:
        query = " ".join([f'topic:{topic}' for topic in topics])
        return self.search_repositories(query)

    def search_in_readme_and_description(self, keywords: Iterable) -> PaginatedList:
        query = '+'.join(keywords) + '+in:readme+in:description'
        return self.search_repositories(query, sort='stars', order='desc')

    def search_users_by_language(self, language: Union[Language, str]) -> PaginatedList:
        if isinstance(language, Language):
            language = language.name
        elif not isinstance(language, str):
            raise ValueError('language has to be a string or a search.models.Language instance')
        query = 'language:' + language
        return self.search_users(query)
