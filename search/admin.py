from django.contrib import admin
from .models import GitHubUser, GitHubRepository, Profession, Skill, Language


@admin.register(GitHubUser)
class GitHubUserAdmin(admin.ModelAdmin):
    list_display = ['login', 'name']
    search_fields = ['login', 'name', 'location', 'hireable', 'company']


@admin.register(GitHubRepository)
class GitHubRepositoryAdmin(admin.ModelAdmin):
    list_display = ['owner', 'name', 'languages']
    search_fields = ['owner', 'name', 'languages', 'created_at', 'description']


@admin.register(Profession)
class ProfessionAdmin(admin.ModelAdmin):
    list_display = ['person', 'name']
    search_fields = ['person', 'name']


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['person', 'name']
    search_fields = ['person', 'name', 'professions']


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['person', 'name']
    search_fields = ['person', 'name', 'professions', 'file_extensions']
