from django.contrib.postgres.fields import ArrayField
from django.db import models


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
