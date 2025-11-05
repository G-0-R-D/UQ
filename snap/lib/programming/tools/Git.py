
import os, subprocess, shlex, json

# https://git-scm.com/docs/user-manual


def call(CMD):
	p = subprocess.Popen(shlex.split(CMD), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=None, shell=False)
	out,err = p.communicate()
	assert p.returncode == 0, 'error: {}'.format(err)
	return out,err

def reorient(self):
	rootpath = self['rootpath']
	os.chdir(rootpath)

def build(ENV):

	SnapNode = ENV.SnapNode

	class GitProject(SnapNode):

		# TODO make some of our own concepts like 'save'(full local commit), and 'share' (push?)
		#	-- pull and keeping current should largely be done quietly internally?

		__slots__ = []

		@ENV.SnapProperty
		class rootpath:

			def get(self, MSG):
				"()->str"
				return self.__snap_data__['rootpath']

			set = None # can't change project, start a new one

		@ENV.SnapChannel
		def status(self, MSG):
			"()->dict(str)"
			reorient(self)

			# TODO get in json and return
			# https://github.com/kellyjonbrazil/jc/blob/master/jc/parsers/git_log.py

		@ENV.SnapChannel
		def log(self, MSG):
			"()->dict(str)"
			# TODO just merge into a general info json with status?

		@ENV.SnapChannel
		def ignore(self, MSG):
			"(list(str))"
			raise NotImplementedError()
			


		@ENV.SnapChannel
		def pull(self, MSG):
			"()"

			reorient(self)

			raise NotImplementedError()

		@ENV.SnapChannel
		def push(self, MSG):
			"()"

			reorient(self)

			# https://www.reddit.com/r/learnprogramming/comments/1mq2ypp/password_authentication_is_not_supported_for_git/
			# https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
			# https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account

			"""
			ssh-keygen -t ed25519 -C "email@example.com"
				-- give it location
				-- give it password

			eval "$(ssh-agent -s)"
			ssh-add ~/.ssh/id_ed25519
			"""
			# https://stackoverflow.com/questions/23546865/how-to-configure-command-line-git-to-use-ssh-key
			"git config core.sshCommand 'ssh -i ~/.ssh/id_rsa'  #specific private key"

			"""
			git config user.signingKey = ~/.ssh/git_user/key.pub
			git config core.sshCommand 'ssh -i ~/.ssh/git_user/key'

			git remote add origin git@github.com:username/repo.git
			git branch -M main
			git push -u origin main
			
			"""

			# https://docs.github.com/en/authentication/managing-commit-signature-verification/telling-git-about-your-signing-key
			"""
			gpg --full-generate-key
			<press enter to accept defaults>
			gpg --list-secret-keys --keyid-format=long
			# copy after slash, above your name: sec: 4096R/3AA5C34371567BD2
			gpg --armor --export 3AA5C34371567BD2
			"""
			# https://docs.github.com/en/authentication/managing-commit-signature-verification/adding-a-gpg-key-to-your-github-account

			# first:
			# git pull origin main

			raise NotImplementedError()

		@ENV.SnapChannel
		def commit(self, MSG):
			"(str message!)"

			message = MSG.kwargs['message']

			reorient(self)

			#call('git commit --all -m "{}"'.format(message))

			raise NotImplementedError()
			
		@ENV.SnapChannel
		def branch(self, MSG):
			"()"

			reorient(self)

			# TODO we should return a new branch object to manage the branch...?

			raise NotImplementedError()

		@ENV.SnapChannel
		def init(self, MSG):
			"(str name!, str email!, str branch_name?)"

			# NOTE: name and email can be None, they just have to be assigned...
			name,email = MSG.kwargs['name'], MSG.kwargs['email']
			branch_name = MSG.kwargs.get('branch_name', 'main')

			reorient(self)

			call('git init')

			#call('git config default.name branch "{}"'.format(default_name))
			call('git branch -m "{}"'.format(branch_name) # after-init version

			call('git config user.name "{}"'.format(name))
			call('git config user.email "{}"'.format(email))

			

		def __init__(self, ROOTPATH, **SETTINGS):
			SnapNode.__init__(self, **SETTINGS)

			assert os.path.isdir(ROOTPATH), 'not a directory: {}'.format(repr(ROOTPATH))
			self.__snap_data__['rootpath'] = ROOTPATH

	ENV.GitProject = GitProject
