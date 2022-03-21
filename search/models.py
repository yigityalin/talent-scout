from collections import Counter
from collections.abc import Iterable
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from django.utils import text
from github import Github
from github.GithubException import UnknownObjectException
from github.NamedUser import NamedUser
from typing import Union

from github.Repository import Repository

from .utils.pagination import CombinedPaginatedList
import yaml


class Language(models.Model):
    name = models.CharField(max_length=64, unique=True, null=False, blank=False)
    file_extensions = ArrayField(base_field=models.CharField(max_length=16), null=True, blank=True)

    def __str__(self):
        return self.name


class Profession(models.Model):
    DELIMITER = ","

    name = models.CharField(max_length=64)
    skills = models.TextField()

    def __str__(self):
        return self.name

    @property
    def skills_list(self):
        return [skill.strip().lower() for skill in self.skills.split(self.DELIMITER)]


class GitHubUser(models.Model):
    DELIMITER = ","

    login = models.CharField(max_length=39, unique=True, null=False, blank=False)
    bio = models.CharField(max_length=160, null=True, blank=True)
    blog = models.CharField(max_length=255, null=True, blank=True)
    company = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    hireable = models.BooleanField()
    html_url = models.URLField(null=True, blank=True)
    location = models.CharField(max_length=64, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    public_repos = models.IntegerField()
    languages = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'GitHubUser(login={str(self.login)})'

    @property
    def languages_list(self):
        return [language.strip().capitalize()
                for language in self.languages.split(self.DELIMITER)]

    def get_absolute_url(self):
        return reverse('search:user', kwargs=dict(login=self.login))

    @staticmethod
    def create_languages_str_from_list(languages):
        return ", ".join(languages)

    @staticmethod
    def save_named_user(named_user: NamedUser, languages: list):
        user, _ = GitHubUser.objects.update_or_create(
            login=named_user.login,
            defaults=dict(
                bio=named_user.bio,
                blog=named_user.blog,
                company=named_user.company,
                email=named_user.email,
                hireable=named_user.hireable,
                html_url=named_user.html_url,
                location=named_user.location,
                name=named_user.name,
                public_repos=named_user.public_repos,
                languages=GitHubUser.create_languages_str_from_list(languages)
            )
        )
        return user

    class Meta:
        verbose_name = "GitHub User"
        verbose_name_plural = "GitHub Users"


class GitHubRepository(models.Model):
    owner = models.ForeignKey(GitHubUser, on_delete=models.RESTRICT)
    name = models.CharField(max_length=100, null=False, blank=False)
    created_at = models.DateTimeField()
    description = models.TextField(null=True, blank=True)
    forks_count = models.IntegerField()
    languages = ArrayField(base_field=models.CharField(max_length=32))
    license = models.CharField(max_length=48, null=True, blank=True)

    def __str__(self):
        return f'GitHubRepository(owner={str(self.owner)}, name={str(self.name)})'

    @staticmethod
    def save_repository(repository: Repository, owner: GitHubUser):
        languages = repository.get_languages()
        languages = sorted(languages.keys(), key=languages.get, reverse=True)
        try:
            license_ = repository.get_license().license.name
        except UnknownObjectException:
            license_ = None
        repository, _ = GitHubRepository.objects.update_or_create(
            owner=owner, name=repository.name,
            defaults=dict(
                created_at=repository.created_at,
                description=repository.description,
                forks_count=repository.forks_count,
                languages=languages,
                license=license_
            )
        )
        return repository

    class Meta:
        verbose_name = "GitHub Repository"
        verbose_name_plural = "GitHub Repositories"


class Search(models.Model, Github):
    class SearchCriteria(models.TextChoices):
        USERNAME = 'NAME'
        LOCATION = 'LOC'
        LANGUAGE = 'LANG'
        PROFESSION = 'PROF'

    query = models.CharField(max_length=256, blank=False, null=False)
    by = models.CharField(choices=SearchCriteria.choices, max_length=4,
                          default=SearchCriteria.PROFESSION)

    def __init__(self, *args, **kwargs):
        models.Model.__init__(self, *args, **kwargs)
        Github.__init__(self, settings.GITHUB_API_TOKEN)

    @property
    def known_languages(self):
        if not Language.objects.exists():
            languages = self.get_known_languages()
            for language, extensions in languages.items():
                Language.objects.update_or_create(
                    name=language,
                    file_extensions=extensions
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

    def update_known_languages(self):
        languages = self.get_known_languages()
        for language, extensions in languages.items():
            Language.objects.update_or_create(
                name=language,
                defaults=dict(file_extensions=extensions)
            )

    def get_known_languages(self):
        user = self.get_user('github')
        repo = user.get_repo('linguist')
        file = repo.get_contents('lib/linguist/languages.yml')
        content = file.decoded_content.decode('utf-8')
        languages_dict = yaml.load(content, Loader=yaml.SafeLoader)
        return {
            language: attrs.get('extensions')
            for language, attrs in languages_dict.items()
        }

    @property
    def slug(self):
        return text.slugify(self.query)

    def get_absolute_url(self):
        kwargs = {
            "query": self.slug,
            "by": dict(self.SearchCriteria.choices).get(self.by).lower(),
            "page": 1,
        }
        return reverse("search:results", kwargs=kwargs)

    def search_in_readme_and_description(self, keywords: Iterable):
        query = '+'.join(keywords) + '+in:readme+in:description'
        return self.search_repositories(query, sort='stars', order='desc')

    def search_in_topics(self, topics: Iterable):
        query = " ".join([f'topic:{topic}' for topic in topics])
        return self.search_repositories(query)

    def search_users_by_username(self, username):
        query = username + ' in:login'
        return self.search_users(query), GitHubUser

    def search_users_by_location(self, location):
        query = location + ' in:location'
        return self.search_users(query), GitHubUser

    def search_users_by_language(self, language: Union[Language, str]):
        if isinstance(language, Language):
            language = language.name
        elif not isinstance(language, str):
            raise ValueError('language has to be a string or a search.models.Language instance')
        query = 'language:' + language
        return self.search_users(query), GitHubUser

    def search_users_by_profession(self, profession):
        query = list(profession)
        profession = Profession.objects.filter(name__icontains=profession)
        if profession.exists():
            query = profession.first().skills_list
        paginated_lists = [
            self.search_in_readme_and_description(query),
            self.search_in_topics(query)
        ]
        return CombinedPaginatedList(paginated_lists), GitHubRepository

    def search(self, query, by):
        search_fn = getattr(self, f'search_users_by_{by.lower()}')
        return search_fn(query)
