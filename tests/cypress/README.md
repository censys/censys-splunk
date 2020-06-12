

# Set up

Install the Cypress test software, see the instructions at
<https://docs.cypress.io/guides/getting-started/installing-cypress.html>

Install the Docker image for Splunk and the Censys plug-in:

1.  Get the Docker image: <https://hub.docker.com/r/splunk/splunk/>
2.  Start Splunk

        docker run -d -p 8000:8000 -e "SPLUNK_START_ARGS=--accept-license" -e "SPLUNK_PASSWORD=PaSSWorD_FoR_SpLuNk" --name splunk splunk/splunk:latest
3.  Go to <http://localhost:8000> and log in as `admin` using the
    password specified on the `docker run` command line
4.  Go to <https://app.censys.io/docs/splunk-integration/> and
    follow the instructions.

Set the environment variable `CYPRESS_SPLUNK_PASSWORD` to what you
set the password to on the `docker run` line.  Note that this
password will be printed to the Cypress console when the tests run,
so don't use a secret password (this should only ever be running on
your laptop and not exposed to any networks, so this shouldn't be a
security risk, but be aware).


# Running the tests

Go into the directory with the `cypress.json` file in it and type:

    npx cypress run

If you want to watch the tests run, type:

    npx cypress run --headed

or

    npx cypress run --browser chrome


# Notes

-   The tests are in `e2e/censys_app_spec.js`

-   The tests are all in one test block so the test user can stay
    logged in; if you make a new test block, you will need to log in
    again

-   Splunk isn't well structured for automated testing, so there is
    some fragility in the tests because they rely on DOM elements that
    could change; if a test fails because an element can't be found,
    you'll have to update it to match what the current version of
    Splunk shows


# Things to do

The initial commit of this is a simple skeleton with lots of room
for improvement.

Some specific areas of improvement are:

-   [ ] the login code could be pulled out into a utility library

-   [ ] the tests could include the installation process and start
    from an unmodified Splunk Docker container

-   [ ] the tests could populate Splunk with known data then confirm
    that the reports are correct

-   [ ] the tests could start the Docker container so that the set-up
    was automated
