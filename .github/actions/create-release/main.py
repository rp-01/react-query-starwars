#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import base64
import os
import re
import sys
import github
import yaml
from tqdm import tqdm
#some

def get_inputs(input_name: str, prefix='INPUT') -> str:
    '''
    Get a Github actions input by name
    Args:
        input_name (str): input_name in workflow file.
        prefix (str, optional): prefix of input variable. Defaults to 'INPUT'.
    Returns:
        str: action_input
    References
    ----------
    [1] https://help.github.com/en/actions/automating-your-workflow-with-github-actions/metadata-syntax-for-github-actions#example
    '''
    return os.getenv(prefix + '_{}'.format(input_name).upper())
    
class GithubChangelog:
    '''
    Class for data interface of Github
    Use it to get changelog data and file content from Github and write new file content to Github
    '''
    def __init__(self, ACCESS_TOKEN, REPO_NAME, PATH, BRANCH, PULL_REQUEST, COMMIT_MESSAGE, COMMITTER):
        '''
        Initial GithubContributors
        Args:
            ACCESS_TOKEN (str): Personal Access Token for Github
            REPO_NAME (str): The name of the repository
            PATH (str): The path to the file
            BRANCH (str): The branch of the file
            PULL_REQUEST (str): Pull request target branch, none means do not open a pull request
            COMMIT_MESSAGE (str): Commit message you want to use
            COMMITTER (str): Committer you want to use to commit the file
        '''
        self.__commit_message = COMMIT_MESSAGE
        self.__path = PATH
        self.__branch = BRANCH
        self.__pull_request = PULL_REQUEST
        self.__sha = ''
        self.__releases = {}
        self.__changelog = ''
        self.__file_exists = False
        # Use PyGithub to login to the repository
        # References: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html#github.Repository.Repository
        g = github.Github(ACCESS_TOKEN)
        self.__repo = g.get_repo(REPO_NAME)
        self.__author = github.GithubObject.NotSet if COMMITTER == '' else github.InputGitAuthor(COMMITTER.split(' ')[0], COMMITTER.split(' ')[1])

    def get_last_tag(self):
        tags = self.__repo.get_tags()
        return tags[0].name

    def get_last_commit_message(self, semver_type):
        # get latest commit
        releases = self.__repo.get_releases()

        self.__releases['Unreleased'] = {'html_url': '', 'body': '', 'created_at': '', 'commit_sha': ''}
        commits = self.__repo.get_commits(sha=self.__branch)
        last_commit = commits[0]
        release_message = last_commit.commit.message
        print(release_message)
        last_commit_message = ''
        if any(semver in release_message for semver in semver_type):
            last_commit_message = release_message.split('\n\n')
            print(f'{last_commit_message}')
        # last_commit_messag = last_commit.commit.message
        return last_commit_message

    def read_releases(self):
        return self.__releases
        
    def create_release(self,tag,message):
        self.__repo.create_git_release(tag, tag, message, draft=False, prerelease=False)

    def get_release_message(self):
        commits = self.__repo.get_commits(sha=self.__branch)
        last_commit = commits[0]
        release_message = last_commit.commit.message
        return release_message
    def get_pull_request(self):
        commits = self.__repo.get_commits(sha=self.__branch)
        for commit in commits:
            pulls = commit.get_pulls()
            for pull in pulls:
                print(f'pull rq: {pull}')
                print(pull.head.repo.tags.url)

def create_tag(tag, commit_message, semver_type, releases):
    
    try:
        tag_name = tag[1:].split('.')
        tag_name = list(map(int, tag_name))
        for commit in commit_message:
            regex, name = commit.split(':')
            if(regex =='feat'): 
                tag_name[1] = tag_name[1] + 1
            elif(regex =='fix'): 
                tag_name[2] = tag_name[2] + 1
            elif(regex =='breaking change'):
                tag_name[0] = tag_name[0] + 1
    
        tag_name = list(map(str, tag_name))
        new_tag = 'v' + ('.').join(tag_name)
        print(new_tag)
        print(commit_message)
        print(semver_type)
    except Exception as e:
        print(e)

    return new_tag

def main():
    ACCESS_TOKEN = get_inputs('ACCESS_TOKEN')
    
    REPO_NAME = get_inputs('REPO_NAME')
    if REPO_NAME == '':
        REPO_NAME = get_inputs('REPOSITORY', 'GITHUB')
    PATH = get_inputs('PATH')

    BRANCH = get_inputs('BRANCH')
    if BRANCH == '':
        BRANCH = github.GithubObject.NotSet
    
    PULL_REQUEST = get_inputs('PULL_REQUEST')
    COMMIT_MESSAGE = get_inputs('COMMIT_MESSAGE')
    COMMITTER = get_inputs('COMMITTER')
    part_name = get_inputs('TYPE')
    part_name = part_name.split(',')
    changelog = GithubChangelog(ACCESS_TOKEN, REPO_NAME, PATH, BRANCH, PULL_REQUEST, COMMIT_MESSAGE, COMMITTER)
    last_tag = changelog.get_last_tag()
    last_commit_message = changelog.get_last_commit_message(part_name)
    if(last_commit_message != ''):
        new_release_tag = create_tag(last_tag, last_commit_message, part_name ,changelog.read_releases())
        if new_release_tag == last_tag:
            print("new release is not requried. Exiting workflow....")
        
        else:
            release_message = changelog.get_release_message()
            changelog.get_pull_request()
            # changelog.create_release(new_release_tag,release_message)
    else:
        print("invalid commit message format")

if __name__ == '__main__':
    main()