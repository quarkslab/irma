/* eslint prefer-arrow-callback: "off" */
// See: https://github.com/cucumber/cucumber-js/blob/master/docs/faq.md
/* eslint func-names: "off" */

const { assert, expect } = require('chai');
const csvParser = require('csv-parse');
const { Given, Then, When } = require('cucumber');
const path = require('path');
const request = require('request');

const ROOT_URL = 'http://localhost';
const wait = ms => new Promise(r => setTimeout(r, ms));
const URIS = {
  main: '/',
  search: '/search',
  previous_searched: '/search?value=eicar&type=name&page=1&offset=25',
};


Given('I am on the {word} page', async function (pageName) {
  // Waiting for networkidle allow XHR to be resolved
  await this.page.goto(ROOT_URL + URIS[pageName], { waitUntil: 'networkidle0' });
});


Then('I take a screenshot named {string}', async function (name) {
  await this.page.screenshot({ path: name });
});

Then('The page title should be {string}', async function (text) {
  expect(await this.page.title()).to.equal(text);
});

Then('I should see a(n) {string} alert', async function (type) {
  const errors = await this.page.$x('/html/body/alerts/div/ul/li');
  expect(errors).to.have.lengthOf(1);

  const className = await (await errors[0].getProperty('className')).jsonValue();
  expect(className).to.equal(`alert-${type}`);
});

// Depending on your needs, the regexp can match `should` or `should not` statements
Then('The file {string} should ({word} )be flagged as a malware', async function (fileName, status) {
  /**
   * Removing the eslint complaint which would require that the return
   * statement should be at the end of the block scope. Having the `return`
   * statement when the filename is found in the result list is more readable.
   */
  // eslint-disable-next-line consistent-return
  const className = await this.page.evaluate(function (selector, name) {
    /**
     * Removing the eslint complaint that `document` is not defined. The
     * `evaluate` function run the code directly in the browser, and `document`
     * is a global variable available there.
     */
    // eslint-disable-next-line no-undef
    const divs = document.querySelectorAll(selector);

    for (let i = 0; i < divs.length; i += 1) {
      if (divs[i].querySelector('a').text === name) {
        return divs[i].querySelector('span').className;
      }
    }
  }, '.infos', fileName);

  expect(className).to.include((status === 'not') ? 'label-success' : 'label-danger');
});

// Depending on your needs, the regexp can match `should` or `should not` statements
Then('I should ({word} )see {string} in the search results', async function (status, fileName) {
  const linkArray = await this.page.$x(`//a[contains(text(), "${fileName}")]`);

  // eslint-disable-next-line no-unused-expressions
  (status === 'not') ? expect(linkArray).to.be.empty : expect(linkArray).to.not.be.empty;
});

// Depending on your needs, the regexp can match `should` or `should not` statements
Then('The button {string} is ({word} )enabled', async function (text, negative) {
  const links = await this.page.$x(`//a[contains(text(), "${text}")]`);
  const buttons = await this.page.$x(`//button[contains(text(), "${text}")]`);
  const submits = await this.page.$x(`//input[@type="submit" and contains(@value, "${text}")]`);
  const clickables = links.concat(buttons, submits);

  // eslint-disable-next-line no-unused-expressions
  expect(clickables).to.be.an('array').to.not.be.empty;
  let enabled = 'false';
  if (negative === 'not') {
    enabled = 'true';
  }

  const disabled = await (await clickables[0].getProperty('disabled')).jsonValue();
  // eslint-disable-next-line no-unused-expressions
  expect(disabled).to.be[enabled];
});

Then('I should be able to download the csv report', async function () {
  /**
   * See: https://github.com/GoogleChrome/puppeteer/issues/299
   *
   * For the moment, Puppeteer isn't capable of downloading a file in headless
   * mode. To check that the CSV generation is working, we first try to click
   * on the `csv` button on the scan page, that will fail if there is a 404
   * error, and then perform a request to the API to retrieve the csv file,
   * and then check its content.
   */

  // Only retrieving the part matching the scan id to be used in the http request.
  const scanId = this.page.url().match(/\/scan\/(.{36})$/)[1];

  request(`${ROOT_URL}/api/v1.1/scans/${scanId}/report`, (err, res, body) => {
    if (err) { throw err; }

    csvParser(body, { delimiter: ';' }, (parseError, output) => {
      if (parseError) { throw parseError; }

      // Length of 3 assert that there is at least the header and two results.
      expect(output).to.have.lengthOf(3);
      // Length of 12 assert that there is the common informations and an AV result.
      expect(output[0]).to.have.lengthOf(12);
    });
  });
});

When('I go back', async function () {
  await this.page.goBack({ waitUntil: 'networkidle0' });
  /** For a strange reason the networkidle0 option is not working properly, the
   * next actions are perform too fast after the back action, and not waiting
   * for the XHR requests to be done.
   * This is a hotfixe, take a look at https://github.com/GoogleChrome/puppeteer/issues/1412
   */
  await wait(500);
});

When('I wait {int} second(s)', async function (number) {
  await wait(number * 1000);
});

When('I select the file named {string}', async function (fileName) {
  assert.notInclude(fileName, '..');

  await (
    await this.page.$x('//input[@id="file-container"]')
  )[0].uploadFile(path.join(process.env.PWD, '/tests/functionals/samples', fileName));
});

When('I click to choose a file', async function () {
  await (
    await this.page.$x('//div[@class="drop-zone"]')
  )[0].click();
});

// Test the progress bar from the upload which has his property
// aria-valuenow coming to 100 when all step from the upload are done
When('I wait for the upload to finish', async function () {
  await this.page.waitFor(() => {
    // eslint-disable-next-line no-undef
    const progress = document.querySelector('div.progress-bar');
    return progress && progress.getAttribute('aria-valuenow') === '100';
  });

  // Adding a waiter because it bugs on the CI
  // May be the action is quicker than the property changes on the DOM element
  await wait(500);
});

When('I wait for the scan to finish', async function () {
  await this.page.waitForXPath('//span[text()="Finished"]');
});

When('I type {string} in the search input', async function (search) {
  /**
   * TODO: There is the presence of two `#search` id on the page_ One
   * should be rename or replace with a more specific id.
   */
  await this.page.type('input#search', search);
});

When('I click on {string}', async function (text) {
  const links = await this.page.$x(`//a[contains(text(), "${text}")]`);
  const buttons = await this.page.$x(`//button[contains(text(), "${text}")]`);
  const submits = await this.page.$x(`//input[@type="submit" and contains(@value, "${text}")]`);

  const clickables = links.concat(buttons, submits);

  if (clickables[0] != null) {
    /** For a strange reason the networkidle0 option for the waitForNavigation
     * function is not working properly, the next actions are perform too fast
     * after the back action, and not waiting for the XHR requests to be done.
     * Using the `wait` function is a hotfixe, take a look at
     * https://github.com/GoogleChrome/puppeteer/issues/1412
     */
    // const navigationPromise = this.page.waitForNavigation({ waitUntil: 'networkidle0' });
    await clickables[0].click();
    // await navigationPromise;
    await wait(500);
  } else {
    throw Error(`Link "${text}" not found on the page`);
  }
});
