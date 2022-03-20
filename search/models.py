from collections.abc import Iterable
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from django.utils import text
from github import Github
from github.PaginatedList import PaginatedList
from typing import Union
import yaml


class GitHubUser(models.Model):
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

    def __str__(self):
        return f'GitHubUser(login={str(self.login)})'

    def get_top_languages(self, size=5):
        repos = self.githubrepository_set.all()
        for repo in repos:
            print(repo.languages)

    class Meta:
        verbose_name = "GitHub User"
        verbose_name_plural = "GitHub Users"


class GitHubRepository(models.Model):
    owner = models.ForeignKey(GitHubUser, on_delete=models.RESTRICT)
    name = models.CharField(max_length=100, null=False, blank=False)
    created_at = models.DateTimeField()
    description = models.TextField()
    forks_count = models.IntegerField()
    languages = ArrayField(base_field=models.CharField(max_length=32))
    license = models.CharField(max_length=48)

    def __str__(self):
        return f'GitHubRepository(owner={str(self.owner)}, name={str(self.name)})'

    class Meta:
        verbose_name = "GitHub Repository"
        verbose_name_plural = "GitHub Repositories"


class Skill(models.Model):
    person = models.ForeignKey(GitHubUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=32, unique=True, null=False, blank=False)


class Language(Skill):
    file_extensions = ArrayField(base_field=models.CharField(max_length=16))


class Profession(models.Model):
    users = models.ManyToManyField(GitHubUser)
    repositories = models.ManyToManyField(GitHubRepository)
    skills = models.ManyToManyField(Skill)
    name = models.CharField(max_length=64)


class Search(models.Model, Github):
    class SearchCriteria(models.TextChoices):
        USERNAME = 'NAME'
        BIO = 'BIO'
        COMPANY = 'COMP'
        EMPLOYABILITY = 'EMPL'
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
        languages_dict = yaml.load(content, Loader=yaml.SafeLoader)
        return languages_dict

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
