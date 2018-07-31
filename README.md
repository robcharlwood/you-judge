# YouJudge

[![Build Status](https://travis-ci.com/robcharlwood/you-judge.svg?branch=master)](https://travis-ci.com/robcharlwood/you-judge.svg?branch=master) [![Coverage Status](https://coveralls.io/repos/github/robcharlwood/you-judge/badge.svg?branch=master)](https://coveralls.io/github/robcharlwood/you-judge?branch=master)

## This project is intended for educational purposes only.

An experimental app using Google's Natural Language processing to process user sentiment analysis on YouTube content and comments.

## Getting Started

These instructions will get you a copy of the project up and running on your
local machine for development and testing purposes.

* Clone the repository ``git clone git@github.com:robcharlwood/you-judge.git``
* Create a virtualenv ``mkvirtualenv you-judge``
* Run ``./install_deps`` to install Python requirements.

I recommend adding the below to your virtualenv's ``postactivate``
script so that you can always ensure you are working on the correct path when you activate your env.

In your choice of editor open the below file - example uses nano:
``nano /Users/foo/.virtualenvs/virtualenvname/bin/postactivate``

Now ensure that you add the below

```
cd /path/to/where/code/lives/
```

Once you activate your environment, this code will move you to the project's code directory.

## Running the project locally
* To serve the backend, run ``./serve``.

## Running test suite

You can run the test suite using the below command.

``./run_tests``

You can also run individual test classes or tests using the spec syntax.

* ``./run_tests appname.tests.test_module``
* ``./run_tests appname.tests.test_module:TestCaseClass``
* ``./run_tests appname.tests.test_module:TestCaseClass.test_method``

## Suggested Deployment Process

To deploy the code to appengine follow the below steps

* Merge ``master`` in to your feature branch ``git merge --no-ff master``
* Resolve any merge conflicts
* Run tests ``./run_tests``
* If all tests are passing, then checkout ``master`` and merge in your feature branch ``git checkout master && git merge --no-ff feature-branch-name``
* Update version in ``app.yaml``
* Update docs, release notes and ``README.md``
* Commit your changes locally.
* Add a git tag for the new version e.g: ``git tag -a 0-0-1 -m"0-0-1 Initial MVP release"``
* Push changes to master branch - ``git push origin master``
* Run ``./deploy`` and follow the prompts

## Versioning

This project uses [git](https://git-scm.com/) for versioning. For the available versions,
see the [tags on this repository](https://github.com/robcharlwood/you-judge/tags).

## Code style

This project adheres to pep8 standards and we use isort to handle the sorting of imports.
The Python code is all unit tested as a bare minimum with integration and end to end tests
added for particularly complex parts of functionality.

## Authors

* **Rob Charlwood**

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details
